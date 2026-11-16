---
name: cov11-b-lance
start: main@55642
reference: forbidden
steps:
  - in room 264 (low byte 8, world 3) the flying lance knight (type $34 variant 1, slot 13, state variable 3 = 6 e34_st_fly) is rising (variable 9 = 0) below screen Y 48: world == 3 and room == 8 and ram[0x6128+13] == 0x34 and ram[0x6200+13] == 6 and ram[0x626C+13] == 0 and ram[0x60AA+13] == 0 and ram[0x6098+13] >= 48
  - it rises above screen Y 32 and 27:B502 holds it at Y 32 (Y velocity 0) while it keeps rising, for several frames: world == 3 and room == 8 and ram[0x6128+13] == 0x34 and ram[0x6200+13] == 6 and ram[0x626C+13] == 0 and ram[0x60AA+13] == 0 and ram[0x6098+13] == 32
  - still held at Y 32 ten frames later: world == 3 and room == 8 and ram[0x6128+13] == 0x34 and ram[0x6200+13] == 6 and ram[0x626C+13] == 0 and ram[0x60AA+13] == 0 and ram[0x6098+13] == 32 and frame >= 56772
forbid:
  - lost a life: lives < 4
  - hurt: hp < 31
---
Coverage movie (batch 11, part B; unit en27). In the ambush of room 264 main beat the flying lance knight (type $34
variant 1, e34_fly) early. Here Kirby waits on the top-left ledge, out of the way, for ~1120 frames. The flyer
bounces between the room's blocks; e34_wall flips its variable 9 (sink / rise) every fourth wall, and on one of its
rising stretches (from main@56743) it climbs past screen Y 32: e34_st_fly's never-run side 27:B502-27:B518 runs
every frame for ~60 frames (Y velocity 0, Y = 32), until the right edge of the screen turns it.
