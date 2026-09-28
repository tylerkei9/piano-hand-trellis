# Hand-Position Trellis dashboard

A single-page visualization of the Viterbi optimizer in `../findOptimalHandPos.py`.
It shows, for any of the 61 example songs, the full trellis of candidate hand
positions the optimizer considered at every note, which one it kept and why,
a synced piano-roll playback with real audio, and a "right-hand-only" hardware
failure mode.

## Files

- `index.html` — the entire app (HTML/CSS/JS, no build step, no dependencies
  beyond Google Fonts).
- `data.json` — the precomputed trace data for every song, every scenario
  (two-hand / right-hand-only), and both hands where applicable. Generated
  by `../scripts/build_dashboard_data.py` — see the root README to regenerate
  it after adding or editing a song.
- `songs_manifest.json` — a human-readable `{key, label}` list of every song
  in `data.json`, written alongside it by the same build script.

## Running it locally

`index.html` fetches `data.json` at load, so it needs to be served over
HTTP:

```
python3 -m http.server 8000
```

then open `http://localhost:8000/`.

## The song catalog

61 songs total: 6 original pieces traced from real MusicXML scores, plus 55
more added to exercise specific parts of the optimizer — scale runs (speed
limit), arpeggios and broken chords (move penalty), black-key trills
(fingering penalty), leap studies of increasing distance (move + speed
penalty scaling), and repeated-note studies (zero-cost efficiency). See
`songs_manifest.json` for the full list, and `../scripts/generate_new_songs.py`
for what each one is designed to demonstrate.
