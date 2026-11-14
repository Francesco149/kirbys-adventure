---
name: cov4-a-wiz
start: main@135120
reference: forbidden
steps:
  - the last boss's second form (type $4E, slot 9) with the Star Rod: room == 16 and ability == 24 and ram[0x6128+9] == 78
  - it starts a swoop (tick routine e4e_tick_swoop, 29 B5AA) facing right, Kirby in the right half of the screen: room == 16 and ram[0x6287] == 0xAA and ram[0x6299] == 0xB5 and ram[0x61E5] == 0x40
  - the fight still on at frame 136,500: room == 16 and ram[0x6128+9] == 78 and frame >= 136500
forbid:
  - lost a life: lives < 8
---
Coverage movie (cov4, unit en29): the Nightmare wizard fight from main's frame 135,120. Kirby flies into the right
half of the screen before the wizard's first swoop, so e4e_face_side turns it right (29:B77A); then he keeps away
from it without firing for about 1,300 frames (a second swoop, more placements by e4e_place).
