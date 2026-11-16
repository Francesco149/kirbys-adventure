---
name: cov12-b-r67
start: main@85760
reference: forbidden
steps:
  - in room 67 the bomb block (col 39, row 6) goes off under UFO Kirby's shot and the chain of bomb blocks under the sealed door goes: room == 67 and ram[0x6AA2] != 0xFB
  - Kirby climbs the shaft to the hidden door (cell 2, $A2) and enters room 68 (never loaded before): room == 68
  - in room 68 he takes the 1-Up on the cloud: room == 68 and lives == 7
  - and leaves by room 68's own door back to room 67 (cell 2, $D2): room == 67 and frame > 86300
forbid:
  - lost a life: lives < 6
---
Coverage movie (batch 12, part B). In room 67 (world 5) the door at cell 2, $A2 sits in a sealed chamber; the
block row under it is a chain of bomb blocks started by the bomb block at the chamber's lower left (tile $20).
UFO Kirby (main's glitched UFO, ability reads $FF) shoots the bomb block, flies up the opened shaft and enters room 68, a single
cloud with an enemy of type $23 (it hits Kirby once and is gone) and a 1-Up (type 5), which no movie had loaded. He takes the 1-Up and goes back
through room 68's door to room 67.
