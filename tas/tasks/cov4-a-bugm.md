---
name: cov4-a-bugm
start: w3-sonnet@59546
reference: forbidden
steps:
  - the beetle mid-boss (type $4A) in slot 9 of room 210, Kirby in his normal form: room == 210 and ram[0x6128+9] == 74 and ram[0x05E0] == 0
  - Kirby has something in his mouth (kirby_form 1): room == 210 and ram[0x05E0] == 1 and ram[0x6128+9] == 74
  - the beetle grabs him with his mouth full (Kirby's tick routine e4a_held_tick at 29 B096): room == 210 and ram[0x627F] == 0x96 and ram[0x6291] == 0xB0 and ram[0x05E0] == 1
  - after the slam Kirby spits and floats: room == 210 and ram[0x05E1] == 13 and ram[0x6128+9] == 74
  - the fight still on at frame 61,000: room == 210 and ram[0x6128+9] == 74 and frame >= 61000
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov4, unit en29): the beetle mid-boss of world 3 from the w3-sonnet playthrough (main's Kirby is in
another form there). Kirby inhales one of its bugs and keeps it in his mouth (kirby_form 1), so the grab takes the
other grip pose (e4a_grip_pose 29:AEC6) and the throw the other pose; he jumps and floats while it picks its attacks
(e4a_pick: kirby_action 4/5 and $0D, 29:A3E4 and 29:A3D3).
