# How this works (no coding background required)

This project answers one question: **if a robot is going to play a song on
a piano, where should its hand be at every moment, and which finger should
press each key?**

That sounds simple, but a hand can only comfortably cover about an octave
at once, it can only move so fast, and every note in the song has to be
reachable at the exact moment it's needed -- all while also thinking ahead
so a convenient position right now doesn't strand the hand somewhere
awkward two notes later. This document explains, without any code, how
the program figures that out. For the code itself, see
`findOptimalHandPos.py`; for a step-by-step visual of it running, see the
`dashboard/`.

## The five steps

**1. Read the sheet music.** The program reads a music file and pulls out
every note: what pitch it is, when it starts, how long it lasts, and
whether it's a black key.

**2. Decide which hand plays what.** For a two-handed piece, the keyboard
gets divided at some point -- say, everything below middle C goes to the
left hand, everything at or above goes to the right. Picking *where* to
divide it is itself a small search (see "Choosing the split point"
below), because the wrong choice can make one hand's part needlessly
hard.

**3. Work out where the hand should be for every note.** This is the
heart of the project, and it's explained in detail below.

**4. Work out which finger plays each note.** Once the hand's position
(specifically, its thumb) is decided, the other four fingers mostly fall
into place naturally. The tricky cases are black keys (which finger
reaches for it, and from which side) and notes just out of comfortable
reach (does the thumb or pinky stretch, or "splay," to get it?).

**5. Turn that into a list of robot commands.** The finished plan --
position by position, finger by finger -- gets written out as
instructions a robot could follow.

## The heart of it: choosing where the hand goes

Imagine planning a driving route with 40 stops, where you're allowed to
skip around in any order, but every mile you drive costs you money, and
driving too fast between two nearby stops costs *extra*. You want the
cheapest total route. There are enormous numbers of possible orders --
trying all of them is out of the question.

The hand-position problem is the same shape: at every note in the song,
there are several *candidate* places the hand's thumb could sit and still
reach that note (or that chord of notes). Moving the hand between notes
costs "money" -- more for a bigger jump, extra if the jump has to happen
faster than the hardware can move, and a bit more for an awkward
fingering like a black key under the thumb. The program wants the
cheapest possible sequence of positions across the *entire* song, not
just the cheapest choice at each note taken by itself, because a cheap
choice right now can force an expensive one later.

**The trick that makes this solvable** is that you don't actually need to
compare every full route to find the cheapest one. At each note, for each
candidate hand position, all that matters going forward is: *what's the
cheapest way to have gotten here so far?* It doesn't matter which exact
earlier positions were visited to achieve that cheapest cost -- only the
cost itself and where the hand ends up. So the program walks through the
song one note at a time, and at each note, for each candidate position,
it keeps only the single cheapest way of reaching it (remembering which
earlier position that came from, so the full path can be traced back out
at the end). Every more expensive way of reaching that same position gets
thrown away immediately, because it could never end up winning later
either -- it's already worse, starting from the same place.

That one idea turns a problem that would otherwise take longer than the
age of the universe to brute-force into one a laptop solves in well under
a second. This general technique has a name -- the **Viterbi
algorithm** -- and it's the same idea used in things like speech
recognition (finding the most likely sequence of words) and GPS
navigation (finding the cheapest route on a map).

Once every note has been processed this way, the program looks at
whichever final candidate position ended up cheapest overall, and traces
back through the "came from" trail to recover the full sequence of hand
positions for the whole song -- that's the answer.

## What makes a position "expensive"

- **Distance.** Moving the hand at all costs a flat fee, plus more for
  each key of distance covered.
- **Speed.** If two notes are close together in time but the hand has to
  travel a long way between them, the required speed might exceed what
  the physical hardware can actually do -- that's penalized heavily,
  since going faster than possible isn't just "expensive," it's not
  achievable at all.
- **Awkward fingering.** Playing a black key with the thumb or pinky
  (rather than a middle finger) costs a bit extra, and stretching a
  finger beyond the hand's natural span ("splaying") costs more still,
  used only as a last resort when there's no better option.
- **Painting yourself into a corner.** The program also peeks a few notes
  ahead: if a position would be cheap right now but make an upcoming note
  impossible (or very expensive) to reach, that's penalized too, so the
  hand doesn't take a shortsighted bargain.

## Choosing the split point

Since where the keyboard gets divided between the two hands affects how
hard each hand's part is, the program doesn't just pick a fixed dividing
line (like always splitting at middle C). Instead it tries a range of
candidate split points, actually runs the full position-choosing search
above for both hands at each candidate, and keeps whichever split
produces the lowest combined cost for both hands together. It does this
in two passes -- a coarse pass across the whole keyboard, then a finer
pass zoomed in around the best coarse answer -- so it stays fast without
missing the true best split by much.

## When it isn't possible at all

Sometimes a chord is simply too wide for one hand to play, no matter
where the hand sits -- the notes are farther apart than any reachable
finger span, even with stretching. The dashboard's "right-hand-only"
hardware-failure mode is a deliberate way to see this happen: with only
one hand available and no dividing line to lean on, some songs' widest
chords become unplayable, and the tool reports that plainly instead of
guessing.
