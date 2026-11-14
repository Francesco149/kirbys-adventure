---
name: cov4-a-ddd
start: cov3-c-dedede@130111
reference: forbidden
steps:
  - back in the 7-7 ring with full HP after the lost life, King Dedede in slot 10: room == 14 and hp == 47 and lives == 7 and ram[0x6128+10] == 71
  - his inhale (tick routine e47_tick_inhale, 2D A90B) catches Kirby on his right: room == 14 and ram[0x6288] == 0x0B and ram[0x629A] == 0xA9 and ram[0x621C] != 0 and x > ram[0x6090]*256 + ram[0x607E]
  - Kirby is spat out and hurt: room == 14 and hp == 39 and lives == 7
  - Dedede is beaten facing right with Kirby on his right: room == 14 and ram[0x6128+10] == 71 and ram[0x61D4] == 0 and ram[0x61E6] < 0x80 and x > ram[0x6090]*256 + ram[0x607E]
  - the stage is cleared: world == 7 and trans == 5
forbid:
  - lost another life: lives < 7
---
Coverage movie (cov4, unit en2d / boss_cov3 / en_more): King Dedede (type $47) in the 7-7 ring. It continues the
previous batch's movie after its lost life: Kirby comes back from the hub with full HP, is inhaled from Dedede's
right side (e47_pull_vel pulling him leftward), swallowed in the right half of the screen (e47_face_in 2D:A9C6) and
spat out to the left (e47_star_place facing left, 2D:B0E2), then beats him with spat stars over about 3,000 frames
(so e47_tick_think counts six actions, 2D:AD9A) and lands the last star from his right, so that the beaten boss
faces right next to Kirby (e47_tick_end 2D:AF76 and the end of the fight).
