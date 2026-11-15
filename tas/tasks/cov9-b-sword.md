---
name: cov9-b-sword
start: main@65600
reference: forbidden
steps:
  - Sword Kirby in 5-2's room $11C: ram[0x55F]*256 + ram[0x55E] == 0x11C and ability == 3
  - with the Sword, in the room of the hammer ape (room $11B, type $4C in slot 10): ram[0x55F]*256 + ram[0x55E] == 0x11B and ability == 3 and ram[0x6128+10] == 76
  - its bar filled (hit points above 0): ram[0x55F]*256 + ram[0x55E] == 0x11B and ram[0x6128+10] == 76 and ram[0x61D4] > 0
  - the ape beaten with the Sword (its hit points 0): ram[0x55F]*256 + ram[0x55E] == 0x11B and ability == 3 and ram[0x6128+10] == 76 and ram[0x61D4] == 0
  - out by its door into the lower half of room $11C, the Sword kept: ram[0x55F]*256 + ram[0x55E] == 0x11C and ability == 3 and y > 250
  - on the outside of room $11A (Kirby left of x 120, low): ram[0x55F]*256 + ram[0x55E] == 0x11A and ability == 3 and x < 120 and y > 330
  - Down on the thin block at the bottom left (property $0E): script $6C, routine kirby_st_sword_drop (15:A56C): ram[0x55F]*256 + ram[0x55E] == 0x11A and ability == 3 and ram[0x6291]*256 + ram[0x627F] == 0xA56C
  - he falls through it: ram[0x55F]*256 + ram[0x55E] == 0x11A and y > 375
forbid:
  - lost a life before the drop: lives < 5
---
Coverage movie (cov9, unit dead_kirby): Sword Kirby drops through a thin floor. From main@65600 (5-2, Sword copied,
room $11C) Kirby takes the ladder rooms ($118, $117, $119, $11A) to the hammer ape's room $11B, beats it with the
Sword and slashes its body away (it lies in front of the door), goes out by the new door to the lower half of room
$11C and by its door (200, 329) to the outside of room $11A, floats over the hill to the left and lands on the single
thin block at (80-95, 368) where the 1-Up sits (lives 5 -> 6), ducks and holds Down: kirby_st_sword_crouch's
down_bit5_test answers carry and script $6C runs kirby_st_sword_drop. The block is the bottom row of the room: Kirby
falls out of it and loses that life (the movie ends as he falls; lives are back to 5 after it).
