---
name: w2-sequence
start: w12-sonnet:ms-1-whispy
reference: forbidden
steps:
  - 2-1 entered: world == 1 and room == 169
  - Tornado copied inside 2-1: world == 1 and ability == 18 and room >= 169 and room <= 172
  - 2-1 goal game: world == 1 and room == 42
  - back in the W2 hub holding Tornado: world == 1 and room == 1 and ability == 18
  - 2-2 entered holding Tornado: world == 1 and room == 173 and ability == 18
forbid:
  - lost a life: lives < 4
---
A "do X in this sequence" task. The movie starts from a verified library prefix: the w12-sonnet run's trace from
power-on to the World 2 hub (frame 24,870: no ability, full HP, 4 lives). From there, in this order:
1. enter 2-1;
2. copy Tornado (ability id 18 = $12) inside 2-1. The walkthrough puts Twister on the log path;
3. clear 2-1 (goal game);
4. return to the W2 hub still holding Tornado;
5. enter 2-2 still holding it.

No life may be lost along the way. Take damage only if it cannot cost the ability: a hit can knock it out.

The point is to measure how the recipe handles an ordered, constrained objective rather than plain progress:
- planning the order;
- guarding the constraint in search (`avoid`);
- checking it with RAM.

Report the cost per step and whatever the recipe's §6 got wrong. Expected budget: ~$5-8.
