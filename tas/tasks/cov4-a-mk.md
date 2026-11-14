---
name: cov4-a-mk
start: cov3-b-mk:sword
reference: forbidden
steps:
  - the duel is on with the sword: room == 108 and ability == 3 and ram[0x6134] == 0x42
  - the boss shrugs a sword hit off ($0788 = 2): room == 108 and ram[0x0788] == 2 and ram[0x05E1] != 7
  - Kirby slides into the boss while it blinks after a hit: room == 108 and ram[0x05E1] == 7 and ram[0x078B] > 2 and abs(x - (ram[0x6092]*256 + ram[0x6080])) < 12
  - a slide answered by the boss's counter ($0788 = 2 while sliding): room == 108 and ram[0x0788] == 2 and ram[0x05E1] == 7 and abs(x - (ram[0x6092]*256 + ram[0x6080])) < 16
  - the boss is beaten with Kirby in the middle third of the screen: room == 108 and ram[0x6134] == 0x42 and ram[0x61D6] == 0 and x >= 100 and x <= 155
forbid:
  - lost a life: lives < 5
---
Coverage movie (cov4, unit en2b): Meta Knight's duel in room 108 (6-7), from the previous batch's checkpoint with
the sword in hand. The boss shrugs off a sword hit (e42_hurt 2B:B095, $0788 = 2 and the record 39:8864), Kirby
slides into it (kirby_rect kind 1: e42_hit's reaction 3 at 2B:B021, one slide thrown back by kirby_knock_back, one
answered by the counter at 2B:B056), slides into it while it blinks after a hit (2B:AFA7), and beats it standing in
the middle third of the screen, so the falling boss hops toward a point $30 / $D0 (e42_hop_center 2B:B778).
