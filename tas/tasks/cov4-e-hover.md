---
name: cov4-e-hover
start: main@24766
reference: forbidden
steps:
  - the hovering type $2F (variable 0 = 2) comes out of the tower's doorway in room 194 with six rounds to fly (variable 6): room == 194 and ram[0x6128+11] == 0x2F and ram[0x6236+11] == 6 and ram[0x6290+11]*256 + ram[0x627E+11] == 0xADC3
  - Kirby (the UFO) backs away to the left in front of it, so it stays on the screen while it bobs: room == 194 and ram[0x6128+11] == 0x2F and ram[0x6236+11] == 2 and ram[0x6290+11]*256 + ram[0x627E+11] == 0xADC3
  - its last round ends (variable 6 = 0) and entry $0A of e2f_scripts starts and it flies off upward (tick 25.B0C7): room == 194 and ram[0x6128+11] == 0x2F and ram[0x6236+11] == 0 and ram[0x6290+11]*256 + ram[0x627E+11] == 0xB0C7
forbid:
  - lost a life: lives < 4
  - Kirby hit: hp < 39
---
Coverage movie (cov4, unit en25b). The hovering type $2F flies toward Kirby with six rounds of eight bobbing phases
(variable 6). In every corpus movie it was beaten or left the screen before its rounds ran out. Here main's Kirby (the
UFO) backs away to the left ahead of it for about 300 frames, so e2f_tick_hover counts variable 6 down to 0
(25:ADE7 taken, 25:AE18) and entry $0A of e2f_scripts (25:ADBA) gives it the tick routine at 25:B0C7-B0E0: it rises
off the top of the screen.
