---
name: cov12-b-r77
start: cov5-f-del@192140
reference: forbidden
steps:
  - in room 77 (world 5, stage 7's flooded hold) Hammer Kirby takes the right-hand door (cell 0, $D4), the one an enemy of type $2B stands on, into room 84 (never loaded before): room == 84
  - in room 84 he takes the Maxim Tomato (type 5) and beats the enemy of type $16 beside it: room == 84 and hp == 47 and ram[0x6128+10] != 5 and ram[0x6128+11] != 22
  - he leaves by room 84's door under the water, back into room 77 (cell 0, $D8): room == 77 and frame > 192400
forbid:
  - lost a life: lives < 4
  - took a hit: hp < 39
---
Coverage movie (batch 12, part B). Room 77 has two doors above the water on short posts; the corpus only ever took
the left one (to room 83). The right one (cell 0, $D4) has an enemy of type $2B (kind $2E) standing on it. Hammer
Kirby (from cov5-f-del, the 100% file) enters it into room 84, a small walled room with a Maxim Tomato and an enemy
of type $16 (kind $1A) on a ledge over water, which no movie had loaded; he takes the tomato, beats the enemy and
leaves by the room's underwater door back to room 77, without taking a hit.
