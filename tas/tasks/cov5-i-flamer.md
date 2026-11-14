---
name: cov5-i-flamer
start: main@6190
reference: forbidden
steps:
  - in 1-3's room 54 the crawler of type $17 in slot 10 leaps off the block cross toward Kirby (its tick routine e17_hit, 2B:AA13): room == 54 and ram[0x6128+10] == 0x17 and ram[0x6290+10]*256 + ram[0x627E+10] == 0xAA13
  - it dashes at Kirby (tick e17_tick_dash, 2B:A57D): room == 54 and ram[0x6128+10] == 0x17 and ram[0x6290+10]*256 + ram[0x627E+10] == 0xA57D
  - after the dash's upward swing its turn (tick e17_tick_turn, 2B:A59A) finds a block beside it and goes on steering (variable 2 = a new wait, not 0): room == 54 and ram[0x6128+10] == 0x17 and ram[0x6290+10]*256 + ram[0x627E+10] == 0xA59A and ram[0x61EE+10] > 1
forbid:
  - lost a life: lives < 4
  - Kirby hit: hp < 39
---
Coverage movie (cov5, unit en2b). From main in 1-3 (room 54) Kirby walks about under the cross of blocks and keeps
the leaping crawler (type $17, slot 10) near him without touching it: it leaps off, steers to the point beside him and
makes its first dash, which ends with the upward swing next to a block. e17_tick_turn turns obj_dir by $10 the other
way (2B:A5C8-A5CE, the aim below obj_dir) and its probe of the four sides finds that block (2B:A5EB-A603: the jump to
e17_tick_home's speed step, 2B:A683), and in the frames after it waits (2B:A59F: variable 2 not yet 0). In the corpus
the turn ran twice (w12-sonnet), both times with no surface around.
