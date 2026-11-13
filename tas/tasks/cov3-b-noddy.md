---
name: cov3-b-noddy
start: main@108061
reference: forbidden
steps:
  - the creature of type $2E in slot 10 sleeps (tick e2e_tick_sleep 25.AC23): room == 109 and ram[0x6132] == 0x2E and ram[0x629A]*256 + ram[0x6288] == 0xAC23
  - late in the sleep (variable 3 = 1, variable 2 below 20): ram[0x620A] == 1 and ram[0x629A]*256 + ram[0x6288] == 0xAC23 and ram[0x61F8] < 20
  - it wakes on its own and walks again (tick e2e_tick_walk 25.ABEB): ram[0x6132] == 0x2E and ram[0x629A]*256 + ram[0x6288] == 0xABEB
forbid:
  - lost a life: lives < 6
---
Coverage movie (unit en25b). In room 109 (7-1) the Noddy-like creature of type $2E falls asleep on a ledge. Kirby
stands still and lets it sleep its full 480 frames: no movie had a sleep last longer than 224, so the waking code of
e2e_tick_sleep (25:AC35-25:AC6B) never ran.
