---
name: cov3-b-e4d
start: main:7-2-room139
reference: forbidden
steps:
  - the mid-boss of type $4D is in slot 11 of room 139 with 27 hit points: room == 139 and ram[0x6133] == 0x4D and ram[0x61D5] == 27
  - it catches Kirby (state 8 in the low bits of variable 9): ram[0x6133] == 0x4D and (ram[0x6277] % 16) == 8
  - state 3: ram[0x6133] == 0x4D and (ram[0x6277] % 16) == 3
  - state 4: ram[0x6133] == 0x4D and (ram[0x6277] % 16) == 4
  - state 9: ram[0x6133] == 0x4D and (ram[0x6277] % 16) == 9
  - state 5: ram[0x6133] == 0x4D and (ram[0x6277] % 16) == 5
forbid:
  - lost a life: lives < 6
  - the mid-boss was hurt: ram[0x6133] == 0x4D and ram[0x61D5] < 27
---
Coverage movie (unit en2a). The mid-boss of type $4D in room 139 (7-2) ran only once in the corpus and was beaten
in its first lunge. Here Kirby never hurts it and dodges it for about 1,700 frames, so that it goes through its
other states: it catches and throws Kirby (state 8) and runs the states 3, 4, 9 and 5 of e4d_next.
