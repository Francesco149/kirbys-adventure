---
name: cov4-a-bug7
start: main@112380
reference: forbidden
steps:
  - the world-7 beetle (type $4A, obj_param 1) in slot 11 of room 137: room == 137 and ram[0x6128+11] == 74
  - it grabs Kirby while facing right (Kirby's tick routine e4a_held_tick at 29 B096): room == 137 and ram[0x627F] == 0x96 and ram[0x6291] == 0xB0 and ram[0x61E7] < 0x80
  - free again, the fight still on 1,500 frames later: room == 137 and ram[0x6128+11] == 74 and ram[0x6291] != 0xB0 and frame >= 114300
  - a second grab facing right: room == 137 and ram[0x627F] == 0x96 and ram[0x6291] == 0xB0 and ram[0x61E7] < 0x80
forbid:
  - lost a life: lives < 6
---
Coverage movie (cov4, unit en29): the beetle mid-boss of world 7 (room 137, obj_param 1), from main's frame where
the fight is on. It grabs Kirby from its right side twice (e4a_grab_test facing right, e4a_throw_dir probing ahead
of a beetle that faces right, and its random throws), and in between Kirby keeps away from it for about 1,400
frames so that it summons its bugs (e4a_bug_fly with obj_param 1) and leaps (e4a_leaps with obj_param 1).
