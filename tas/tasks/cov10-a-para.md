---
name: cov10-a-para
start: cov9-b-para@12650
reference: forbidden
steps:
  - Parasol Kirby running (kirby_st_para_run) on the side door of 2-1's first room at (584, 137): room == 169 and ability == 9 and ram[0x6291]*256 + ram[0x627F] == 0xAE1D and abs(x - 584) <= 5
  - Up there takes the door into the grotto: room == 171 and ability == 9
  - back, skidding to a turn (kirby_st_para_turn) on the door: room == 169 and ability == 9 and ram[0x6291]*256 + ram[0x627F] == 0xAEB9 and abs(x - 584) <= 5
  - Up there takes the door: room == 171 and ability == 9
  - back, floating down under the Parasol (kirby_st_para_float) onto the door: room == 169 and ability == 9 and ram[0x6291]*256 + ram[0x627F] == 0xB068 and abs(x - 584) <= 6 and y >= 129
  - Up there takes the door: room == 171 and ability == 9
  - back, puffing up (kirby_st_para_puff) on the door: room == 169 and ability == 9 and ram[0x6291]*256 + ram[0x627F] == 0xB46E and abs(x - 584) <= 6 and y >= 129
  - Up there takes the door: room == 171 and ability == 9
  - back, the Parasol's dive (kirby_st_para_dive) onto the door: room == 169 and ability == 9 and ram[0x6291]*256 + ram[0x627F] == 0xB131 and abs(x - 584) <= 6 and y >= 129
  - Up there takes the door: room == 171 and ability == 9
  - back, the dive bounces off a Waddle Dee (kirby_st_para_dive_hit): room == 169 and ability == 9 and ram[0x6291]*256 + ram[0x627F] == 0xB1B5 and frame < 14040
  - a second bounce: room == 169 and ability == 9 and ram[0x6291]*256 + ram[0x627F] == 0xB1B5 and frame > 14300 and frame < 14370
  - a third bounce: room == 169 and ability == 9 and ram[0x6291]*256 + ram[0x627F] == 0xB1B5 and frame > 14370
  - Select in it drops the Parasol: room == 169 and ability == 255
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov10, units kst15, kst_rest, cov9). From cov9-b-para@12650 (Parasol Kirby in 2-1's first room, room
169), the door exits of the Parasol's states at the side door (584, 137), each followed by the way back from the
grotto (room 171): Up while running (kirby_st_para_run 15:AE80), while skidding to a turn (kirby_st_para_turn
15:AF08), while floating down under the Parasol (kirby_st_para_float 15:B0B8), while puffing up (kirby_st_para_puff
15:B48C) and in the Parasol's dive (kirby_st_para_dive 15:B183). Their door tests come before the tests of Up held,
which is why they can answer. On the way the jump reaches its top (kirby_st_para_jump's kirby_at_top exit
15:AF70). Then three dives onto Waddle Dees and the pad exits of the bounce (kirby_st_para_dive_hit): B (15:B1F7,
script $C5), Up held (15:B215, script $C6) and Select (15:B21F, the Parasol dropped), each pressed after the hit's
four frames of stop.
