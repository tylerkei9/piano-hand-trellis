"""
Defines new demo pieces for the Hand-Position Trellis dashboard and writes
them out as outputs/<song>_timed_steps.csv in the same format as the
existing example songs (start_time,midi,duration,white_key_index,is_black),
using the real midi_to_key_position() from findOptimalHandPos.py so the
key-position math matches the actual algorithm.

Two kinds of pieces:
  - NAMED: seven short, hand-transcribed excerpts of well-known public-domain
    melodies, each chosen to exercise a specific part of the optimizer
    (black-key fingering, wide leaps, speed limits, hand-boundary stress,
    repeated-note efficiency).
  - PROCEDURAL: a much larger set of music-theory-generated etudes (scale
    runs, arpeggios, broken-chord figures, leap studies, black-key trills),
    computed directly from interval math rather than transcribed from
    memory, across all 12 keys, so the set is both large and reliably
    correct. Each still targets one algorithm mechanic on purpose.

Each entry in a song is (midi_number, duration_in_seconds) played back to
back, or ("gap", seconds) to advance time without adding a note (a rest).
"""
import csv
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
import findOptimalHandPos as fh

OUTPUTS_DIR = os.path.join(REPO_ROOT, "outputs")

KEY_NAMES = ["c", "csharp", "d", "dsharp", "e", "f", "fsharp", "g", "gsharp", "a", "asharp", "b"]
KEY_LABELS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJOR_STEPS = [2, 2, 1, 2, 2, 2, 1]

# ---------------------------------------------------------------------------
# NAMED: hand-transcribed excerpts, each targeting one mechanic.
# ---------------------------------------------------------------------------
NAMED_SONGS = {
    "odetojoy": {
        "label": "Ode to Joy",
        "notes": [
            (64, 0.5), (64, 0.5), (65, 0.5), (67, 0.5),
            (67, 0.5), (65, 0.5), (64, 0.5), (62, 0.5),
            (60, 0.5), (60, 0.5), (62, 0.5), (64, 0.5),
            (64, 0.75), (62, 0.25), (62, 1.0),
            (64, 0.5), (64, 0.5), (65, 0.5), (67, 0.5),
            (67, 0.5), (65, 0.5), (64, 0.5), (62, 0.5),
            (60, 0.5), (60, 0.5), (62, 0.5), (64, 0.5),
            (62, 0.75), (60, 0.25), (60, 1.0),
        ],
    },
    "furelise": {
        "label": "Fur Elise (opening)",
        "notes": [
            (76, 0.2), (75, 0.2), (76, 0.2), (75, 0.2), (76, 0.2),
            (71, 0.3), (74, 0.3), (72, 0.3), (69, 0.3),
            ("gap", 0.3),
            (60, 0.3), (64, 0.3), (69, 0.3), (71, 0.3),
            ("gap", 0.3),
            (64, 0.3), (68, 0.3), (71, 0.3), (72, 0.3),
            ("gap", 0.3),
            (64, 0.5),
        ],
    },
    "rowrowboat": {
        "label": "Row, Row, Row Your Boat",
        "notes": [
            (60, 0.4), (60, 0.4), (60, 0.4), (62, 0.4), (64, 0.4),
            (64, 0.4), (62, 0.4), (64, 0.4), (65, 0.4), (67, 0.4),
            (72, 0.25), (72, 0.25), (72, 0.25),
            (67, 0.25), (67, 0.25), (67, 0.25),
            (64, 0.25), (64, 0.25), (64, 0.25),
            (60, 0.25), (60, 0.25), (60, 0.25),
            (67, 0.4), (65, 0.4), (64, 0.4), (62, 0.4), (60, 0.6),
        ],
    },
    "scalerun": {
        "label": "C Major Scale Run",
        "notes": [
            (60, 0.08), (62, 0.08), (64, 0.08), (65, 0.08),
            (67, 0.08), (69, 0.08), (71, 0.08), (72, 0.08),
            (72, 0.08), (71, 0.08), (69, 0.08), (67, 0.08),
            (65, 0.08), (64, 0.08), (62, 0.08), (60, 0.3),
        ],
    },
    "jinglebells": {
        "label": "Jingle Bells",
        "notes": [
            (64, 0.3), (64, 0.3), (64, 0.4),
            (64, 0.3), (64, 0.3), (64, 0.4),
            (64, 0.3), (67, 0.3), (60, 0.3), (62, 0.3), (64, 0.6),
            ("gap", 0.2),
            (65, 0.3), (65, 0.3), (65, 0.3), (65, 0.3), (65, 0.3),
            (64, 0.3), (64, 0.3), (64, 0.2), (64, 0.2),
            (62, 0.3), (62, 0.3), (64, 0.3), (62, 0.5), (67, 0.7),
        ],
    },
    "leapstresstest": {
        "label": "Octave Leap Stress Test",
        "notes": [
            (36, 0.5), (84, 0.5), (38, 0.5), (86, 0.5), (40, 0.5),
            (88, 0.5), (41, 0.5), (89, 0.5), (43, 0.5), (91, 0.5),
            (60, 0.5), (64, 0.5), (67, 0.5), (72, 0.8),
        ],
    },
    "frerejacques": {
        "label": "Frere Jacques",
        "notes": [
            (60, 0.4), (62, 0.4), (64, 0.4), (60, 0.4),
            (60, 0.4), (62, 0.4), (64, 0.4), (60, 0.4),
            (64, 0.4), (65, 0.4), (67, 0.7),
            (64, 0.4), (65, 0.4), (67, 0.7),
            (67, 0.3), (69, 0.3), (67, 0.3), (65, 0.3), (64, 0.4), (60, 0.5),
            (67, 0.3), (69, 0.3), (67, 0.3), (65, 0.3), (64, 0.4), (60, 0.5),
            (60, 0.4), (55, 0.4), (60, 0.7),
            (60, 0.4), (55, 0.4), (60, 0.7),
        ],
    },
}


def major_scale(tonic_midi, octaves=1):
    notes = [tonic_midi]
    m = tonic_midi
    steps = (MAJOR_STEPS * octaves)[: 7 * octaves]
    for s in steps:
        m += s
        notes.append(m)
    return notes


def build_procedural_songs():
    songs = {}

    # Scale runs: fast (0.09s/note) ascending + descending, one per key.
    # Targets: velocity/speed-limit penalty, consistently, in every key.
    for pc, (kid, klabel) in enumerate(zip(KEY_NAMES, KEY_LABELS)):
        tonic = 60 + pc
        up = major_scale(tonic)
        down = list(reversed(up[:-1]))
        notes = [(n, 0.09) for n in up] + [(n, 0.09) for n in down[:-1]] + [(down[-1], 0.3)]
        songs[f"scale_run_{kid}"] = {"label": f"Scale Run in {klabel}", "notes": notes}

    # Arpeggios: root-3rd-5th-octave broken chord, moderate tempo, one per key.
    # Targets: hand-position jumps that stay musically "shaped" rather than random.
    for pc, (kid, klabel) in enumerate(zip(KEY_NAMES, KEY_LABELS)):
        tonic = 60 + pc
        third = tonic + 4
        fifth = tonic + 7
        octave = tonic + 12
        up = [tonic, third, fifth, octave]
        down = list(reversed(up))
        notes = [(n, 0.25) for n in up] + [(n, 0.25) for n in down]
        songs[f"arpeggio_{kid}"] = {"label": f"Arpeggio in {klabel}", "notes": notes}

    # Broken-chord "waltz" figure: root-fifth-third repeating, one per key.
    # Targets: a different repeating-jump shape than the arpeggio (fifth
    # then a smaller drop to the third) to vary the move-penalty pattern.
    for pc, (kid, klabel) in enumerate(zip(KEY_NAMES, KEY_LABELS)):
        tonic = 60 + pc
        third = tonic + 4
        fifth = tonic + 7
        pattern = [tonic, fifth, third] * 4
        notes = [(n, 0.3) for n in pattern]
        songs[f"waltz_figure_{kid}"] = {"label": f"Broken Chord in {klabel}", "notes": notes}

    # Leap studies: alternate a fixed low anchor with a note leaping upward
    # by an increasing interval. Targets: the move penalty and velocity
    # penalty scaling directly with leap distance.
    leap_intervals = [("minor3rd", 3), ("perfect5th", 7), ("octave", 12), ("octave_plus_4th", 17), ("two_octaves", 24)]
    for name, interval in leap_intervals:
        anchor = 60
        notes = []
        for i in range(5):
            notes.append((anchor, 0.4))
            notes.append((anchor + interval, 0.4))
        songs[f"leap_study_{name}"] = {"label": f"Leap Study ({name.replace('_', ' ')})", "notes": notes}

    # Black-key trills: fast alternation between a black key and its upper
    # white-key neighbor, one per black key. Targets: black-key fingering
    # penalty combined with speed, in every register position a black key
    # can occupy.
    black_key_pcs = [1, 3, 6, 8, 10]  # C#, D#, F#, G#, A# relative to C
    black_key_names = ["csharp", "dsharp", "fsharp", "gsharp", "asharp"]
    black_key_labels = ["C#", "D#", "F#", "G#", "A#"]
    for pc, kid, klabel in zip(black_key_pcs, black_key_names, black_key_labels):
        black = 60 + pc
        upper_white = black + 1
        pattern = [black, upper_white] * 6
        notes = [(n, 0.15) for n in pattern]
        songs[f"trill_{kid}"] = {"label": f"Black Key Trill ({klabel})", "notes": notes}

    # Repeated-note endurance studies: same note held/repeated at two
    # tempos. Targets: showing the optimizer keep the hand still (zero
    # move cost) across many repeats, at both a fast and a moderate pace.
    songs["repeated_notes_fast"] = {
        "label": "Repeated Notes (fast)",
        "notes": [(67, 0.1)] * 20,
    }
    songs["repeated_notes_moderate"] = {
        "label": "Repeated Notes (moderate)",
        "notes": [(67, 0.25)] * 20,
    }

    return songs


def build_timed_steps(notes):
    rows = []
    t = 0.0
    for entry in notes:
        pitch, duration = entry
        if pitch == "gap":
            t += duration
            continue
        white_key_index, is_black, _ = fh.midi_to_key_position(pitch)
        rows.append((round(t, 4), pitch, duration, white_key_index, int(is_black)))
        t += duration
    return rows


def main():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    all_songs = {}
    all_songs.update(NAMED_SONGS)
    all_songs.update(build_procedural_songs())

    manifest = []
    for song_id, song in all_songs.items():
        rows = build_timed_steps(song["notes"])
        out_path = os.path.join(OUTPUTS_DIR, f"{song_id}_timed_steps.csv")
        with open(out_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["start_time", "midi", "duration", "white_key_index", "is_black"])
            writer.writerows(rows)
        manifest.append((song_id, song["label"], len(rows)))
        print(f"{song_id}: {len(rows)} notes -> {out_path}")

    print(f"\nTotal new songs: {len(manifest)}")

    manifest_path = os.path.join(OUTPUTS_DIR, "_new_songs_manifest.csv")
    with open(manifest_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["song_id", "label", "note_count"])
        writer.writerows(manifest)
    print(f"Manifest -> {manifest_path}")


if __name__ == "__main__":
    main()
