---
name: w1-scratch
start: power-on
reference: forbidden
steps:
  - 1-1 entered: world == 0 and room == 43
  - Whispy Woods arena: world == 0 and stage == 7 and room == 8
  - World 2 hub: world == 1 and room == 1
---
Make a trace from power-on to the World 2 hub: World 1 (Vegetable Valley, stages 1-1 to 1-4) and Whispy Woods.
Produce every input yourself; the reference TAS inputs and its splits are hidden for this task (walkthrough,
mechanics and speedrun text are fine).

This run measures the v2 search tools (explore, go) on a long task with fights. For comparison, with the older
tools the same harness did this stretch in 24,870 frames, ~195 turns and $3.23 (Sonnet) and in 20,247 frames,
~241 turns and $9.26 (Opus). Use the addendum's method first: `go` through each stage, an explore search with a
time cell through the goal game, explore searches with the boss HP variable in the cell for fights. Don't
optimise frames beyond what that gives; a complete, verified trace with honest per-stage turns and costs is the
goal. `milestone` at every stage clear. Report, per stage: turns, dollars, frames, searches that failed, and
where the addendum was wrong or missing something. Expected budget: under $4.
