---
name: cov4-b-ufo
start: main@43605
reference: forbidden
steps:
  - the saucer (type $28, the UFO enemy) in slot 12 of room 238 has its count of dashes (variable 5) at 4: room == 238 and ram[0x6128+12] == 0x28 and ram[0x6230] == 4
  - after the fourth dash its count goes back to 0 (28.AA3F) and it goes on: room == 238 and ram[0x6128+12] == 0x28 and ram[0x6230] == 0
forbid:
  - lost a life: lives < 4
  - the saucer is gone: ram[0x6128+12] != 0x28
---
Coverage movie (cov4, unit en28). In every corpus movie the saucer was inhaled, beaten or left the screen within
three dashes. Here Kirby keeps away from it in room 238 so that it lives on: at the fourth pick e28_tick_pick takes
the point beside Kirby (28:A9F9-AA07) and the end of that dash resets the count and starts 28:A963 (28:AA3F).
