---
name: cov3-b-frosty
start: main@8230
reference: forbidden
steps:
  - Mr. Frosty (type $48) is in slot 10 of room 57: room == 57 and ram[0x6132] == 0x48
  - it charges (e48_tick_charge 25.B7D1): ram[0x6132] == 0x48 and ram[0x629A]*256 + ram[0x6288] == 0xB7D1
  - after the charge it decides from row 4 of e48_choice (variable 6 = 3 or 4 after a decision in row 4): ram[0x6132] == 0x48 and ram[0x6240] == 3 and ram[0x629A]*256 + ram[0x6288] == 0xB8BF
  - backing away for a charge it meets the wall (tick 25.B839, entry 0x0F of e48_scripts): ram[0x6132] == 0x48 and ram[0x629A]*256 + ram[0x6288] == 0xB839
  - then the ticks 25.B85B and 25.B899: ram[0x6132] == 0x48 and ram[0x629A]*256 + ram[0x6288] == 0xB899
  - at the swing its block is within reach (tick 25.B953 of the script 25.B5D0): ram[0x6132] == 0x48 and ram[0x629A]*256 + ram[0x6288] == 0xB953
  - at a swing Kirby is 30 pixels or more above it (the script 25.B5AB): ram[0x6132] == 0x48 and ram[0x63A0 + ram[0x6156]]*256 + ram[0x6380 + ram[0x6156]] >= 0xB5AB and ram[0x63A0 + ram[0x6156]]*256 + ram[0x6380 + ram[0x6156]] < 0xB5D0
  - it is hit in the air during a hop (e48_hit_air): ram[0x6132] == 0x48 and ram[0x629A]*256 + ram[0x6288] == 0xB8BF and ram[0x61D4] < 20
forbid:
  - lost a life: lives < 4
---
Coverage movie (unit en25b). Mr. Frosty's arena in room 57. Kirby keeps out of its way for a long time without
hurting it, so that it charges (once in the corpus before), decides after a charge, backs into a wall, swings its
block when the block is close and when Kirby floats high above it; at the end Kirby spits a star at it during a hop.
