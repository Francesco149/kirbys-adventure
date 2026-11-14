---
name: cov4-c-para
start: cov2-water-parasol:in
reference: forbidden
steps:
  - Parasol Kirby on the first ladder of 2-3's cave: room == 179 and ability == 9 and ram[0x6291]*256 + ram[0x627F] == 0xB362
  - through the half-flooded door to the next room with the Parasol: room == 181 and ability == 9
  - puffed up on the water of room 181 (the hover's water exit): room == 181 and ram[0x6291]*256 + ram[0x627F] == 0xB55F
  - back in the cave through the door at the ledge: room == 179 and ability == 9 and frame > 24800
  - the Parasol dropped with Select and swallowed again on the platform: room == 179 and ability == 9 and y < 260 and frame > 25330
  - dropped once more, swimming: room == 179 and ability == 255 and frame > 26200
forbid:
  - lost a life: lives < 3
---
Coverage movie for the exits of Parasol Kirby's states (bank 15, units kst15, kst_rest, kst_abl, kst_cov3) that
no movie had taken. From the cov2-water-parasol checkpoint in 2-3's cave (room 179): the ladder taken from the
stand, the walk, the run, the turn, the rise, the fall and the dive, and left sideways; a walk into a wall, Up
during a walk and a bounce (puff), A and B during a run, Down and A during a turn, B during the rise; the door
from a fall into room 181 (fall into water from the float, a walk off an underwater ledge, a stroke while walking
under water, the hover, the flap and the exhale ending in the water, B during the float, a run off a ledge, the
door from a stand back to room 179); then on the platform above the shallow channel Select during the run, the
fall, the float and the dive (the star swallowed again each time), Up during a dive, a run off the platform, and
last Select while swimming (the star is lost in the water).
