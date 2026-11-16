---
name: cov11-b-e3a
start: main@110020
reference: forbidden
steps:
  - in room 111 (world 6) the class-1 creature of type $3A (kind $95, slot 11, obj_param $0784+11 = 1) stands still in state 0 (variable 4 = 0) with Kirby 64+ px away: world == 6 and room == 111 and ram[0x6128+11] == 0x3A and ram[0x0784+11] == 1 and ram[0x6212+11] == 0 and abs(x - (ram[0x6086+11]*256 + ram[0x6074+11])) >= 64
  - its count (variable 5) reaches $4B: e3a_tick's choice at 26:B42B reads obj_param 1 and takes 26:B432 (random below 3): world == 6 and room == 111 and ram[0x6128+11] == 0x3A and ram[0x0784+11] == 1 and ram[0x6224+11] == 0x4B
forbid:
  - lost a life: lives < 6
  - hurt: hp < 39
---
Coverage movie (batch 11, part B; unit en26b). The only class-1 type $3A (kind $95) is placed in room 111 at
(136,152); main walked up to it at once. Here Kirby waits at the room's left end, 80 px away, for ~120 frames: with
no Kirby within 64 px its variable 5 counts up to $4B, and the choice at 26:B42B reads obj_param 1 and takes the
never-run side 26:B432 (random below 3 instead of below 4).
