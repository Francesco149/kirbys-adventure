---
name: cov9-b-cannon
start: main@123500
reference: forbidden
steps:
  - Fireball copied in 7-5's cannon room (room $A6), the fuse (type $0B, slot 9) still at the top of the rope: room == 166 and ability == 4 and ram[0x6128+9] == 11 and ram[0x6086+9]*256 + ram[0x6074+9] == 316
  - the fuse is lit (its tick routine leaves e0b_tick 23:AAAF): room == 166 and ram[0x6128+9] == 11 and ram[0x6290+9]*256 + ram[0x627E+9] != 0xAAAF
  - Kirby sits in the cannon (a type $06 object on e06_tick_loaded 23:A658) before the spark reaches it: room == 166 and ram[0x07DB] == 0 and ((ram[0x6131] == 6 and ram[0x6299]*256 + ram[0x6287] == 0xA658) or (ram[0x6132] == 6 and ram[0x629A]*256 + ram[0x6288] == 0xA658) or (ram[0x6133] == 6 and ram[0x629B]*256 + ram[0x6289] == 0xA658) or (ram[0x6134] == 6 and ram[0x629C]*256 + ram[0x628A] == 0xA658) or (ram[0x6135] == 6 and ram[0x629D]*256 + ram[0x628B] == 0xA658) or (ram[0x6136] == 6 and ram[0x629E]*256 + ram[0x628C] == 0xA658) or (ram[0x6137] == 6 and ram[0x629F]*256 + ram[0x628D] == 0xA658) or (ram[0x6138] == 6 and ram[0x62A0]*256 + ram[0x628E] == 0xA658) or (ram[0x6139] == 6 and ram[0x62A1]*256 + ram[0x628F] == 0xA658))
  - the fuse burnt down and the cannon fires shot kind 1 (world 6: e06_shot_kind gives 1; variable 1 of the cannon = 1): room == 166 and ram[0x07DB] != 0 and ram[0x07DA] == 0x82 and ram[0x6128+15] == 6 and ram[0x61DC+15] == 1
  - Kirby flies up and right out of the room into room $A7: room == 167
forbid:
  - lost another life: lives < 7
---
Coverage movie (cov9, unit dead_en1 / en23): the cannon of kind $F9 in 7-5's room $A6 (world index 6), which main
passed at frame 123360 without firing it. e06_shot_kind gives world 6 shot kind 1, the diagonal shot (e06_shot_1,
e06_shot_spin, Kirby's flight with e06_shot_tick_diag). From main@123500 (Kirby with one bar left): the laser of a
type $16 kills him (the life is spent on purpose: he starts the room again with full health), Fireball copied from
the type $17 that circles the blocks, a Fireball dash over the top of the rope lights the fuse, Kirby runs and jumps
to the cannon and sits in it while the spark is still on the screen (a spark left far behind the camera vanishes
and never sets $07DB), the cannon fires him up and to the right into room $A7.
