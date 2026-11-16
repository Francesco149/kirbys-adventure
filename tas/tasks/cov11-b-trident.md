---
name: cov11-b-trident
start: main@103522
reference: forbidden
steps:
  - in room 106 (world 5) Kirby stands on the small block under the trident knight's ledge, less than 32 px from it in X, while the trident knight (type $35, slot 11) walks its ledge (state variable 3 = 0, e35_st_walk): world == 5 and room == 106 and ram[0x6128+11] == 0x35 and ram[0x6200+11] == 0 and abs(x - (ram[0x6086+11]*256 + ram[0x6074+11])) < 32 and y >= 96 and y <= 111
  - it walks to the end of the ledge with its count below $3C and Kirby within 32 px: 27:B343 starts the script e35_hop_back (27:B186), the only writer of variable 3 = 2: world == 5 and room == 106 and ram[0x6128+11] == 0x35 and ram[0x6200+11] == 2 and ram[0x625A+11] == 0x78
forbid:
  - lost a life: lives < 6
  - hurt: hp < 7
---
Coverage movie (batch 11, part B; unit en27). In the ambush of room 106 the trident knight walks a 32-px ledge
(x 112-143) and backs away from Kirby. main stayed 64+ px away. Here Kirby flies right onto the block under the
ledge and waits, within 32 px of it in X: the knight walks to the ledge's end with variable 8 below $3C, and
e35_st_walk's never-run side 27:B343 starts the never-read script at 27:B186 (e35_hop_back: variable 3 = 2,
a hop back of $0100 with Y velocity -3, sound $0D); the knight hops off the ledge down to the floor.
