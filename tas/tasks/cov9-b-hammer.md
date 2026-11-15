---
name: cov9-b-hammer
start: cov9-b-sword@68303
reference: forbidden
steps:
  - in the hammer ape's room ($11B) with the ape beaten (type $4C in slot 10, hit points 0), the Sword dropped with Select: ram[0x55F]*256 + ram[0x55E] == 0x11B and ability == 255 and ram[0x6128+10] == 76 and ram[0x61D4] == 0
  - the beaten ape swallowed: Hammer: ram[0x55F]*256 + ram[0x55E] == 0x11B and ability == 8
  - out by its door into the lower half of room $11C: ram[0x55F]*256 + ram[0x55E] == 0x11C and ability == 8 and y > 250
  - on the outside of room $11A, left and low: ram[0x55F]*256 + ram[0x55E] == 0x11A and ability == 8 and x < 120 and y > 330
  - Down on the thin block at the bottom left (property $0E): script $A3, routine kirby_st_hammer_drop (17:B13E): ram[0x55F]*256 + ram[0x55E] == 0x11A and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB13E
  - he falls through it: ram[0x55F]*256 + ram[0x55E] == 0x11A and y > 375
forbid:
  - lost a life before the drop: lives < 5
---
Coverage movie (cov9, unit dead_kirby): Hammer Kirby drops through a thin floor. A branch of cov9-b-sword at frame
68303 (5-2, the hammer ape just beaten with the Sword): Select drops the Sword, Kirby swallows the beaten ape (Hammer),
goes out by the new door to the lower half of room $11C, by its door (200, 329) to the outside of room $11A, floats
over the hill to the single thin block at the bottom left (the 1-Up there: lives 5 -> 6), ducks and holds Down:
kirby_st_hammer_duck's down_bit5_test answers carry, script $A3 runs kirby_st_hammer_drop, and he falls out of the
bottom of the room (the movie ends as he falls).
