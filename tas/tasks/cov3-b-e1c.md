---
name: cov3-b-e1c
start: main@62040
reference: forbidden
steps:
  - the creature of type $1C in slot 11 fades in above Kirby (e1c_tick_fade_in 2A.BCE8): room == 17 and ram[0x6133] == 0x1C and ram[0x629B]*256 + ram[0x6289] == 0xBCE8
  - it lands after coming back (tick 2A.BD1C, entry 7 of e1c_scripts): ram[0x6133] == 0x1C and ram[0x629B]*256 + ram[0x6289] == 0xBD1C
  - and runs on with the tick routine 2A.BD3B: ram[0x6133] == 0x1C and ram[0x629B]*256 + ram[0x6289] == 0xBD3B
forbid:
  - lost a life: lives < 4
---
Coverage movie (unit en2a). In room 17 the creature of type $1C vanishes and comes back above Kirby. Kirby stands
still and lets it fall: in the corpus it was always inhaled or hit before it landed, so the landing after the
reappearance (entry 7 of e1c_scripts, 2A:BD1C-2A:BD79) never ran.
