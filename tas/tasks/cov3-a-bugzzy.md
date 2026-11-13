---
name: cov3-a-bugzzy
start: main@31545
reference: forbidden
steps:
  - Bugzzy (type $4A) in its room: room == 210 and ram[0x6128+9] == 74
  - Bugzzy grabs Kirby (Kirby's tick routine is e4a_held_tick at 29 B096): room == 210 and ram[0x627F] == 0x96 and ram[0x6291] == 0xB0
  - Kirby slammed and free again, Bugzzy alive: room == 210 and hp == 39 and ram[0x6291] != 0xB0 and ram[0x6128+9] == 74
  - Bugzzy charges (tick routine e4a_tick_charge at 29 A516): room == 210 and ram[0x627E+9] == 0x16 and ram[0x6290+9] == 0xA5
  - the fight still on 1,000 frames in: room == 210 and ram[0x6128+9] == 74 and frame >= 32600
forbid:
  - lost a life: lives < 4
  - more than the slam's damage: hp < 31
---
Coverage movie (cov3, unit en29): the beetle mid-boss Bugzzy (type $4A) of world 3. Kirby walks into it and is
grabbed, held up and slammed (e4a_grab, e4a_held_tick, e4a_throw_kirby), then dodges without attacking for
about 900 frames so the beetle runs its charges (with a wall bounce) and its summoned bugs.
