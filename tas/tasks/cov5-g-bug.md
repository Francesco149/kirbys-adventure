---
name: cov5-g-bug
start: main@31540
reference: forbidden
steps:
  - in World 3's Bugzzy room 210 Select drops main's UFO, Kirby is in normal form: room == 210 and ram[0x5E0] == 0 and ram[0x6128+9] == 0x4A
  - Bugzzy (type $4A, slot 9) flies (tick e4a_tick_fly 29.A4CA) with Kirby less than 32 pixels away in X: room == 210 and ram[0x6290+9]*256 + ram[0x627E+9] == 0xA4CA and abs(x - (ram[0x6086+9]*256 + ram[0x6074+9])) < 32
  - later, after a grab that threw Kirby (hurt), Bugzzy leaps (tick e4a_tick_leap 29.A4DA): room == 210 and ram[0x6290+9]*256 + ram[0x627E+9] == 0xA4DA and hp < 47
forbid:
  - lost a life: lives < 4
  - dying: hp > 47
---
Coverage movie (cov5, unit en29 / boss_cov4). Main fights World 3's Bugzzy with the UFO; here Kirby drops it with
Select and fights in normal form, inhaling and spitting. e4a_fly_pick answers 0 (Kirby less than $20 pixels away in X,
29:A466) when Bugzzy takes off, and a grab's e4a_throw_dir reaches its path 29:A388 (with blocks in front, a value
of e4a_throw_dirs that differs from variable 4).
