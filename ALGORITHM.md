# How this works

This project answers one question: when a robot plays a song on a piano,
where should its hand be at each moment, and which finger presses each key?

A hand covers about one octave, it moves at a limited speed, and every note
must be reachable when it is played. A position that is convenient now can
also leave the hand badly placed for the next few notes. This document
explains how the program handles that, without code. The code is in
`findOptimalHandPos.py`, and the `dashboard/` shows it running step by step.

## The five steps

1. **Read the sheet music.** The program reads a music file and records
   each note's pitch, start time, length and whether it is a black key.
2. **Divide the notes between the hands.** For a two-handed piece, the
   keyboard is split at one point: notes below it go to the left hand, notes
   above it to the right. The split point is chosen by search (see
   [Choosing the split point](#choosing-the-split-point)).
3. **Choose a hand position for every note.** This is the main problem,
   described below.
4. **Assign fingers.** Once the thumb's position is fixed, the other fingers
   mostly follow. The special cases are black keys (which finger plays them)
   and notes just outside the hand's reach (whether the thumb or pinky
   stretches, or "splays," to reach them).
5. **Write robot commands.** The final plan is written out as step-by-step
   instructions for the robot.

## Choosing where the hand goes

At each note there are several places the thumb could sit and still reach
that note or chord. Each move between notes has a cost. Longer moves cost
more, moves faster than the hardware allows cost much more, and awkward
fingerings add a small cost. The goal is the lowest total cost for the whole
song, not the lowest cost at each note separately.

This is similar to planning a road trip: the cheapest next stop is not always
part of the cheapest overall route.

There are far too many possible sequences to compare one by one. The program
avoids this with one observation: for any position at any note, only the
cheapest way of arriving there matters. Any more expensive way of reaching
the same position can never lead to a better result later, so it is dropped
immediately.

The program moves through the song one note at a time. For each candidate
position, it keeps the cheapest way of reaching it and records which earlier
position that came from. At the end, it takes the cheapest final position
and follows those records backward to recover the full plan.

This method is the **Viterbi algorithm**. It is also used in speech
recognition and route planning. It solves each song in under a second.

## What makes a position costly

- **Distance.** Any move has a flat cost, plus a cost for each key moved.
- **Speed.** A long move between two closely spaced notes may exceed the
  hardware's top speed. This has a high cost because the robot cannot do it.
- **Fingering.** Playing a black key with the thumb or pinky instead of a
  middle finger adds a small cost. Stretching past the hand's natural span
  adds more and is used only when no better option exists.
- **Dead ends.** The program checks a few notes ahead. A position that is
  cheap now but makes an upcoming note hard or impossible to reach gets an
  extra cost.

## Choosing the split point

The split point between the hands affects how hard each hand's part is, so
it is not fixed at middle C. The program tries a range of split points, runs
the full search for both hands at each one, and keeps the split with the
lowest combined cost. It first checks the whole keyboard at wide intervals,
then checks closely around the best result.

## When a song cannot be played

Some chords are wider than one hand can reach in any position, even with
stretching. In that case the program reports that the chord is unplayable
instead of producing an invalid plan. The dashboard's right-hand-only mode
shows this: with one hand covering every note, some songs' widest chords
become unplayable.
