---
name: cov4-e-fire
start: w12-sonnet@2100
reference: forbidden
steps:
  - Kirby inhales the Hot Head of room 43 (type $29) and swallows it, so he has Fire: room == 43 and ability == 0
  - he goes left until its place is off the screen and comes back; the Hot Head (slot 14) is there again and starts an attack (its script waits, tick 3E.D786, after it has walked from its place at X 949) while Kirby has Fire: room == 43 and ability == 0 and ram[0x6086+14]*256 + ram[0x6074+14] < 930 and ram[0x6128+14] == 0x29 and ram[0x6290+14]*256 + ram[0x627E+14] == 0xD786
  - e29_tick_still sees kirby_ability = 0 and starts e29_walk again (tick 24.B809, variable 2 = $5A): room == 43 and ability == 0 and ram[0x6128+14] == 0x29 and ram[0x6290+14]*256 + ram[0x627E+14] == 0xB809 and ram[0x61EE+14] >= 0x58
forbid:
  - lost a life: lives < 4
  - Kirby hit: hp < 47
---
Coverage movie (cov4, unit en24c). Type $29 (Hot Head) gives Fire. Kirby takes Fire from the Hot Head of 1-1's first
room, walks left until it is off the screen, comes back and keeps out of its way while the new one walks. Each time
its timer starts an attack (e29_attack), e29_tick_still finds kirby_ability = 0 on its first frame and sets the script
e29_walk (24:B8A2 taken, 24:B8B1-B8B5): it does not attack a Kirby who has its ability. No corpus movie had a Hot Head
attack while Kirby had Fire.
