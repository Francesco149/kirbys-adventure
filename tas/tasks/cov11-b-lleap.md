---
name: cov11-b-lleap
start: cov3-a-lance2@56150
reference: forbidden
steps:
  - in room 264 (low byte 8, world 3) the leaping lance knight (type $34 variant 0, slot 10, state 0 e34_st_leap) is in its last leap (variable 8 = 1) with variable 9 = 1 and Kirby 40+ px away in X: world == 3 and room == 8 and ram[0x6128+10] == 0x34 and ram[0x6200+10] == 0 and ram[0x625A+10] == 1 and ram[0x626C+10] == 1 and abs(x - (ram[0x6086+10]*256 + ram[0x6074+10])) >= 40
  - it lands: 27:B61B starts the never-read script e34_throw_spear (27:B40B), the only writer of variable 3 = 2 with variable 6 = $FA: world == 3 and room == 8 and ram[0x6128+10] == 0x34 and ram[0x6200+10] == 2 and ram[0x6236+10] == 0xFA
  - the thrown spear (type $31) flies: world == 3 and room == 8 and (ram[0x6128+16] == 0x31 and ram[0x6290+16] == 0xB9 and ram[0x627E+16] == 0xC4)
forbid:
  - lost a life: lives < 4
---
Coverage movie (batch 11, part B; unit en27). cov3-a-lance2 stayed within 40 px of the leaping lance knight at its
last landing (the thrust). Here Kirby stands still at x 162, ~69 px away (the mace ball of the other knight hits
him once): with variable 9 = 1 e34_st_leap's never-run side 27:B61B starts the never-read script at 27:B40B
(e34_throw_spear: a crouch, variable 3 = 2, a hop with Y velocity -2 and a thrown spear, a child of type $31 with
variable 0 = 5), and the spear flies off to the right.
