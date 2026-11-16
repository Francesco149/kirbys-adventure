---
name: cov11-a-flee
start: cov4-e-fish@6250
reference: forbidden
steps:
  - in room 50 Kirby waits in the right-hand pool at the level of the chasing fish (type $18, slot 10, e18_tick_chase 24:AF9F), which has followed him to the right end of its own pool: room == 50 and x >= 300 and y >= 100 and ram[0x6128+10] == 0x18 and ram[0x6290+10]*256 + ram[0x627E+10] == 0xAF9F and ram[0x6086+10]*256 + ram[0x6074+10] >= 225
  - the chase count reaches $0700 and the fish flees (e18_tick_flee 24:B043): room == 50 and ram[0x6128+10] == 0x18 and ram[0x6290+10]*256 + ram[0x627E+10] == 0xB043
  - it flees straight left; a steering step finds both velocities at their limits (X -$00C0, Y 0) and the script 24:AF90 gives it the tick routine 24:B065 (e18_tick_flee_test): room == 50 and ram[0x6128+10] == 0x18 and ram[0x6290+10]*256 + ram[0x627E+10] == 0xB065 and ram[0x60F2+10] == 0xFF and ram[0x60E0+10] == 0x40
forbid:
  - lost a life: lives < 4
  - hurt: hp < 39
---
Coverage movie (batch 11, part A; unit en_cov4 / en24c). In cov4-e-fish Kirby stayed on the ledge above the fish, so
the fleeing fish fled straight down and bounced between the floor and the surface of its shallow pool: its Y velocity
never reached the limit and e18_tick_flee's test at 24:B055 never saw a step that changed neither velocity. Here Kirby
goes right (the fish follows below him to the right end of its pool) and drops into the right-hand pool at the fish's
level, so when the count reaches $0700 the fish flees straight left (eighth 6: X negative, Y toward 0, Y velocity 0).
After 16 steps the X velocity sits at -$00C0, the next step changes nothing, 24:B057 starts e18_pause_flee (24:AF90)
and the fish runs e18_tick_flee_test (24:B065) until it leaves the screen on the left.
