---
name: cov5-i-wheel
start: main@15190
reference: forbidden
steps:
  - in room 176 Kirby waits on the hill; Grand Wheelie (type $49, slot 14) rolls left at him, hits the hill's side and hops back (tick e49_tick_hop_back, 2A:ACA7): room == 176 and ram[0x6128+14] == 0x49 and ram[0x6290+14]*256 + ram[0x627E+14] == 0xACA7 and hp == 47
  - the hop back lands (variable 5 + 1): room == 176 and ram[0x6290+14]*256 + ram[0x627E+14] == 0xACA7 and ram[0x6224+14] == 1 and ram[0x60AA+14]*256 + ram[0x6098+14] == 145
  - Kirby spits his mouthful at it and it lies down beaten (tick e49_tick_down, 2A:AE20): room == 176 and ram[0x6128+14] == 0x49 and ram[0x6290+14]*256 + ram[0x627E+14] == 0xAE20
  - Kirby leaves it lying until its time runs out and it is gone, not inhaled: room == 176 and ram[0x6128+14] >= 0x80 and inh == 3
forbid:
  - lost a life: lives < 4
  - dying: hp > 47
---
Coverage movie (cov5, unit en2a / boss_cov3). Main inhales Grand Wheelie in World 2 (room 176) right away. Here Kirby
(keeping main's mouthful) waits on top of the hill to the left, so the Wheelie rolls left into the hill's side:
e49_tick_run's wall path with a negative X velocity (2A:AC08: obj_dir $C0) and e49_hop_back, whose landings run
(2A:ACB6-ACC8: variable 5 + 1, obj_dir $40, velocity 0; with e49_fall_var6's paths 2A:ACD9-AD08). Then Kirby goes
down to the floor, dodges a few of its rolls (one hit, 47 -> 39; their braking runs e49_tick_brake 2A:AD46-AD57) and spits the mouthful at it: it lies
down, and as Kirby does not inhale it, e49_tick_down's variable 6 runs out (2A:AE2A-AE35: the script 22:8162).
