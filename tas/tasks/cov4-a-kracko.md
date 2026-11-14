---
name: cov4-a-kracko
start: main@59530
reference: forbidden
steps:
  - the cloud boss with the eye (type $3D) in slot 15 of room 11: room == 11 and ram[0x6128+15] == 61
  - it glides to the right at Kirby (state 1, obj_dir $40): room == 11 and ram[0x620F] == 1 and ram[0x61EB] == 0x40
  - the fight still on at frame 60,900: room == 11 and ram[0x6128+15] == 61 and frame >= 60900
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov4, unit en2f): the cloud boss with the eye (Kracko by look) in world 4's boss room, from main's
frame where the fight begins. Kirby stays on the ground under it and on its right, so that it starts glides with
Kirby to its right (e3d_glide_start 2F:A648, and its random axis 2F:A627), Kirby passes it during a glide
(e3d_glide_test, carry set 2F:A573) and Kirby's Y velocity is 0 when it decides to charge (kirby_floor_test1 22:8A68);
about 1,400 frames of its eye phase.
