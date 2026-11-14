---
name: cov4-d-egg
start: cov-minigame-egg@18100
reference: forbidden
steps:
  - all thirty throws are over with no bomb eaten and 27 eggs eaten (the game ends by the count, egg_over = 2): ram[0x07B0] == 30 and ram[0x07B1] >= 25 and ram[0x07B2] == 0 and ram[0x07AF] == 2
  - the 25-egg prize, one life, is paid and the game is left early with Start: room == 1 and world == 1 and lives == 5 and frame < 19500
forbid:
  - a bomb eaten: ram[0x07B2] != 0
---
Coverage movie (units minigame, leftovers). Egg Catcher in the World 2 hub from the corpus' frame before the first
throw. Every egg is eaten with A at the right moment and no bomb is: after the thirtieth throw egg_tick_end and
egg_over_test end the game by the count (3A:8137, 3A:80E7), egg_result_kind answers 2 (3A:8120) and egg_bonus pays a
life (lives_pending, 3C:BEB1) for 25 eggs or more. Start on the closing screen skips the rest of minigame_end
(3C:BABC).
