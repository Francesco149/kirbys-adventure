---
name: cov11-d-mole
start: main@81284
reference: forbidden
steps:
  - in Heavy Mole's tunnel (room 12) Kirby has dropped the UFO and slides (kirby_rect kind 1) on the floor beside the boss: room == 12 and ram[0x05E1] == 7 and ram[0x0501] == 1 and ram[0x6128+12] == 0x46 and abs(ram[0x6086+12]*256 + ram[0x6074+12] - x) < 30
  - the slide's reaction knocks him back up and left (kirby_knock_back from e46_hit's 2C:AFFA, via the body's kind-1 reaction and the claw's 2C:B839) without damage: room == 12 and ram[0x05E1] == 5 and vx <= -300 and vy <= -500 and hp == 23 and frame > 81466
forbid:
  - lost a life: lives < 6
  - hurt: hp < 23
---
Coverage movie (batch 11, part D; unit en2c). main fights Heavy Mole as UFO Kirby, who cannot slide. Here Kirby
drops the UFO with Select, follows the mole along its tunnel and slides into it while the boss is level with the
floor: on the same frame the body's record 39:959C answers the slide (kind 1: variable 5 = $FF, 2C:AFBB taken) and the
lower claw's record 39:95CC does too (variable 7 = $FF, 2C:B839 falls through): both run kirby_knock_back (2C:AFFA,
2C:B83B), and Kirby bounces back without losing health. The blink case (2C:AF83 taken, a slide within 30 frames of a
damaging hit) was not reached: after a spat star hit the boss had dug on ~40 px away, and the slide ends at the
ledge of the pit it digs.
