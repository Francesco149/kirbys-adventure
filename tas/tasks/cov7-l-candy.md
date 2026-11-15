---
name: cov7-l-candy
start: w3-sonnet@69420
reference: forbidden
steps:
  - the Invincible Candy inhaled (not touched): bit 6 of kirby_flags set: room == 222 and (ram[0x05FB] & 0x40) != 0
  - an enemy killed by touching it while invincible: room == 222 and (ram[0x05FB] & 0x40) != 0 and ram[0x6128+14] != 17
  - an enemy inhaled and swallowed while invincible: room == 222 and (ram[0x05FB] & 0x40) != 0 and ability != 255
  - through the door with the flag kept: room == 223 and (ram[0x05FB] & 0x40) != 0
forbid:
  - lost a life: lives < 4
---
Coverage movie (units khelp, khelp2, hud, hit). In room 222 of World 3 normal-form Kirby inhales the Invincible Candy
(item 2) with B instead of touching it: e05_inhaled's far jump table takes entry 2 (scr_19_B821, never ran before),
the sparkle effect $19 and binop_mem kirby_flags |= $40. While bit 6 is set: hud_ability shows card $23 (HYPER),
pad_double_tap takes its bit-6 path (walking and double taps), hit_kirby calls hit_interrupt when an enemy touches
him (the enemy dies), hit_item, kirby_pal_row returns at once (the swallow's flash). Bit 6 survives the door to room
223 (kirby_start_init keeps bits 5 and 6) and ends about 1,000 frames after the candy, before any song change, so
snd_music's skip (3F:F861) and kirby_bit6_clear's free (14:A742) stay unreached.
