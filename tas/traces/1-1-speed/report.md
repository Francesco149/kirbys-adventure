# Report: task 1-1-speed (power-on -> 1-1 clear -> W1 hub), normal-Kirby route, no UFO glitch

Result: hub (world 0 room 0) at **f3159**. Reference points: w12-opus 3713, human TAS 2625. Total cost ~$2.9, 2 episodes, ~70 turns.

## Segments (final trace)
| segment | frames | how |
|---|---|---|
| power-on -> 1-1 room 43 | 569 | Start presses f28/f176/f210/f325, U*150 L*58 U*35; coordinate-descent scan of press frames in the lab found nothing better; hub walk is a fixed cutscene (beam on hub gave 244 vs our 243) |
| room 43 | 844 (569->1413) | 2 beam calls: score x to x>=760, then phased score (float up the wall, then door) |
| room 44 | 639 (1433->2072) | one beam call (depth 90, beam 768, 380 s) with run actions, phased score x then door |
| room 45 | 692 (2072->2764) | one beam call (depth 95, beam 768, 371 s), same scheme |
| goal game -> hub | 395 | goalscan: A press at k=56 (also k=56 in every hold length) |

## Improvement table
| version | frames | cum. $ | technique |
|---|---|---|---|
| v1 (rooms 44/45 by partial x-search + door search; no run actions) | 3229 | ~$2.2 | recipe §2 as written |
| v2: rooms 44+45 redone as single phased searches with run actions `. R*7`, `R . R*6` | 3159 (-70) | ~$2.85 | run (double-tap) macros: -72 f on room 45's first 800 px alone (614 -> 542 in the same search) |
Frames/$ of the curve: v1 -> v2 bought 70 f for ~$0.6 (~115 f/$). Further: room 43 redo with run macros (est. -30..-60 f) would force re-searching 44/45 (~$1): not taken.

## What worked / what was wrong in the recipe
- **Missing from the recipe: run macros.** The recipe alphabet (`R*8`, `RA*8`...) never double-taps, so Kirby walks (332) not runs (460). Adding `. R*7` and `R . R*6` cut 72 f of 614 on one 800-px stretch (measured, same start state).
- **Stale x right after a room change**: for ~20 frames after `room` changes, `x` still holds the old room's door x (984), so goals like `x >= 600` fire at depth 1 (happened twice). Gate goals on `x < old_door_x` or start searching ~20 frames later.
- Plain `-2|dx|-|dy|` door score stalled 180 s in room 44 from 380 px out (hills/pit); x-score with a pit penalty `-(y>150)*500` then a short door search worked (recipe's "score x until near the door" advice is right).
- Single phased search per room (x below a threshold, then `const - |dx| - |dy|` near the door, `room changed` bonus) beat the two-call chain by 30-38 f per room, at ~6 min of search wall time each.
- goalscan k=56 confirmed; room change 395 f after the goal-game room starts.
- UFO route (the TAS's 2625): needs 2+ ability enemies inhaled in room 43; an `inab>=2` beam failed (only one reachable on our RNG); not pursued. That is the remaining ~530 f gap.
- Cost note: turns at end of episode cost ~$0.25 each (context growth), consistent with recipe §5.
