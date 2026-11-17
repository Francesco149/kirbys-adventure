# Batch 13: poses no movie drew that play can reach (2026-11-17)

Units unread_kirby, unread_en and unread_sys draw every unread pose by force; these are the ones the agents judged
reachable in play, the leads for a coverage batch (a movie that draws them replaces nothing, but makes the poses
"played"). Pose numbers are entries of the named table; bit 0 of Kirby's pose is his facing; the forms' standing and
crouching poses are base + 2 x floor kind (flat and four slopes).

## Kirby (banks 1A-1C, unit unread_kirby)
- Other facing of a drawn state (movie@frame where the drawn partner first appears):
  - 1A:8000 / 1A:8676 poses 9, 27, 29 (main@52612-52625), 49 (w12-opus@2118).
  - 1A:8846 (inhale / full mouth) 29 (w3-sonnet@75090), 39 (w3-sonnet@74681).
  - 1A:96A4 (holding a grabbed enemy) 11, 19, 21, 23, 25, 33, 51 (attract@6469-6616, cov2-save-finished@143996).
  - Sword 11, 22, 31, 33, 35, 48, 105; Hammer 27, 28; Parasol 17, 21, 25, 38, 53, 65, 89.
  - 1C:8216 (ability attacks, sleep) 11, 13, even 40-56, odd 75-85, 124, 126, 131, 134, 139, 141, 149, 151.
  - 1C:8DA6 (hurt, frozen, held) 32, 34, 37, 39, 41, 43, odd 45-57 (frozen Kirby, main@110253), 73.
- Standing / crouching on a slope: Sword 12-17 and 50-55; Hammer 16, 17, 20-23 and 56, 57, 60-63; Parasol 18, 19,
  22, 23 and 60-63, 66, 67; Stone 14-17 (two slope kinds); full mouth 1A:8846 30, 31 (the slope kind not covered).
- Full-mouth walk up a slope for more than 12 frames: 1A:8846 40-43.
- The goal game's row-4 sign: 1A:99DA / 1A:99F2 entry 4.
- 1C:94CE entry 76 drawn whole on screen (the corpus clipped one sprite).

## Enemies and bosses (banks 30-33, unit unread_en)
- Apple rider ($13) and M-ball rider ($14) rolling while facing right.
- Aiming cannon ($10) with its barrel in octants 3-5.
- Leaper $2F upside down, facing the other way (pose 4).
- Lance and axe knights of the Meta Knight ambush (main@55642) facing the other way.
- Mr. Frosty facing right (14, 16); UFO laser facing left (5); Chilly's frost facing right; type $1E variant 6
  sitting facing right; the shell mid-boss dropping its small shell facing right.
- Paint Roller painting picture 1 (2C:A73E never ran): poses 42-45.
- Dedede: e47_swallow's tail facing right (33:9796 pose 7); e47_caught_poses with kirby_form 1 (2D:A3C4, pose 4).
- Other facings: Meta Knight 31:8000 5, 22, 60 and 31:80F8 even 22-28; last boss 49, 51; beetle even 40-50; shell
  boss 76, 78, 98.

## Minigames (banks 35-3A, unit unread_sys)
- Crane Fever prize pictures (3A:9589 by crane_prize_rows): one small doll (0), two small (2), small then big (3),
  big then small (4), two big (5); the corpus only won one big doll. The first credit's picture (3A:9651 entries 0,
  2) depends on the same results.
- Crane Fever's claw holding a look-1 doll (the table at 3A:8D2F); crane_claw_look ran only with look 0.
- Quick Draw round 4, the hat landing (3A:978C entry 4, qd_hat_land).

## Unsure (who selects them not traced; listed in each unit's Open list)
Kirby: 1A:8EE6 10-15, 35, 99, 112-122; 1A:96A4 26-29, 36, 37; 1A:9910 76, 87; 1A:99F2 6; Sword 36, 37; Hammer
36-43, 82, 83; Parasol 40, 41, 92-95; Ball 16, 18, 23; 1C:8216 132, 133; 1C:8DA6 10-15, 58-71; 1C:94CE 3, 14, 15;
1C:9CD7 8, 10, 12. Enemies: Meta Knight 31:8000 70-77, 82-83, 90-105, 121-123 and 31:80F8 0-11, 49-52; Mr. Shine &
Mr. Bright 31:9218 30, 31, 66-68, 70, 92; beetle 33:838A 10, 11, 22-27, 64-75; shell boss 33:8B50 10, 11, 104-107;
type $4F 33:9E5A 10, 11; 32:9F37 1, 3; exhibit $0F (32:86D9). Minigames and scenes: the level card's Kirby
35:93A5, enemy types $22, $4D, $25 (bank 37), 37:93F2, 37:9A97 48/49, 37:967D 2, and the remaining Egg Catcher,
crane and Quick Draw entries.
