---
name: cov3-a-wizard
start: main:8-wizard-fight
reference: forbidden
steps:
  - the last boss's second form fight with the Star Rod: room == 16 and world == 7 and ability == 24 and ram[0x6128+9] == 78
  - a Star Rod shot (variable 3 = 13) is turned back by a hurting part (variable 0 cleared, Y velocity high byte 255): room == 16 and ((ram[0x6128+6] < 128 and ram[0x6200+6] == 13 and ram[0x61CA+6] == 0 and ram[0x6116+6] == 255) or (ram[0x6128+7] < 128 and ram[0x6200+7] == 13 and ram[0x61CA+7] == 0 and ram[0x6116+7] == 255) or (ram[0x6128+8] < 128 and ram[0x6200+8] == 13 and ram[0x61CA+8] == 0 and ram[0x6116+8] == 255))
forbid:
  - lost a life: lives < 8
  - hit: hp < 39
---
Coverage movie (cov3, unit en29): the Nightmare Wizard fight. Kirby flies up beside the wizard and fires the Star
Rod into one of its hurting parts, which turns the shot back (e62_reflect's turn, 29:BD65), something no corpus
movie did.
