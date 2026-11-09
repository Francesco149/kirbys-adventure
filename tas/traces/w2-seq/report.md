# w2-sequence report (episode 1)
Movie: 24,870 -> 29,217 (4,347 frames), ~$1.40 total, 42 turns, all in one episode, 0 lives lost, 1 hit in room 169 and 1 in room 170. Both hits came before Tornado; no hits while holding it.
| step | frames (movie) | turns | ~$ |
|---|---|---|---|
| hub -> 2-1 (room 169) | 24870-24970 (100) | 3 | 0.20 |
| room 169 -> 170 (coconut shore) | 25000-26390 | 18 | 0.48 |
| room 170 -> 172 (beach) | 26420-27367 | 8 | 0.28 |
| Tornado in 172 (one goal search: inhale Twister + D) | 27394-27575 | 3 | 0.10 |
| 172 -> goal game 42 (avoid ability!=18, hp<31) | 27575-28350 | 3 | 0.10 |
| goal game (goalscan k=56, 395 f) -> hub, ability kept | 28350-28745 | 3 | 0.07 |
| hub -> 2-2 room 173 (avoid room 169) | 28745-29217 | 2 | 0.05 |

Pace was about 3,100 f/$ overall.

## What worked as written
- §6 ordered predicates plus `avoid ability != 18` in every search after the copy. The goal search `ability == 18` with B/D actions copied Tornado in 181 frames (12 s).
- goalscan worked: best k=56, the same as the previous run's range.
- The trick of putting the entry room in avoid worked: hub room 169 was excluded on the way to 2-2.

## What was wrong or missing (measured)
- A score of `-2*abs(x-door)-abs(y-door_y)` with 8-frame actions stalled 4 times in 2-1 (rooms 169 and 170, best x 249, 585, 913). Two causes:
  - Hills needed floating, and the y penalty plus many RNG-distinct ground states crowded the float branches out of the beam.
  - Switching to score `x` (plus a pit penalty) and chaining score-only partials worked. Recommend: score x first, add y only near the door.
- **Door entry fails while Kirby is puffed (floating)**. The search reached the door coordinates (score 0) but no `U*5 .*3` entered the door in room 170. Fix: a `B` (exhale), wait about 20 frames, then Up. Add `B*2 .*16 U*6` to the door alphabet. §2 does not mention this.
- 2-1 room ids: 169 shore, then 170 beach, then **172** log path (room 171 was not visited; the 169 side door at 584,137 goes to the grotto). The walkthrough's "A9-AC in order" is misleading.
- The 2-2 door is about 130 px right and 80 px up of the hub arrival spot: (258,185).
- Stage clear keeps Tornado (hub ability 18 confirmed by RAM).
