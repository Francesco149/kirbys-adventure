---
name: cov9-b-para
start: main@11700
reference: forbidden
steps:
  - in 2-1's first room (room 169) the UFO is dropped with Select (kirby_form 0): room == 169 and ram[0x05E0] == 0
  - through the side door at (584, 137) into the grotto: room == 171
  - Parasol copied from the type $2A in the grotto: room == 171 and ability == 9
  - back in room 169 with the Parasol: room == 169 and ability == 9
  - Down on the thin block at the palm's top (property $0E, bit 5 of prop_shape at both feet): script $C1, routine kirby_st_para_drop (15:B28A): room == 169 and ability == 9 and ram[0x6291]*256 + ram[0x627F] == 0xB28A
  - through the thin block onto the ground below, the Parasol kept: room == 169 and ability == 9 and y > 110 and ram[0x6291]*256 + ram[0x627F] != 0xB28A
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov9, unit dead_kirby): Parasol Kirby drops through a thin floor. From main@11700 (2-1, Kirby as the
glitched UFO, kirby_form $0D) Select drops the UFO, Kirby takes the side door at (584, 137) into the grotto (room 171),
copies the Parasol from the Parasol Waddle Dee, goes back to room 169 and walks right to the top of the palm by the
right door (a block of property $0E, the thin floor), ducks and holds Down: kirby_st_para_crouch's down_bit5_test
answers carry, script $C1 (kirby_s_para_drop) runs kirby_st_para_drop for 16 frames and he falls through.
