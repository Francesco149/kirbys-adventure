---
name: cov4-b-sun
start: main@40820
reference: forbidden
steps:
  - the goal game (the stage before the boss door) played with the A press 35 frames later than main, back in the World 3 hub: room == 2
  - in the boss room of World 3 the first move is the other way round (e45_begin's random number 0 stores 7 in $078C, the sun goes up and the moon stays on the ground): room == 10 and ram[0x078C] == 7
  - the fight goes on to frame 43000 with Kirby alive: room == 10 and frame >= 43000 and hp > 0
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov4, unit en28). Mr. Shine and Mr. Bright (type $45) pick their first move with one random
number in e45_begin; every corpus movie entered the fight with the same generator state and got the same answer.
No random number is drawn between the goal game and that call, so the A press in the goal game is delayed by 35
frames (the goal game draws a number every 4 frames); the rest of main's inputs to the boss door are kept. The
answer 0 (28:BAE2-BB1C) starts the other order, and Kirby then dodges the pair for about 1,200 frames.
