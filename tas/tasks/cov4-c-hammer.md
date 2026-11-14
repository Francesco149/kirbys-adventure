---
name: cov4-c-hammer
start: main@90705
reference: forbidden
steps:
  - the UFO given up with Select beside the beaten Bonkers in 6-3's ship: room == 75 and ram[0x5E0] == 0 and ability == 255
  - the Hammer swallowed from the beaten Bonkers: room == 75 and ability == 8
  - Hammer Kirby on the ladder by the crates: room == 75 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB23E
  - the Hammer dropped with Select: room == 75 and ability == 255 and frame > 93400
  - the Hammer swallowed again: room == 75 and ability == 8 and frame > 93450
  - through the lower left door to the shore with the Hammer: room == 74 and ability == 8
  - back in the ship's room at the end: room == 75 and ability == 8 and frame > 95300
forbid:
  - lost a life: lives < 6
---
Coverage movie for the exits of Hammer Kirby's states (bank 17, units kst_cov3 and kst_abl) that no movie had
taken: until now the Hammer was played only in the Heavy Mole's tunnel. From main in 6-3 (room 75) just after the
UFO beat Bonkers: Select gives the UFO up, Kirby swallows the beaten Bonkers and has the Hammer. Then: B, Down
and Up during a walk, A, B, Down and Up during a run, B during the rise, the ladder from the stand, a walk, a
run, the rise and a fall, a walk and a run off the crate ledge, runs and walks into the wall, A and B during the
skid, Select during the walk, the run and the fall (the star swallowed again each time), and the lower left door
to room 74 and back from a walk, a stand, the rise, a flap and a fall (HP stays at 7, one hit from death).
