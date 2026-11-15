---
name: cov7-k-ddd
start: cov4-a-ddd@134440
reference: forbidden
steps:
  - King Dedede (type $47, slot 10) is beaten in the 7-7 ring (variable 0 = 0), Kirby next to him on his right: room == 14 and ram[0x6128+10] == 71 and ram[0x61D4] == 0 and x - (ram[0x6090]*256 + ram[0x607E]) < 32
  - Kirby walks off to the right, so when e47_end starts (variable 6 = 1) he is 32 pixels and more away: room == 14 and ram[0x6288] == 0x10 and ram[0x629A] == 0xAF and ram[0x6236+10] == 1 and x - (ram[0x6090]*256 + ram[0x607E]) >= 32
  - the boss slides to a stop with Kirby still far away: variable 6 = $FF without the knock-back: room == 14 and ram[0x6236+10] == 0xFF and x - (ram[0x6090]*256 + ram[0x607E]) >= 32 and hp == 7
  - the stage is cleared: world == 7 and trans == 5
forbid:
  - lost another life: lives < 7
---
Coverage movie (cov7, unit en2d). In cov4-a-ddd (and main) Kirby stood next to the beaten Dedede when e47_end began,
so e47_tick_end knocked him back at once. Here, from cov4-a-ddd at frame 134,440, Kirby walks to the right end of
the ring before e47_end starts: its first tick finds variable 6 = 1 (2D:AF27-AF31: the path for variable 6 positive,
which waits while kirby_action is 3 or more), and when the boss's slide stops with Kirby 32 pixels and more away the
stopped-boss path sets variable 6 = $FF (2D:AF46-AF4B). Then the end of the fight plays out as usual.
