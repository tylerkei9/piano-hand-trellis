"""
Generic Viterbi-trellis tracer for the piano hand-position optimizer.

For every song CSV in outputs/*_timed_steps.csv, replicates the REAL
pipeline (find_optimal_split_point -> assign_hands_to_notes -> Viterbi per
hand) plus an "RH-only hardware failure" scenario (all notes forced onto
the right hand, no boundary), and dumps the full trellis (every candidate
state, every transition considered, the kept/backpointer edge, and the
backtracked optimal path) as JSON for the dashboard.
"""
import sys
import os
import json
import io
import csv
import contextlib

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
import findOptimalHandPos as fh

OUTPUTS_DIR = os.path.join(REPO_ROOT, "outputs")
DASHBOARD_DIR = os.path.join(REPO_ROOT, "dashboard")

ORIGINAL_SONGS = [
    ("hotcrossbuns", "Hot Cross Buns"),
    ("hbd", "Happy Birthday"),
    ("twinkletwinkle", "Twinkle Twinkle Little Star"),
    ("maryhadlamb", "Mary Had a Little Lamb"),
    ("starspanbanner", "Star-Spangled Banner"),
    ("fuyunohanashi1", "Fuyu no Hanashi"),
]


def load_manifest_labels():
    labels = {}
    manifest_path = os.path.join(OUTPUTS_DIR, "_new_songs_manifest.csv")
    with open(manifest_path) as f:
        for row in csv.DictReader(f):
            labels[row["song_id"]] = row["label"]
    return labels


def trace_hand(note_groups, hand, max_boundary=None, min_boundary=None):
    """Instrumented re-implementation of optimize_with_boundaries() that
    records the full trellis instead of only the final path."""
    valid_groups = [(i, g) for i, g in enumerate(note_groups) if g is not None]
    if not valid_groups:
        return None

    n = len(valid_groups)
    dp = [{} for _ in range(n)]
    backpointer = [{} for _ in range(n)]
    trace_steps = []

    first_real_idx = valid_groups[0][0]
    first_states = fh.get_possible_states_extended(note_groups, first_real_idx, max_boundary, min_boundary, hand)
    if not first_states:
        first_states = fh.get_possible_states_extended(note_groups, first_real_idx, None, None, hand)
    if not first_states:
        return None

    g0 = note_groups[first_real_idx]
    step0 = {
        "index": 0, "time": g0["time"], "keys": g0["keys"], "notes": g0["notes"],
        "is_black": g0.get("is_black", [False] * len(g0["notes"])),
        "durations": g0.get("durations", [0.5] * len(g0["notes"])),
        "states": [],
    }
    for state, penalty, _ in first_states:
        dp[0][state] = penalty
        step0["states"].append({"pos": state, "cost": round(penalty, 2),
                                 "fingering_penalty": round(penalty, 2),
                                 "incoming": [], "kept_from": None})
    trace_steps.append(step0)

    failed_at = None
    for i in range(1, n):
        curr_real_idx = valid_groups[i][0]
        prev_real_idx = valid_groups[i - 1][0]

        possible_states = fh.get_possible_states_extended(note_groups, curr_real_idx, max_boundary, min_boundary, hand)
        used_fallback_boundary = False
        if not possible_states:
            possible_states = fh.get_possible_states_extended(note_groups, curr_real_idx, None, None, hand)
            used_fallback_boundary = True
        if not possible_states:
            failed_at = curr_real_idx
            break

        time_delta = note_groups[curr_real_idx]["time"] - note_groups[prev_real_idx]["time"]
        gi = note_groups[curr_real_idx]
        step = {"index": i, "time": gi["time"], "keys": gi["keys"], "notes": gi["notes"],
                "is_black": gi.get("is_black", [False] * len(gi["notes"])),
                "durations": gi.get("durations", [0.5] * len(gi["notes"])), "states": []}

        for curr_state, fingering_penalty, _ in possible_states:
            min_cost = float("inf")
            best_prev = None
            incoming = []
            for prev_state, prev_cost in dp[i - 1].items():
                distance = abs(curr_state - prev_state)
                move_penalty = fh.MOVE_PENALTY if distance > 0 else 0
                velocity_penalty = 0.0
                if distance > 0 and time_delta > 0:
                    required_velocity = distance / time_delta
                    if required_velocity > fh.MAX_KEYS_PER_SECOND:
                        velocity_penalty = fh.VELOCITY_PENALTY * (required_velocity - fh.MAX_KEYS_PER_SECOND)
                boundary_penalty = 0
                if not used_fallback_boundary:
                    if max_boundary and curr_state > max_boundary:
                        boundary_penalty += 1000
                    if min_boundary and curr_state < min_boundary:
                        boundary_penalty += 1000
                transition_cost = distance + move_penalty + velocity_penalty + fingering_penalty + boundary_penalty
                cost = prev_cost + transition_cost
                incoming.append({
                    "from": prev_state, "prev_cost": round(prev_cost, 2), "distance": distance,
                    "move_penalty": move_penalty, "velocity_penalty": round(velocity_penalty, 2),
                    "fingering_penalty": round(fingering_penalty, 2),
                    "boundary_penalty": boundary_penalty,
                    "transition_cost": round(transition_cost, 2), "total_cost": round(cost, 2),
                })
                if cost < min_cost:
                    min_cost = cost
                    best_prev = prev_state

            if best_prev is not None:
                dp[i][curr_state] = min_cost
                backpointer[i][curr_state] = best_prev

            step["states"].append({
                "pos": curr_state,
                "cost": round(min_cost, 2) if best_prev is not None else None,
                "fingering_penalty": round(fingering_penalty, 2),
                "incoming": incoming, "kept_from": best_prev,
            })
        trace_steps.append(step)

    if not dp[len(trace_steps) - 1]:
        return {"ok": False, "failed_at_time": note_groups[failed_at]["time"] if failed_at is not None else None,
                "steps": trace_steps}

    last_i = len(trace_steps) - 1
    final_state = min(dp[last_i], key=dp[last_i].get)
    path_segment = [final_state]
    for i in range(last_i, 0, -1):
        prev_state = backpointer[i][path_segment[0]]
        path_segment.insert(0, prev_state)

    full_path = [None] * len(note_groups)
    for k in range(len(path_segment)):
        real_idx = valid_groups[k][0]
        full_path[real_idx] = path_segment[k]

    return {
        "ok": True,
        "hand": hand,
        "max_boundary": max_boundary,
        "min_boundary": min_boundary,
        "steps": trace_steps,
        "final_path": full_path,
        "final_cost": round(dp[last_i][final_state], 2),
        "incomplete": failed_at is not None,
        "failed_at_time": note_groups[failed_at]["time"] if failed_at is not None else None,
    }


def build_song(song):
    csv_path = os.path.join(OUTPUTS_DIR, f"{song}_timed_steps.csv")
    note_groups = fh.load_notes_grouped_by_time(csv_path)
    if not note_groups:
        print(f"  !! no data for {song}", file=sys.stderr)
        return None

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        split = fh.find_optimal_split_point(note_groups)
        l_groups, r_groups, _ = fh.assign_hands_to_notes(note_groups, split) if split is not None else ([None]*len(note_groups), note_groups, [])

    widest_span, widest_time, widest_keys = 0, None, []
    for g in note_groups:
        if g and len(g["notes"]) > 1:
            span = max(g["notes"]) - min(g["notes"])
            if span > widest_span:
                widest_span, widest_time, widest_keys = span, g["time"], g["keys"]

    max_b = split
    min_b = (split + fh.MIN_HAND_GAP) if split is not None else None

    trace_left = trace_hand(l_groups, "left", max_boundary=max_b, min_boundary=None)
    trace_right = trace_hand(r_groups, "right", max_boundary=None, min_boundary=min_b)
    trace_failure = trace_hand(note_groups, "right", max_boundary=None, min_boundary=None)

    result = {
        "song": song,
        "split_point": split,
        "split_note_name": fh.index_to_note_name(split) if split is not None else None,
        "n_time_steps": len([g for g in note_groups if g]),
        "widest_simultaneous_span": widest_span,
        "widest_simultaneous_time": widest_time,
        "widest_simultaneous_keys": widest_keys,
        "scenarios": {
            "two_hand": {
                "label": "Two-hand (normal)",
                "left": trace_left,
                "right": trace_right,
            },
            "rh_failure": {
                "label": "Right-hand-only (left hand disabled)",
                "left": None,
                "right": trace_failure,
            },
        },
    }
    return result


def main():
    manifest_labels = load_manifest_labels()
    all_song_ids = [s for s, _ in ORIGINAL_SONGS] + list(manifest_labels.keys())
    song_labels = dict(ORIGINAL_SONGS)
    song_labels.update(manifest_labels)

    out = {
        "_constants": {
            "MOVE_PENALTY": fh.MOVE_PENALTY,
            "MAX_KEYS_PER_SECOND": fh.MAX_KEYS_PER_SECOND,
            "VELOCITY_PENALTY": fh.VELOCITY_PENALTY,
            "MIN_HAND_GAP": fh.MIN_HAND_GAP,
            "INNER_FINGER_BLACK_KEY_PENALTY": fh.INNER_FINGER_BLACK_KEY_PENALTY,
            "OUTER_FINGER_BLACK_KEY_PENALTY": fh.OUTER_FINGER_BLACK_KEY_PENALTY,
            "OUTER_FINGER_SPLAY_PENALTY": fh.OUTER_FINGER_SPLAY_PENALTY,
            "MAX_OUTER_SPLAY": fh.MAX_OUTER_SPLAY,
            "LOOKAHEAD_STEPS": fh.LOOKAHEAD_STEPS,
        }
    }
    song_manifest = []
    failed = []
    for song in all_song_ids:
        print(f"Tracing {song}...", file=sys.stderr)
        try:
            data = build_song(song)
        except Exception as e:
            print(f"  !! FAILED: {song}: {e}", file=sys.stderr)
            failed.append(song)
            continue
        if data:
            out[song] = data
            song_manifest.append({"key": song, "label": song_labels[song]})
            for scen_key, scen in data["scenarios"].items():
                for hand_key in ("left", "right"):
                    t = scen[hand_key]
                    if t is None:
                        continue
                    ok = t.get("ok")
                    cost = t.get("final_cost")
                    print(f"    {scen_key}/{hand_key}: ok={ok} cost={cost} steps={len(t.get('steps', []))}", file=sys.stderr)
        else:
            failed.append(song)

    out["_song_labels"] = {row["key"]: row["label"] for row in song_manifest}

    write_data_chunks(out)

    print(f"Songs included: {len(song_manifest)}", file=sys.stderr)
    if failed:
        print(f"Songs FAILED to trace: {failed}", file=sys.stderr)

    manifest_path = os.path.join(DASHBOARD_DIR, "songs_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(song_manifest, f, indent=2)
    print(f"Wrote {manifest_path}", file=sys.stderr)


# The trellis trace data grows well past the ~16MB single-file limit some
# static hosts (including the Claude Artifact preview used during
# development) impose, once enough songs are included. Rather than have
# two different code paths for "small dataset, one file" vs "large
# dataset, split it," the dashboard always fetches a manifest of chunk
# files and merges them -- so this works unchanged whether there's 6
# songs or 600. TARGET_CHUNK_BYTES is deliberately well under any 16MB
# cap to leave headroom.
TARGET_CHUNK_BYTES = 8 * 1024 * 1024


def write_data_chunks(out):
    # Remove a stale single-file data.json from older runs of this script,
    # so nothing accidentally keeps fetching outdated data.
    stale = os.path.join(DASHBOARD_DIR, "data.json")
    if os.path.exists(stale):
        os.remove(stale)

    items = [(k, v, len(json.dumps(v))) for k, v in out.items()]
    total_bytes = sum(size for _, _, size in items)
    n_chunks = max(1, -(-total_bytes // TARGET_CHUNK_BYTES))  # ceil division

    items.sort(key=lambda x: -x[2])
    chunks = [dict() for _ in range(n_chunks)]
    chunk_sizes = [0] * n_chunks
    for key, value, size in items:
        idx = min(range(n_chunks), key=lambda i: chunk_sizes[i])
        chunks[idx][key] = value
        chunk_sizes[idx] += size

    chunk_names = []
    for i, chunk in enumerate(chunks):
        name = f"data-part{i + 1}.json"
        with open(os.path.join(DASHBOARD_DIR, name), "w") as f:
            json.dump(chunk, f)
        size_mb = os.path.getsize(os.path.join(DASHBOARD_DIR, name)) / 1e6
        print(f"Wrote dashboard/{name} ({size_mb:.2f} MB, {len(chunk)} entries)", file=sys.stderr)
        chunk_names.append(name)

    manifest_path = os.path.join(DASHBOARD_DIR, "data-manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(chunk_names, f)
    print(f"Wrote dashboard/data-manifest.json ({len(chunk_names)} chunks, {total_bytes / 1e6:.2f} MB total)", file=sys.stderr)


if __name__ == "__main__":
    main()
