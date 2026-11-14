---
name: cov5-i-bonk
start: main@111330
reference: forbidden
steps:
  - in 7-2's room 113 Select drops main's UFO, then Kirby takes the upper door to Bonkers' room 133: room == 133 and ram[0x5E0] == 0 and ram[0x6128+13] == 0x4C
  - Bonkers (type $4C, slot 13) runs (variable 9 = 4) under the flying Kirby into the left wall and turns to the hop back (variable 9 = $0A): room == 133 and ram[0x626C+13] == 10 and ram[0x6086+13]*256 + ram[0x6074+13] <= 30 and hp == 31
  - at his next run Kirby hovers right above him, the swing that follows sees Kirby above and leaps (variable 9 = 7): room == 133 and ram[0x626C+13] == 7 and abs(x - (ram[0x6086+13]*256 + ram[0x6074+13])) <= 3 and hp == 31
  - at a throw the thrown object (type $4C in slot 16) lands on the floor (state 0): room == 133 and ram[0x6128+16] == 0x4C and ram[0x6200+16] == 0 and ram[0x60AA+16]*256 + ram[0x6098+16] >= 150 and hp == 31
forbid:
  - lost a life: lives < 6
  - Kirby hit: hp < 31
---
Coverage movie (cov5, unit en28). From main in 7-2 (room 113) Select drops the UFO and the normal-form Kirby takes the
upper door to room 133, where Bonkers fights. Kirby flies near the ceiling and stays out of reach the whole time:
- the first run starts with Kirby at the left wall and high up, so Bonkers runs under him into the wall during the
  run steps: e4c_tick_walk's path for a wall while the pose is below $0A (28:A424-A429: variable 9 = $0A, e4c_set_next);
- at the next run Kirby hovers right above him when the step count is taken: e4c_run_count gets a distance below 6
  and makes it 1 (28:A6AC);
- Kirby out of its way, the thrown object falls to the floor (e4c_tick_thrown's landing,
  28:A2D1-A2D8: state 0) and, its variable 3 run out, makes its second flight (the script 28:A2A4-A2BB).
