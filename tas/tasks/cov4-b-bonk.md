---
name: cov4-b-bonk
start: w3-sonnet@71690
reference: forbidden
steps:
  - Bonkers (type $4C in slot 13) throws, its thrown object (type $4C, variable 0 = 1) appears in slot 12: room == 225 and ram[0x6128+12] == 0x4C and ram[0x6128+13] == 0x4C
  - Kirby gets out of its way and it is still flying 45 frames later: room == 225 and ram[0x6128+12] == 0x4C and frame >= 71815 and hp == 7
  - at its next throw (state 5, variable 9 of slot 13) Kirby is less than 40 pixels from it, so e4c_near answers 1 and it jumps at him instead: room == 225 and ram[0x6279] == 5 and abs(x - (ram[0x6086+13]*256 + ram[0x6074+13])) < 40 and hp == 7
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov4, unit en28). In w3-sonnet the object Bonkers throws (e4c_thrown) was hit in its first frame.
Here Kirby (7 hit points left) dodges it, so e4c_tick_thrown goes past the hit test: obj_collide, obj_gravity_a and
the rest of its tick routine (28:A2CA-A2ED) run while it flies across the arena. Kirby then stays out of
trouble until the next throw comes round in its cycle of states and is near it at that moment: e4c_near answers
1 (28:A545) and the throw state takes its other way, a jump at Kirby.
