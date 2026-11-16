---
name: cov12-b-r76
start: main@91050
reference: forbidden
steps:
  - in room 76 (world 5's ship) UFO Kirby takes the door at cell 4, $22 into room 78 (never loaded before), the right half of its cabin: room == 78
  - he takes the 1-Up of room 78's right half: room == 78 and lives == 7
  - out by room 78's right door (back at room 76's cell 4, $44) and in again by that door, into room 79 (never loaded before), its right half, where the hiding enemy of type $1C wakes: room == 79
  - out to room 76 again, then the door at cell 3, $E2 into room 79's left half, and its 1-Up: room == 79 and lives == 8
  - out by room 79's left door (room 76's cell 3, $C4) and in again by that door, into room 78's left half with its type-$1C enemy: room == 78 and lives == 8
forbid:
  - lost a life: lives < 6
  - took a hit: hp < 7
---
Coverage movie (batch 12, part B). Room 76 (world 5, the ship) has four doors below its deck at cell 3, $C4 and
$E2 and cell 4, $22 and $44 that lead to rooms 78 and 79, two cabins split in half by a wall: each half has its own
door, and each cabin has a 1-Up in one half and an enemy of type $1C (kind $6E) in the other. No movie had loaded
either cabin. UFO Kirby (main's glitched UFO, ability reads $FF; hp 7 from main) flies into the closed space under
the deck from the right, enters all four halves through all four doors, takes both 1-Ups and leaves each half by
its own door, without taking a hit.
