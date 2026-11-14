---
name: cov4-a-turtle
start: cov2-abilities-throw@53120
reference: forbidden
steps:
  - the 4-4 mid-boss with the round shell (type $4B) in slot 10 of room 2, Kirby with the UFO: room == 2 and ram[0x6128+10] == 75 and ability == 23
  - Kirby drops the UFO and keeps its star in his mouth (kirby_form 1): room == 2 and ram[0x05E0] == 1 and ram[0x05E2] == 23 and ram[0x6128+10] == 75
  - it grabs him with his mouth full (hit_kirby_off set): room == 2 and ram[0x050C] != 0 and ram[0x05E0] == 1 and ram[0x6128+10] == 75
  - a second grab with the turtle facing right: room == 2 and ram[0x050C] != 0 and ram[0x05E0] == 1 and ram[0x61E6] == 0x40 and ram[0x6128+10] == 75
  - the fight still on at frame 53,899: room == 2 and ram[0x6128+10] == 75 and frame >= 53899
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov4, unit boss_cov3 / en29): the 4-4 mid-boss with the round shell, from the cov2-abilities-throw
movie (Kirby has the UFO there). Kirby throws the UFO away, inhales its star and keeps it in his mouth, and is
grabbed twice with his mouth full: the grip poses for kirby_form 1 (e4b_pose_arg 29:ABBE, e4a_grip_pose), the
probe with no wall near (e4b_throw_kind's random answer, 29:AB44), and the second time facing right (the probes
added, 29:AB02; e4b_throw_kirby facing right 29:AD71 / 29:AD88; e4b_kirby_flown 29:B106).
