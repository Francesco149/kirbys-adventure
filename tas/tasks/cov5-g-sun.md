---
name: cov5-g-sun
start: main@41480
reference: forbidden
steps:
  - in the boss room 10 of World 3 Select drops main's UFO, Kirby is in normal form: room == 10 and ram[0x5E0] == 0 and ram[0x6128+10] == 0x45 and ram[0x6128+15] == 0x45
  - Kirby slides (kirby_rect kind 1) into the body on the ground: room == 10 and ram[0x501] == 1 and ((ram[0x60AA+10]*256+ram[0x6098+10] > 140 and abs(ram[0x502]+ram[0x503]*256 - (ram[0x6086+10]*256+ram[0x6074+10])) < 16) or (ram[0x60AA+15]*256+ram[0x6098+15] > 140 and abs(ram[0x502]+ram[0x503]*256 - (ram[0x6086+15]*256+ram[0x6074+15])) < 16))
  - with Kirby at the left edge, the moon's rush (tick 28.B5F5) facing left reaches the left edge of the screen: room == 10 and ((ram[0x6290+10]*256+ram[0x627E+10] == 0xB5F5 and ram[0x6086+10]*256+ram[0x6074+10] < 18) or (ram[0x6290+15]*256+ram[0x627E+15] == 0xB5F5 and ram[0x6086+15]*256+ram[0x6074+15] < 18))
  - the sun's push after its shot (tick 28.B2CC) at the left edge of the screen: room == 10 and ((ram[0x6290+10]*256+ram[0x627E+10] == 0xB2CC and ram[0x6086+10]*256+ram[0x6074+10] < 18) or (ram[0x6290+15]*256+ram[0x627E+15] == 0xB2CC and ram[0x6086+15]*256+ram[0x6074+15] < 18))
forbid:
  - lost a life: lives < 4
  - dying: hp > 47
---
Coverage movie (cov5, unit en28). In every fight of the corpus the ground body's attacks went right (Kirby on its
right) and none reached an edge of the screen. Here main's Kirby drops the UFO with Select at the start of the fight
in room 10 and keeps to the left edge, floating out of the way: e45_hit's kind-1 path (28:B0F0, Kirby's slide into
the body: variable 5 = $FF), the moon's attacks facing left (e45_tick_lunge 28:B5D7, e45_tick_moon_rush 28:B635, and
at the edge 28:B602; e45_tick_moon_arc's edge flip 28:B660), the sun's rush stopped at the edge (28:B434), its push
at the left edge (28:B2E0), and the hop's edge (28:B175). About 3,800 frames of the fight, Kirby down to one bar.
