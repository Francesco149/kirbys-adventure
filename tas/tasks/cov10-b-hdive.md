---
name: cov10-b-hdive
start: cov5-f-del@211600
reference: forbidden
steps:
  - the Hammer's dive lands on an enemy and bounces (kirby_st_hammer_dive_hit, 17:B06C): room == 51 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB06C and frame < 211670
  - B in the bounce: the swing in the air (script $A8, kirby_st_hammer_air_swing 17:B3E5): room == 51 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB3E5 and frame < 211680
  - a second bounce: room == 51 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB06C and frame > 211800
  - Up in it: puffed up (script $A9, kirby_st_hammer_inflate 17:B4BD): room == 51 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB4BD and frame > 211840
  - a third bounce: room == 51 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB06C and frame > 212000
  - Select in it drops the Hammer: room == 51 and ability == 255 and frame > 212055
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov10, unit cov5_tour): the pad exits of kirby_st_hammer_dive_hit (17:B06C), the bounce after Hammer
Kirby's dive hits something, which the corpus had run once (cov5-f-del@211663) and left only by falling. From
cov5-f-del@211600 (room 51, the sea with the posts, Hammer) the same dive bounces off the Waddle Dee; B in the bounce
gives the swing in the air (17:B0A4 falls through: script $A8). Two more dives onto the room's walkers bounce again: Up in
the second puffs him up (17:B0C2: script $A9), Select in the third drops the Hammer (17:B0D6: pad_select_drop, script 1).
