---
name: cov3-c-dedede
start: main:7-7-fight
reference: forbidden
steps:
  - King Dedede starts an inhale: ram[0x6128+12] == 71 and ram[0x6242] >= 0x50 and ram[0x6242] <= 0x5A
  - the inhale runs out with Kirby out of reach: ram[0x6128+12] == 71 and ram[0x6242] <= 3 and frame < 129720
  - a later inhale facing left catches Kirby: ram[0x6128+12] == 71 and ram[0x621E] != 0 and ram[0x6242] > 30 and ram[0x6242] <= 0x5A and ram[0x62C6+12] == 0 and x < ram[0x6086+12]*256 + ram[0x6074+12]
  - Kirby is swallowed and spat out (he had 7 HP): hp == 255
---
Coverage movie for King Dedede's inhale (type $47, unit en_more, e47_tick_inhale). In the 7-7 fight Kirby
floats out of reach through one inhale until its counter (variable 6, $6242 for slot 12) runs out, then stands
in front of Dedede facing left during the next one and is caught (variable 4 set, Kirby's script 2D:A38E).
