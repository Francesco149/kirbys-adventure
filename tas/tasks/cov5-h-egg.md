---
name: cov5-h-egg
start: cov-minigame-egg@18100
reference: forbidden
steps:
  - all thirty eggs eaten and no bomb: ram[0x07B1] == 30 and ram[0x07B2] == 0
  - the 30-egg prize, three lives, paid in the World 2 hub: room == 1 and world == 1 and lives == 7
forbid:
  - a bomb eaten: ram[0x07B2] != 0
---
Coverage movie for Egg Catcher's perfect game (units leftovers and minigame): from the corpus' frame before the first
throw every one of the 30 eggs is eaten and every bomb is let bounce off; egg_result_kind answers 3 (3A:8125, 30
eggs), egg_bonus takes its 30-egg entry (3C:BE9F-BEA3) and three lives are paid on the return to the hub.
