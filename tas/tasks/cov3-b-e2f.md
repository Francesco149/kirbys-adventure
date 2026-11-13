---
name: cov3-b-e2f
start: main@40560
reference: forbidden
steps:
  - the creature of type $2F in slot 13 leaps (tick e2f_tick_leap 25.AFF4): ram[0x629D]*256 + ram[0x628B] == 0xAFF4 and room == 235
  - it rises above the top of the screen (entry 3 of e2f_scripts, tick 25.B075): ram[0x629D]*256 + ram[0x628B] == 0xB075
  - and goes on to the tick routine 25.B0E1: ram[0x629D]*256 + ram[0x628B] == 0xB0E1
forbid:
  - lost a life: lives < 4
---
Coverage movie (unit en25b). In the tower shaft of room 235 (world 3) the orange creature of type $2F lurks on a
ledge. Kirby floats up beside it so that it leaps, then stays below and lets it rise: no movie had it go above the
top of the screen, so the scripts behind entry 3 of e2f_scripts never ran.
