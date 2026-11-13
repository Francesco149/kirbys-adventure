---
name: cov3-a-cannon
start: cov-abilities-fireball@57101
reference: forbidden
steps:
  - Fireball Kirby back in 4-3's first room: room == 248 and ability == 4
  - the fuse is lit (the type $0B object in slot 10 leaves the rope's top end at X 316): room == 248 and ram[0x6128+10] == 11 and ram[0x6086+10]*256 + ram[0x6074+10] < 310
  - the spark reached the cannon ($07DB set) while Kirby sat in it: room == 248 and ram[0x07DB] != 0 and ram[0x6129] == 255
  - shot into the 1-Up room: room == 249
  - 1-Up taken: room == 249 and lives == 5
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov3, unit en23): the fuse cannon of 4-3. From the end of cov-abilities-fireball (4-5's last room,
Fireball copied), clear 4-5, go back into 4-3 from the World 4 hub, light the fuse at the top of the rope with a
Fireball dash, sit in the cannon's opening while the spark runs along the rope, and get fired to the 1-Up room.
