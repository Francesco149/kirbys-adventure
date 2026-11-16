---
name: cov12-a-hubs
start: cov5-f-del@239523
reference: forbidden
steps:
  - the World 5 hub's Warp Star Station (room 34, never loaded before), entered from the hub (help screen on first entry): room == 34 and (ram[0x055F] & 1) == 0 and world == 4
  - star 6 carries Kirby to World 6's station (room 35, never loaded before): room == 35 and (ram[0x055F] & 1) == 0 and world == 5
  - the World 6 museum (room 29, never loaded before; help screen on first entry): room == 29 and (ram[0x055F] & 1) == 0
  - its Wheelie exhibit inhaled from the low block and swallowed: Wheel: room == 29 and (ram[0x055F] & 1) == 0 and ability == 7
  - the World 6 arena (room 41, never loaded before; help screen on first entry): Fire Lion (script $4D, slot 11) fights: room == 41 and (ram[0x055F] & 1) == 0 and ram[0x6128+11] == 0x4D and ram[0x61CA+11] > 0
  - Fire Lion beaten without Kirby taking a hit: room == 41 and (ram[0x055F] & 1) == 0 and ram[0x6128+11] == 0x4D and ram[0x61CA+11] == 0 and ram[0x6200+11] == 0 and hp == 47
  - back in station 35, star 7 carries Kirby to World 7's station (room 36, never loaded before): room == 36 and (ram[0x055F] & 1) == 0 and world == 6
  - star 3 carries him to World 3's station (room 32, never loaded before): room == 32 and (ram[0x055F] & 1) == 0 and world == 2
  - the World 3 arena (room 38, never loaded before): Grand Wheelie (script $49, slot 10) fights: room == 38 and (ram[0x055F] & 1) == 0 and ram[0x6128+10] == 0x49 and ram[0x61CA+10] > 0
  - Grand Wheelie beaten: room == 38 and (ram[0x055F] & 1) == 0 and ram[0x6128+10] == 0x49 and ram[0x61CA+10] == 0 and ram[0x6200+10] == 0
  - back in station 32, star 4 carries him to World 4's station (room 33, never loaded before): room == 33 and (ram[0x055F] & 1) == 0 and world == 3
  - the World 4 museum (room 27, never loaded before): the Ball exhibit swallowed: room == 27 and (ram[0x055F] & 1) == 0 and ability == 17
  - the World 4 arena (room 39, never loaded before): Bugzzy (script $4A, slot 11) fights: room == 39 and (ram[0x055F] & 1) == 0 and ram[0x6128+11] == 0x4A and ram[0x61CA+11] > 0
  - Bugzzy beaten, inhaled and swallowed: Suplex: room == 39 and (ram[0x055F] & 1) == 0 and ability == 21
  - by the hub's next-world door into the World 5 hub, then its arena (room 40, never loaded before): Bonkers (script $4C, slot 13) fights: room == 40 and (ram[0x055F] & 1) == 0 and ram[0x6128+13] == 0x4C and ram[0x61CA+13] > 0
  - Bonkers beaten: room == 40 and (ram[0x055F] & 1) == 0 and ram[0x6128+13] == 0x4C and ram[0x61CA+13] == 0 and ram[0x6200+13] == 0
  - Bonkers inhaled and swallowed: Hammer: room == 40 and (ram[0x055F] & 1) == 0 and ability == 8
  - back in the World 5 hub with Hammer: room == 4 and (ram[0x055F] & 1) == 0 and world == 4 and ability == 8
forbid:
  - lost a life: lives < 4
---
Coverage movie (batch 12, part A: the hub extras). From cov5-f-del's end on the 100% file (Kirby in the World 5 hub,
every Big Switch pressed), Kirby enters the eleven hub rooms no movie had loaded: the five Warp Star Stations (32-36),
the museums of Worlds 4 and 6 (27, 29) and the arenas of Worlds 3-6 (38-41). He travels mostly by star: a station's
numbered star lands him in the target world's own station (34 -> 35 -> 36 -> 32 -> 33), and the station's exit door
puts him in that hub. The first station, museum and arena each show their help screen once. In the museums he swallows
the exhibits (Wheel in 29, Ball in 27); each arena is one mid-boss fight, all four won: Fire Lion (41, with Wheel, no
hit), Grand Wheelie (38), Bugzzy (39, inhaled after the win: Suplex) and Bonkers (40, inhaled: Hammer); the win drops a
Maxim Tomato, eaten in 38, 39 and 40. Room numbers are 9-bit: the hub doors to stage rooms 260+ share the low byte
($055E) with rooms 4-40, hence the `$055F & 1` tests. About 251,950 frames (over env.parse_spec's 200,000-frame limit,
like cov5-f-sw).
