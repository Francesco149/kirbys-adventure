---
name: cov11-d-saucer
start: main@87480
reference: forbidden
steps:
  - in room 70 the saucer (slot 9, type $24) ends its first pass with Kirby 24 px or more above or below it, so e24_tick_fly takes 2B:A158 (variable 9 + 1 = 1, another $28-frame pass) instead of crossing to Kirby's other side: room == 70 and ram[0x6128+9] == 0x24 and ram[0x6275] == 1
  - when its climb ends (e24_tick_clear) the first probe (side 3) answers a surface, so 2B:A0C1 is taken to 2B:A0C8 and the loop counter (variable 2) stays 4: room == 70 and ram[0x6128+9] == 0x24 and ram[0x6275] == 2 and ram[0x61F7] == 4
forbid:
  - lost a life: lives < 6
  - hurt: hp < 15
---
Coverage movie (batch 11, part D; unit en2b). main crosses room 70 while the saucer makes its two passes at Kirby's
height and climbs away. Here UFO Kirby drops below the saucer as its first $78-frame pass ends, so obj_dy_kirby
gives 24 px or more and e24_tick_fly takes the "far in height" side (2B:A158: one more short pass instead of the
cross), and the climb that follows ends where the first of e24_tick_clear's four probes answers a surface
(2B:A0C1 taken to 2B:A0C8). The inputs were found with random macro sequences checked against the branch targets on
the instrumented core.
