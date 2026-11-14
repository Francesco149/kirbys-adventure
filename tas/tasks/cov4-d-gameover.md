---
name: cov4-d-gameover
start: cov-gameover@6935
reference: forbidden
steps:
  - CONTINUE chosen, and with both skips the World 1 hub is back before frame 7300: room == 0 and world == 0 and lives == 4 and hp == 47 and frame < 7300
---
Coverage movie (units scenes, scenes2). The game over of the corpus' cov-gameover, but A is pressed on the GAME OVER
card (gameover_tick_wait: sound $2C and the menu at once, 2E:A56E / 2E:A58F), CONTINUE is chosen, and A is pressed
again while sleeping Kirby runs off (gameover_tick_hurry: the scene ends at once, 2E:A655).
