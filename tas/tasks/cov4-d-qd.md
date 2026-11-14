---
name: cov4-d-qd
start: cov-minigame-quickdraw@41980
reference: forbidden
steps:
  - fifth duel, the first false start (A before FIRE): ram[0x6249] == 4 and ram[0x61F0] == 0 and ram[0x07CF] == 0
  - the second false start loses the duel: ram[0x6249] == 4 and ram[0x61F0] == 1 and ram[0x07CF] == 1
  - the result screen pays a life for the four hats and the game ends: room == 2 and world == 2 and ram[0x6249] == 0 and lives == 5
forbid:
  - lost a life: lives < 4
---
Coverage movie (units minigame, scenes3, leftovers). Quick Draw in the World 3 hub (level 0) from the corpus' frame
after four won duels. In the fifth duel A is pressed in the 20 frames before FIRE (qd_tick_early: the first false
start restarts the duel, 3C:ACB4), then again in the restarted duel (the second false start, 3C:ACE0: qd_lost + 1 and
the lost result after false starts, 3C:B87C / 3C:B89B). The result screen counts four hats, so qd_perfect reads qd_lost
(3C:B96A).
