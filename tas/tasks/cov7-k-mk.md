---
name: cov7-k-mk
start: cov4-a-mk@106700
reference: forbidden
steps:
  - in Meta Knight's duel (room 108) Kirby takes the sword: room == 108 and ability == 3
  - the boss (type $42, slot 12) has its 60 hit points: room == 108 and ram[0x6134] == 0x42 and ram[0x61D6] == 60
  - it shrugs off a sword hit ($0788 = 2) while Kirby is above it, inside the upward cone that e42_shrug_pose looks for: room == 108 and ram[0x0788] == 2 and ram[0x05E1] != 7 and (ram[0x60B6]*256 + ram[0x60A4]) - y >= 8 and abs(x - (ram[0x6092]*256 + ram[0x6080]))*2 <= (ram[0x60B6]*256 + ram[0x60A4]) - y
  - Kirby fights on (search-driven) and gives the last blow standing within 16 pixels of the boss in the right half of the screen: room == 108 and ram[0x6134] == 0x42 and ram[0x61D6] == 0 and abs(x - (ram[0x6092]*256 + ram[0x6080])) < 16 and x >= 130
forbid:
  - lost a life: lives < 5
  - dying: hp > 47
---
Coverage movie (cov7, unit en2b). From cov4-a-mk's duel before the sword is taken: Kirby takes the sword and, as the
boss comes down, hits it from above; it shrugs the hit off (e42_shrug, $0788 = 2) and e42_shrug_pose's aim at Kirby
answers below $10 / $E0 and above (Kirby straight above it), so the pose is chosen by the distance in X
(2B:B819-B835, never ran before). The same moment runs 2B:B665-B677 (e42_unused_p) for the first time.
Then the duel goes on (Kirby takes three hits) and the last blow lands with Kirby next to the boss in the right half
of the screen: e42_cape_vx gives the falling cape the velocity for Kirby right of the middle (2B:BBA5), and
e42_hop_center (2B:B7F0) and e42_other_side (2B:B606) take paths no movie had.
