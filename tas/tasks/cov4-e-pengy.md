---
name: cov4-e-pengy
start: main@31464
reference: forbidden
steps:
  - in room 208 Kirby flies from between the two Pengys (type $3A, slots 9 and 12) to the upper left corner: room == 208 and x < 50 and y < 60
  - the left Pengy (slot 9, next to the block at its left) starts a slide to the left (variable 4 = 1, obj_dir $C0): room == 208 and ram[0x6128+9] == 0x3A and ram[0x6212+9] == 1 and ram[0x61DC+9] == 0xC0
  - it slides into the block, e3a_tick turns it round (26.B391) and it slides to the right: room == 208 and ram[0x6128+9] == 0x3A and ram[0x6212+9] == 1 and ram[0x61DC+9] == 0x40 and ram[0x6086+9]*256 + ram[0x6074+9] < 92
forbid:
  - lost a life: lives < 4
  - Kirby hit: hp < 47
---
Coverage movie (cov4, unit en26b). Pengy slides along its facing after standing a while. In the corpus no slide met
a wall. Here main's Kirby flies to the upper left corner of room 208; the left Pengy turns toward him and, with no
breath to blow, slides to the left into the block beside it: the wall path of state 1 (26:B38F taken, 26:B391-B397:
22:90BA and obj_vx_neg_cur) turns it round, and it slides off its ledge to the right.
