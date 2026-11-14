---
name: cov4-b-fuse
start: cov3-a-cannon@59981
reference: forbidden
steps:
  - Kirby dashes into the fuse cannon of 4-3 before the fuse is lit (the cannon in slot 12 runs e06_tick_loaded 23.A658; the fuse in slot 10 still at X 316): room == 248 and ram[0x6128+12] == 6 and ram[0x629C]*256 + ram[0x628A] == 0xA658 and ram[0x6086+10]*256 + ram[0x6074+10] == 316
  - Down held in the cannon until its count ran out (tick 23.A688): ram[0x6128+12] == 6 and ram[0x629C]*256 + ram[0x628A] == 0xA688
  - Down let go, loaded again (tick 23.A658): ram[0x6128+12] == 6 and ram[0x629C]*256 + ram[0x628A] == 0xA658
  - A pressed, Kirby jumps out and the cannon waits again (tick e06_cannon_tick 23.A5C7): ram[0x6128+12] == 6 and ram[0x629C]*256 + ram[0x628A] == 0xA5C7 and y > 100
  - then a Fireball dash lights the fuse (the end in slot 10 leaves X 316): room == 248 and ram[0x6128+10] == 11 and ram[0x6086+10]*256 + ram[0x6074+10] < 310
  - the fuse burns down while the cannon is empty and on the screen (e06_cannon_tick sees $07DB and the cannon fires without Kirby): room == 248 and ram[0x07DB] != 0 and ram[0x6128+12] == 6 and x > 380
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov4, units en23 / en_cov3): the fuse cannon of 4-3 left and fired empty. From cov3-a-cannon near the
fuse (Fireball copied), Kirby passes the top of the rope with Fireball dashes (one from its right: the other side
of e0b_lit_test's X test), dashes into the cannon's opening (Kirby's trail effects in slots 3-5 are freed by
e06_cannon_clear_fx), holds Down in the cannon until its count runs out (23:A66B-23:A697), lets go, and presses A,
which lets him jump out (e06_fire_test 23:A6A7). Then he lights the fuse with a dash and waits right of the
cannon: the fuse burns down with the cannon empty, and e06_cannon_tick starts 23:A579 (the cannon fires a blast with
nobody in it). In the corpus Kirby only ever sat in the cannon until it fired.
