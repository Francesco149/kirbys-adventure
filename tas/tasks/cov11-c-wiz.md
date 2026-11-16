---
name: cov11-c-wiz
start: main@134756
reference: forbidden
steps:
  - the last boss's second form (type $4E, slot 9) fights in room 16 with Star Rod Kirby: room == 16 and ram[0x6128+9] == 0x4E and ability == 24
  - Kirby only dodges, so the fight goes on through nine placements (variable 5 = 9; main had 7): room == 16 and ram[0x6128+9] == 0x4E and ram[0x6224+9] == 9
  - the tenth placement takes variable 5 back to 0 (e4e_place, 29:B6F2): room == 16 and ram[0x6128+9] == 0x4E and ram[0x6224+9] == 0 and ram[0x61CA+9] == 60
  - and the next placement counts on from 1: room == 16 and ram[0x6128+9] == 0x4E and ram[0x6224+9] == 1
forbid:
  - lost a life: lives < 8
  - hurt more than twice: hp < 23
---
Coverage movie (batch 11, part C; unit en29). e4e_place counts the boss's placements in variable 5 and goes back to 0
at 10 (29:B6F2-29:B6F6); main beats him after 7 placements and no movie lasted longer. Here Kirby (Star Rod) does not
attack at all and dodges for ~5,000 frames (two hits taken), so the boss places himself ten times and more, reading
e4e_order[0] again after the wrap.
