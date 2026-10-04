# Developer guide

Technical setup and workflows. For what the project does, see the
[README](../README.md); for how the optimizer decides, in plain language, see
[ALGORITHM.md](../ALGORITHM.md). The implementation's own overview is the
module docstring at the top of `findOptimalHandPos.py`, with pointers to the
relevant functions.

## Setup

Python 3.9+ and [music21](https://www.music21.org/) (used to parse MusicXML):

```
python3 -m pip install -r requirements.txt
```

The dashboard itself has no dependencies or build step.

## Repository layout

| Path | Purpose |
| --- | --- |
| `findOptimalHandPos.py` | The optimizer. Parses a MusicXML score, chooses the left/right split point, runs a Viterbi search per hand over candidate thumb positions, assigns fingers, and writes the plan and servo commands. |
| `run_all.py` | Runs the optimizer on every MusicXML file in `inputs/`, writing to `outputs/` with the song name as a filename prefix. |
| `run_all_rh_only.py` | Same, with every note forced onto the right hand (simulated left-hand failure), writing to `output_rh_only/`. |
| `verify_fingering.py` | Independent checker for the optimizer's output: correct notes at correct times, no finger collisions, held notes keep their finger, speed and hand-gap limits, reachability, command format. |
| `inputs/` | MusicXML scores for the six original songs. |
| `outputs/` | `<song>_timed_steps.csv` for all 61 songs (`start_time, midi, duration, white_key_index, is_black`), the input format for the dashboard build. `_new_songs_manifest.csv` lists the 55 generated demo songs. |
| `output_rh_only/` | Right-hand-only results (fingering plans, summaries, servo commands) for the six original songs. |
| `scripts/generate_new_songs.py` | Defines and writes the CSVs for the 55 demo songs (scales, arpeggios, trills, leap studies, repeated notes), each designed to exercise one part of the cost function. |
| `scripts/build_dashboard_data.py` | Runs the real pipeline over every listed song (`ORIGINAL_SONGS` plus the demo-song manifest), in both two-hand and right-hand-only modes, and writes the full trellis trace (every candidate, every transition considered, the kept back-pointer, the final path) for the dashboard. |
| `dashboard/` | The interactive visualization. See [`dashboard/README.md`](../dashboard/README.md). |

## Running the optimizer

On one score (looks in `inputs/` by default):

```
python3 findOptimalHandPos.py hbd.musicxml --prefix hbd
```

On every score:

```
python3 run_all.py            # two-hand, writes to outputs/
python3 run_all_rh_only.py    # right-hand-only, writes to output_rh_only/
```

Both batch runners forward extra options to the optimizer, e.g.
`python3 run_all.py --speed 15 --gap 8`.

Per song, the optimizer writes `<song>_timed_steps.csv`,
`<song>_fingering_plan.csv`, `<song>_fingering_summary.csv` and
`<song>_left_hand_commands.txt` / `<song>_right_hand_commands.txt`. Only the
`_timed_steps.csv` files are kept in `outputs/`; the rest are regenerated on
demand.

**Expected failure:** in two-hand mode, `fuyunohanashi1.musicxml` stops with
"Could not find any valid split point". Its opening chord spans 13 white keys
and the hand can reach at most 9 even with splay, so no hand position can play
it. This is the "impossible reach" case described in `ALGORITHM.md`, reported
on purpose rather than guessed around. The dashboard data for that song comes
from its `timed_steps.csv`, so it isn't affected.

### Options

| Option | Default | Meaning |
| --- | --- | --- |
| `--speed` | 10 | Max hand speed, in keys per second |
| `--penalty` | 4 | Flat cost for any hand movement |
| `--gap` | 6 | Minimum keys between the two hands |
| `--splay-penalty` | 50 | Cost of stretching the thumb or pinky past the natural span |
| `--max-splay` | 2 | How many keys the thumb or pinky can stretch |
| `--black-inner-penalty` | 2 | Cost of a middle finger on a black key |
| `--black-outer-penalty` | 10 | Cost of the thumb or pinky on a black key |
| `--lookahead` | 3 | Future steps checked for dead ends (0 disables) |
| `--lookahead-penalty` | 50 | Cost of a position that limits upcoming moves |
| `--dynamic-split` | off | Let the left/right split point change over the song |
| `--split-change-penalty` | 100 | Cost of moving the split point between segments |
| `--split-max-change` | 3 | Max keys the split can move between segments |
| `--segment-size` | 8 | Time steps per segment for dynamic split |
| `--rh-only` | off | Put every note on the right hand |
| `--transpose` | off | Legacy: transpose to white keys only |
| `--output` | `outputs` | Output folder |
| `--prefix` | (none) | Filename prefix, usually the song name |

Run `python3 findOptimalHandPos.py --help` for the authoritative list.

## Verifying output

```
python3 verify_fingering.py --dir outputs
python3 verify_fingering.py --dir outputs --verbose
python3 verify_fingering.py --self-test
```

Pass the same `--speed` and `--gap` you gave the optimizer if you changed them.

## Regenerating the dashboard data

```
python3 scripts/generate_new_songs.py     # rewrites outputs/<demo-song>_timed_steps.csv
python3 scripts/build_dashboard_data.py   # traces all 61 songs into dashboard/
```

The build writes `dashboard/data-manifest.json`, `dashboard/data-part*.json`
(the trace, about 20 MB, split into size-capped chunks so it fits static-host
file limits) and `dashboard/songs_manifest.json`. Both scripts find the repo
root from their own location, so they work from any directory.

To add a song, either drop a MusicXML file into `inputs/` and run
`run_all.py` (which writes its `timed_steps.csv`), or add a generator to
`scripts/generate_new_songs.py`. Then rebuild the dashboard data. The build
does not scan `outputs/` on its own: a MusicXML song only appears once you add
`("<song-id>", "<Display Name>")` to `ORIGINAL_SONGS` in
`build_dashboard_data.py`. Generated songs are picked up automatically through
`_new_songs_manifest.csv`.

## Viewing the dashboard

The dashboard loads its data with `fetch`, so it must be served over HTTP
rather than opened as a `file://` URL:

```
cd dashboard
python3 -m http.server 8000
```

Then open <http://localhost:8000/>. Any static host works for deployment;
publish the whole `dashboard/` folder.
