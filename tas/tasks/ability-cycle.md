---
name: ability-cycle
start: 1-1-speed:r43_start
reference: forbidden
steps:
  - an ability copied in 1-1's first area: room == 43 and ability != 255 and hp == 47
  - knocked out by a hit: room == 43 and ability == 255 and hp == 39
  - regained from its star: room == 43 and ability != 255 and hp == 39
  - carried into the second area: room == 44 and ability != 255
forbid:
  - lost a life: lives < 4
  - took a second hit: hp < 39
---
A "test trace" task: exercise one behaviour of the game end to end, the copy-ability lifecycle. The trace is meant
as a regression test for that mechanic, so every stage of it is a state predicate.

The movie starts from a verified library prefix: the 1-1-speed trace from power-on to the first frames of 1-1
(room 43, frame 569: no ability, full HP 47, 4 lives). 1-1's first area has ability enemies (the walkthrough lists
Waddle Doo → Beam, Hot Head → Fire, Sparky → Spark). In this order:
1. copy any ability (inhale an ability enemy with B, swallow with Down) without taking damage;
2. take exactly one hit from an enemy: in this game a hit knocks the ability out of Kirby as a bouncing star;
3. get the ability back by inhaling that star and swallowing it, before it disappears;
4. carry the ability through the door into the second area (room 44).

No life may be lost and HP must not drop below 39 (one hit only).

You will need to find out how the knocked-out ability star shows up in state terms (the object slots) to chase it.
Report the cost per step and what the driver card got wrong or lacked.
