---
name: cov5-g-fuse
start: main@48230
reference: forbidden
steps:
  - main's UFO Kirby flies over 4-3's first room without B and passes the unlit fuse (slot 11 at X 316): room == 248 and ram[0x6128+11] == 11 and ram[0x6086+11]*256 + ram[0x6074+11] == 316 and x > 335
  - right of it he lets go of a charged laser (a shot of variable 3 = 3 in slot 8, right of the fuse) and the fuse stays unlit: room == 248 and ram[0x6128+8] == 3 and ram[0x6208] == 3 and ram[0x6086+8]*256 + ram[0x6074+8] > 316 and ram[0x6086+11]*256 + ram[0x6074+11] == 316
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov5, unit en23). e0b_lit_test looks at Kirby's shots of variable 3 = 1 or 3 and takes the X
distance to each; in the corpus every such shot was left of the fuse (main's charged laser, cov4-b-laser). Here
main's UFO Kirby starts before main holds B, flies over the wall past the fuse and fires a laser charged for 20
frames facing right from X 340: the shot right of the fuse makes e0b_lit_test negate the distance
(23:ACB4-23:ACC0); it is too far to light the fuse.
