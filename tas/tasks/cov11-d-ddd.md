---
name: cov11-d-ddd
start: main@129750
reference: forbidden
steps:
  - King Dedede (slot 12, type $47) is down to 25 hit points (main's third piercing shot); UFO Kirby holds his fire and dodges until Dedede makes a moving jump (variable 5 = 2) with fewer than $21 hit points, which takes the low-HP X speed $0220 (2D:AC07): room == 14 and ram[0x6128+12] == 0x47 and ram[0x61D6] < 33 and ram[0x6230] == 2 and abs(s16(ram[0x60F2+12]*256 + ram[0x60E0+12])) == 0x220
  - in a flight Kirby stays above him until his Y velocity reaches the upward limit -$0180 (e47_vy_toward 2D:B1F1): room == 14 and ram[0x6128+12] == 0x47 and s16(ram[0x6116+12]*256 + ram[0x6104+12]) == -384
  - a UFO shot hits him while he falls after a flight (e47_tick_fly_fall 2D:AAE6) and takes 3 hit points: room == 14 and ram[0x6128+12] == 0x47 and ram[0x61D6] == 22
  - Kirby is on his right when he swings the hammer (slot 11, type $63) the second time: the hammer faces right (e63_tick_swing2 2D:A818): room == 14 and ram[0x6128+11] == 0x63 and ram[0x61DC+11] == 0x40 and ram[0x61DC+12] < 0x80 and ram[0x61D6] == 22
forbid:
  - lost a life: lives < 8
  - hurt: hp < 7
---
Coverage movie (batch 11, part D; units en_more, boss_cov4, cov9). main beats Dedede with three piercing shots
in quick succession. Here, after the third one (25 hit points left), UFO Kirby stops shooting and stays out of his
way: Dedede's next moving jump runs with fewer than $21 hit points (the fast X speed of e47_jump_fall, 2D:AC07); in
his flight Kirby stays above him long enough for e47_vy_toward to reach the -$0180 limit (2D:B1F1); a small shot hits
him as he falls after the flight (e47_tick_fly_fall's carry-set side, 2D:AAE6); and Kirby is on his right when the
hammer's second swing starts (e63_tick_swing2, 2D:A818). The movie ends with Dedede alive (22 hit points); the
inputs were found with random macro sequences checked against the branch targets on the instrumented core.
