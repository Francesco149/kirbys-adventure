---
name: cov4-b-poppy
start: w1-v2-sonnet@11170
reference: forbidden
steps:
  - the beaten Poppy Bros. Sr. (type $22 in slot 9) lies trembling in room 49 (tick e22_tick_fade 27.A353): room == 49 and ram[0x6128+9] == 0x22 and ram[0x6299]*256 + ram[0x6287] == 0xA353
  - Kirby leaves it alone until its count runs out and it bursts (slot 9 freed): room == 49 and ram[0x6128+9] != 0x22
forbid:
  - lost a life: lives < 3
---
Coverage movie (cov4, unit en27). In w1-v2-sonnet Kirby inhaled the beaten mid-boss while it lay trembling. Here he
stays away: variable 2 of e22_tick_fade counts down to 0 and the script becomes bank 22's burst (27:A372-A37F).
