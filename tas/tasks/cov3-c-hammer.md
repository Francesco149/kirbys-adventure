---
name: cov3-c-hammer
start: cov2-abilities-mole:hammer2
reference: forbidden
steps:
  - Hammer state 2: ability == 8 and ram[0x5E0] == 4 and ram[0x5E1] == 2
  - Hammer state 3: ram[0x5E0] == 4 and ram[0x5E1] == 3
  - Hammer state 6: ram[0x5E0] == 4 and ram[0x5E1] == 6
  - Hammer state 7: ram[0x5E0] == 4 and ram[0x5E1] == 7
  - Hammer state 13: ram[0x5E0] == 4 and ram[0x5E1] == 13
  - Hammer state 10: ram[0x5E0] == 4 and ram[0x5E1] == 10
  - Hammer state 12: ram[0x5E0] == 4 and ram[0x5E1] == 12
  - still alive with Hammer in the Heavy Mole tunnel: room == 12 and ability == 8 and frame >= 83100
forbid:
  - lost a life: lives < 6
---
Coverage movie for Hammer Kirby (kirby_form 4, ability 8). In the Heavy Mole fight, with the Hammer copied
from the mole's missile, Kirby goes through the Hammer states one by one ($05E1 = 2, 3, 1, 0, 4, 5, 6, 7, $0D,
$0A, $0C: walk, run, jump, swing, duck, slide, inflate and the swings in the air), then keeps up with the
autoscroll for about 500 more frames without dying.
