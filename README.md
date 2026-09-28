# Piano Hand Algorithms

A dynamic-programming (Viterbi) optimizer that decides how a robotic hand
should move across a piano keyboard to play a song, balancing reach, speed,
and fingering comfort against a set of hardware constraints. The `dashboard/`
folder visualizes the optimizer's decision-making, step by step, for a large
catalog of example pieces.

## Structure

- `findOptimalHandPos.py` — the optimizer itself: parses a MusicXML score
  (via [music21](https://www.music21.org/)), assigns notes to left/right
  hand, and runs a Viterbi search per hand to find the lowest-cost sequence
  of hand positions.
- `inputs/` — MusicXML source files for the original six example songs.
- `outputs/` — `<song>_timed_steps.csv` files (start_time, midi, duration,
  white_key_index, is_black) for every example song; this is the optimizer's
  input format and the thing `scripts/build_dashboard_data.py` reads.
- `scripts/generate_new_songs.py` — defines and writes the CSVs for the
  additional demo songs (see `dashboard/songs_manifest.json` for the full
  list and what each one is meant to demonstrate).
- `scripts/build_dashboard_data.py` — runs the real optimizer pipeline
  (split point, hand assignment, Viterbi trace) over every song in
  `outputs/` and writes `dashboard/data.json`, the trace data the dashboard
  reads.
- `dashboard/` — the interactive visualization. See `dashboard/README.md`.

## Regenerating the dashboard data

```
pip install music21   # only needed if you also regenerate the original 6 from MusicXML
python3 scripts/generate_new_songs.py     # (re)writes outputs/<new-song>_timed_steps.csv
python3 scripts/build_dashboard_data.py   # traces every song -> dashboard/data.json
```

Both scripts locate the repo root relative to their own file location, so
they work from a fresh clone with no path editing.

## Viewing the dashboard

`dashboard/index.html` fetches `data.json`, so it must be served over HTTP,
not opened directly as a `file://` URL:

```
cd dashboard
python3 -m http.server 8000
```

Then open `http://localhost:8000/`.
