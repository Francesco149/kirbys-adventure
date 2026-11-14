---
name: cov5-h-sw
start: cov4-c-sword@65590
reference: forbidden
steps:
  - Sword Kirby floating on the water of 5-2's flooded tunnel: room == 23 and ability == 3 and ram[0x6291]*256 + ram[0x627F] == 0xA9C4
  - B there, into the water: room == 23 and ability == 3 and ram[0x6291]*256 + ram[0x627F] == 0xAA25
  - swimming with the Sword: room == 23 and ability == 3 and ram[0x6291]*256 + ram[0x627F] == 0xABA5
  - Select while swimming, the Sword dropped: room == 23 and ability == 255 and frame < 65700
  - the Sword inhaled and swallowed again: room == 23 and ability == 3 and frame > 65700
  - walking under water with it: room == 23 and ability == 3 and ram[0x6291]*256 + ram[0x627F] == 0xAAF7
  - Select while walking under water, dropped again: room == 23 and ability == 255 and frame > 65900
forbid:
  - lost a life: lives < 5
---
Coverage movie for the pad exits of Sword Kirby's water states (bank 15, units kst_cov4, kst15) in 5-2's flooded
tunnel (room 23) from cov4-c-sword: B new while floating on the water (kirby_st_sword_float_water, script $76),
Select while swimming (kirby_st_sword_swim, pad_select_drop) and, after the Sword is inhaled and swallowed again,
Select while walking on the bottom (kirby_st_sword_wade).
