---
name: cov10-c-noddy
start: main@115060
reference: forbidden
steps:
  - in room 144 UFO Kirby hovers above the right part of the floor where the Noddy of class 1 (kind $32, slot 11, obj_param $078F = 1) walks: room == 144 and ram[0x6128+11] == 0x2E and ram[0x078F] == 1 and x >= 840
  - the class-1 Noddy falls asleep (tick routine e2e_tick_sleep 25:AC23, variable 3 = 1): its sleep runs the class test at 25:AC47: room == 144 and ram[0x6128+11] == 0x2E and ram[0x629C-1]*256 + ram[0x628A-1] == 0xAC23 and ram[0x620B] == 1
  - it wakes on its own and walks again (e2e_tick_walk 25:ABEB): room == 144 and ram[0x6128+11] == 0x2E and ram[0x629C-1]*256 + ram[0x628A-1] == 0xABEB and frame > 116300
forbid:
  - lost a life: lives < 8
  - hurt: hp < 31
---
Coverage movie (batch 10, part C; unit en25b). Every Noddy (type $2E) that slept in the corpus was of class 0, so
e2e_tick_sleep's test of obj_param at 25:AC42 always went to the return. In room 144 one Noddy is of class 1 (kind
$32). UFO Kirby flies over to it and waits out of its reach; it walks, falls asleep, and each frame of its sleep takes
the class-1 path (25:AC47: variable 3 is not 0, return). The distance test behind it (25:AC4C-25:AC5E) stays
unreached and is dead: the sleep sets variable 3 = 1 and variable 2 = $E0, and the frame variable 2 reaches 0 also
takes variable 3 to 0 and wakes it at 25:AC3D, so variable 3 is never 0 while variable 2 is not.
