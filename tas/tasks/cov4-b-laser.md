---
name: cov4-b-laser
start: main@48258
reference: forbidden
steps:
  - main's Kirby (the UFO, with kirby_ability $FF) in 4-3's first room with the fuse unlit in slot 11: room == 248 and ram[0x6128+11] == 11 and ram[0x6086+11]*256 + ram[0x6074+11] >= 312
  - a laser shot (variable 3 = 3) reaches the top of the rope and lights the fuse, the spark runs along the rope: room == 248 and ram[0x6128+11] == 11 and ram[0x6086+11]*256 + ram[0x6074+11] < 305 and ability == 255
  - the fuse burns down ($07DB set): room == 248 and ram[0x07DB] != 0
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov4, unit en23). In main's 4-3 Kirby flies the UFO past the fuse holding B. Here B is let go
earlier, so the charged laser (a shot of variable 3 = 3 in slots 6-8) flies into the top of the rope: e0b_lit_test
takes its shot path (23:ACA3-ACFC: within 10 pixels in X and Y, the shot is freed, carry set) and the fuse burns.
The only lighting in the corpus was by a Fireball dash (kirby_rect of kind 7). Kirby (still the UFO) stays where he
is while the spark runs and the fuse burns down.
