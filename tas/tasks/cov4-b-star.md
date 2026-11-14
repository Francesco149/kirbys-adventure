---
name: cov4-b-star
start: main@21095
reference: forbidden
steps:
  - the mix roulette in room 185 stopped early on Freeze: room == 185 and ability == 13
  - Kirby walks right until the arena lock scrolls the camera (extra_state $78C9 = 2, kirby_min_x above 256): room == 185 and ram[0x78C9] == 2 and ram[0x05C9] == 1 and ability == 13
  - Select drops the ability while the lock is still scrolling, its star starts left of kirby_min_x and is freed at once: room == 185 and ram[0x78C9] == 2 and ability == 255
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov4, unit en19). In room 185 (the mid-boss arena of World 2) main mixed two abilities into the
UFO. Here the roulette is stopped early (Freeze), Kirby walks on until arena_lock starts scrolling the camera
(extra_state 2, kirby_min_x rising from 258), and Select drops Freeze there. The ability star starts left of
kirby_min_x, so e05_star_bounds takes its path for extra_state 2 (19:B958-B971) and frees it (19:B9C9); in the
corpus no ability star existed while an arena lock was scrolling.
