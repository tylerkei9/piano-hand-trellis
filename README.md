# Piano Hand Trellis

Plans how a robotic hand moves across a piano keyboard to play a song.

![The dashboard showing Hot Cross Buns. Notes fall onto a keyboard, and below them every hand position the program considered, with the chosen path in orange.](docs/dashboard.png)

## What this is

For each note in a song, a robotic hand could sit in many positions. Some
make the next notes easy to reach. Others lead to stretches or long jumps.
The program compares these options across the whole song and picks the
sequence of hand positions with the least strain and movement.

The dashboard steps through each song note by note. It shows the positions
the program considered, the one it chose and why, and plays the music.

## How it works

A hand covers about one octave, the robot has a top speed, and every note
must be reachable when it is played. The best position for one note can make
the next few notes hard to reach, so the program plans the whole song at
once instead of one note at a time.

Comparing every possible plan directly is not practical. The program uses
the Viterbi algorithm, a standard method for finding the lowest-cost path
through a sequence of choices. It finds the best plan in under a second.

[How this works](ALGORITHM.md) explains the method without code.

## The dashboard

| Section | Shows |
| --- | --- |
| **Song and hardware mode** | Choose one of 61 songs. *Right-hand-only* mode simulates a failed left hand. |
| **Path summary** | Totals for the chosen plan: distance moved, repositions and awkward reaches. |
| **Piano roll** | Notes reaching the keyboard in time with the music, with sound. |
| **Decision map** | Every possible hand position at every note. The orange line is the chosen plan. Click a position to see its costs. |

The songs include six familiar pieces (Hot Cross Buns, Happy Birthday,
Twinkle Twinkle Little Star, Mary Had a Little Lamb, the Star-Spangled Banner
and Fuyu no Hanashi) and 55 short exercises: scales, leaps, arpeggios and
black-key passages.

## Run it

Requires [Python 3](https://www.python.org/downloads/).

1. Click the green **Code** button on this page, choose **Download ZIP** and
   unzip it.
2. Open a terminal (on a Mac, search Spotlight for *Terminal*) and go to the
   `dashboard` folder:
   ```
   cd ~/Downloads/piano-hand-trellis-main/dashboard
   ```
3. Start a local web server:
   ```
   python3 -m http.server 8000
   ```
4. Open **http://localhost:8000/** and click **Enter dashboard**.

Press `Ctrl + C` in the terminal to stop the server.

## Contents

| Path | Contents |
| --- | --- |
| `dashboard/` | The interactive dashboard. |
| `ALGORITHM.md` | How the program decides, without code. |
| `findOptimalHandPos.py` | The program. Reads sheet music and plans the hand's movements. |
| `inputs/` | Sheet music for the six main songs. |
| `outputs/` | Every song's notes in the format the program reads. |
| `output_rh_only/` | Example results for right-hand-only mode. |
| `docs/` | The screenshot and the [developer guide](docs/DEVELOPERS.md). |

## For developers

See the [developer guide](docs/DEVELOPERS.md) for setup, commands, options
and how to rebuild the dashboard data.
