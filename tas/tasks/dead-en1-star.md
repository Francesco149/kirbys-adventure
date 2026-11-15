---
name: dead-en1-star
start: main@26560
reference: forbidden
steps:
  - in world 1's hub (room 1, LEVEL 2) with worlds 0 and 1 done (world_flag_bits = 3): room == 1 and world == 1 and ram[0x07DC] == 3
  - through the hub's door of kind $1D (cell 5, position $82, pixel 648, 233) into the Warp Star Station of world 1: room == 31
  - the star of world 0 (type $06, variable 0 = 1) stands in it: room == 31 and ram[0x6128+11] == 6 and ram[0x61CA+11] == 1 and ram[0x0784+11] == 0
  - Kirby rides it to world 0's Warp Star Station (room $1E): room == 30 and world == 0
forbid:
  - lost a life: lives < 4
---
Coverage movie for unit dead_en1 (the star rooms, 23:ADAB e06_world_star and its routines 23:AE53-23:B05B, the arrival
23:BD35 / e06_arrive_80_pose). Every hub room 0-6 has a door of kind $1D into a room $1E-$24, the Warp Star Station of
that world; door_find refuses it only while world_flag_bits holds the current world's bit alone. No movie went in
(w12-sonnet and w2-seq pressed Up at world 0's door with only world 0 done, and were refused). From main in world 1's
hub with the first two worlds done: walk to the door (648, 233), Up, A past the station's message, walk left onto
the star numbered 1 and ride it to the station of world 0. World numbers are the game's index 0-6 (LEVEL 1-7).
