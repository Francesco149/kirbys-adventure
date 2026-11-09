---
name: w12-scratch
start: power-on
reference: forbidden
steps:
  - 1-1 entered: world == 0 and room == 43
  - Whispy Woods arena: world == 0 and stage == 7 and room == 8
  - World 2 hub: world == 1 and room == 1
  - Paint Roller arena: world == 1 and stage == 7 and room == 9
  - World 3 hub: world == 2 and room == 2
---
Make a trace from power-on to the World 3 hub: World 1 (Vegetable Valley) and Whispy Woods, then World 2 (Ice
Cream Island) and Paint Roller. Produce every input yourself; the reference TAS inputs and its splits are hidden
for this task (walkthrough, mechanics and speedrun text are fine).

This is the validation run for the recipe. For comparison: the previous run did 1-1..1-3 itself before the
recipe existed, in 13,305 frames for ~$6.4 (plus a $4 earlier attempt), 70% slower than the reference. Apply the
recipe as written and measure where it holds and where it doesn't. Don't optimise frames beyond what the routine
gives; a complete, verified trace with honest per-stage costs (and a short report of recipe corrections) is the
goal. Expected budget: ~$25-35. The harness stops hard at the budget: keep the report current at every
milestone so a stop leaves a verified partial trace and an up-to-date report.
