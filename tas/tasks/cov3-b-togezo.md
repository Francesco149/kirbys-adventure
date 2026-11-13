---
name: cov3-b-togezo
start: main@8795
reference: forbidden
steps:
  - Togezo (type $3C) walks in slot 14 of room 59 (state 0): room == 59 and ram[0x6136] == 0x3C and ram[0x620E] == 0
  - its walk runs out (variable 4 = 0) and it hops (state 2): ram[0x6136] == 0x3C and ram[0x620E] == 2 and ram[0x6220] == 0
  - it rolls (state 1): ram[0x6136] == 0x3C and ram[0x620E] == 1
  - the roll runs out and it walks again with a new count (state 0, variable 4 = 240): ram[0x6136] == 0x3C and ram[0x620E] == 0 and ram[0x6220] == 240
forbid:
  - lost a life: lives < 4
---
Coverage movie (unit en26b). In the shaft of room 59 Togezo walks on a ledge above Kirby, who stays still below
it, out of its height. Its walk lasts the full 240 frames (none did in the corpus), so it hops and rolls on its
own, and the roll lasts its 60 frames of rolling: both ends never ran before.
