---
name: cov3-b-mk
start: main:6-7-fight
reference: forbidden
steps:
  - Kirby (7 HP) is beaten in the first try at Meta Knight and is back in the hub: room == 5 and lives == 5
  - back in the boss room with full HP: room == 108 and hp == 47 and lives == 5
  - Kirby has the sword again: room == 108 and ability == 3 and lives == 5
  - Kirby is right of the boss (slot 12): ram[0x6134] == 0x42 and ram[0x61D6] > 0 and x > (ram[0x6092]*256 + ram[0x6080]) + 32
  - the boss is beaten with Kirby within 8 pixels of it: ram[0x6134] == 0x42 and ram[0x61D6] == 0 and abs(x - (ram[0x6092]*256 + ram[0x6080])) < 8 and room == 108
forbid:
  - lost a second life: lives < 5
---
Coverage movie (unit en2b). Meta Knight's duel in room 108 (6-7). From the corpus' frame with Kirby at 7 HP, Kirby
is beaten at once (lives 6 to 5), comes back from the hub with full HP, takes the sword and fights from the boss's
right as well as its left (the corpus only had the boss right of Kirby), pins it at the left wall (e42_clamp_x) and
finishes it standing on it, so that the falling cape is within 16 pixels of Kirby (e42_cape_vx).
