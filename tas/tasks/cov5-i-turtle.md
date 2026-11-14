---
name: cov5-i-turtle
start: w12-opus@39340
reference: forbidden
steps:
  - in the closed room 185 the blue turtle mid-boss (type $4F, slot 10) fights the normal-form Kirby: room == 185 and ram[0x6128+10] == 0x4F
  - Kirby hovers high beside the right pillar; the turtle's dash at him runs into the pillar and e49_scripts entry $17 starts (tick routine 2A:B8B5): room == 185 and ram[0x6128+10] == 0x4F and ram[0x6290+10]*256 + ram[0x627E+10] == 0xB8B5
  - the bounce off the wall plays out and the turtle rests again (tick e4f_tick_rest 2A:B4EF): room == 185 and ram[0x6290+10]*256 + ram[0x627E+10] == 0xB4EF and ram[0x6086+10]*256 + ram[0x6074+10] < 380
forbid:
  - lost a life: lives < 4
  - dying: hp > 47
---
Coverage movie (cov5, unit en2a). From w12-opus at the start of the blue turtle's fight (room 185, Kirby with 31 hit
points) Kirby stays out of its way, ending up hovering high beside the pillar at the right of the arena. The turtle
dashes at him and runs into the pillar: e4f_tick_dash's wall path (2A:B6A2-B6A4: entry $17), whose script
2A:B32E-B369 (the bounce back off the wall, never run before) and its tick routines 2A:B8B5-B92D run until it rests
again. Kirby takes one hit on the way (31 -> 23).
