---
name: cov11-a-chase
start: w12-sonnet@8600
reference: forbidden
steps:
  - in room 50 Kirby drops into the right-hand pool; the chasing fish of the left pool (type $18, slot 11) chases him straight right, both velocities reach their limits and it pauses (e18_tick_pause 24:AFD9): room == 50 and x >= 300 and ram[0x6128+11] == 0x18 and ram[0x6290+11]*256 + ram[0x627E+11] == 0xAFD9
  - Kirby jumps out of the pool up and to the right of the pausing fish (which has bounced off its pool's right wall), and a steering step of the pause changes both velocities: the script 24:AF6A puts it back on e18_tick_chase: room == 50 and y < 90 and ram[0x6128+11] == 0x18 and ram[0x6290+11]*256 + ram[0x627E+11] == 0xAF9F and frame > 8710
forbid:
  - lost a life: lives < 4
  - hurt: hp < 39
---
Coverage movie (batch 11, part A; unit en24c). The chasing fish pauses (e18_pause) when a steering step leaves both
velocities at their limits; in the corpus every pause ended with the fish gone, so e18_tick_pause's test at 24:AFFF
(the step changed X) always returned. Here Kirby (main's route in w12-sonnet) drops into the right-hand pool of room
50, so the fish of the left pool chases him straight right (X +$00C0, Y 0) and pauses. It bounces off the right wall
of its pool in the pause (X velocity -$00C0); Kirby then jumps out of the water up and to its right, the next step
(eighth 1: X positive, Y negative) changes both velocities, and 24:B001-B010 start the chase again (script 24:AF6A).
