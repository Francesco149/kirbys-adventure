---
name: cov3-a-turtle
start: main@53085
reference: forbidden
steps:
  - the rolling armoured mid-boss (type $4B) in its room: room == 2 and world == 3 and ram[0x6128+10] == 75
  - it grabs Kirby (Kirby's tick routine is e4a_held_tick at 29 B096): room == 2 and ram[0x627F] == 0x96 and ram[0x6291] == 0xB0
  - Kirby thrown off, hurt once, and free again: room == 2 and hp == 31 and ram[0x6291] != 0xB0
  - the fight still on with the boss alive about 1,100 frames in: room == 2 and ram[0x6128+10] == 75 and frame >= 54200
forbid:
  - lost a life: lives < 4
  - more than one hit: hp < 31
---
Coverage movie (cov3, unit en29): the mid-boss of 4-4 (type $4B, rolling armour). UFO Kirby flies into it and is
grabbed and rolled around (e4b_touch, the script 29:A895), loses UFO when thrown, then dodges without attacking
for about 700 frames so the boss runs its other attacks (e4b_pick's 1-3).
