---
name: cov4-e-sit
start: main@124925
reference: forbidden
steps:
  - the sitting type $1E (variant 6, slot 11) of room 154 starts its hop (tick e1e_tick_hop 26.A427): room == 154 and ram[0x6128+11] == 0x1E and ram[0x6290+11]*256 + ram[0x627E+11] == 0xA427
  - Kirby leaves it alone and it lands, so e1e_scripts entry 0 makes it sit again (tick e1e_tick_sit 26.A446): room == 154 and ram[0x6128+11] == 0x1E and ram[0x6290+11]*256 + ram[0x627E+11] == 0xA446 and frame > 125000
  - and it hops once more: room == 154 and ram[0x6128+11] == 0x1E and ram[0x6290+11]*256 + ram[0x627E+11] == 0xA427 and frame > 125100
forbid:
  - lost a life: lives < 8
  - Kirby hit: hp < 7
---
Coverage movie (cov4, unit en26b). In main the sitter of variant 6 (type $1E, room 154) was gone before its slow hop
ended. Here main's Kirby (the UFO, 7 hit points) stops left of it and waits: the hop lands (e1e_tick_hop's landing,
26:A438-A43A, and e1e_set_script, 26:A469-A479), the script e1e_sit starts again and it hops a second time.
