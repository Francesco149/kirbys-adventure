---
name: cov7-k-blob
start: main@20960
reference: forbidden
steps:
  - in 2-4's room 185 the light blue blob (type $23) walks on its block in the upper middle (slot 10): room == 185 and ram[0x6128+10] == 0x23 and ram[0x6290+10]*256 + ram[0x627E+10] == 0xAB2F
  - Kirby stays close to it (within $32 pixels in X and $10 in Y) while it walks, so its variable 5 counts down: room == 185 and ram[0x6128+10] == 0x23 and ram[0x6224+10] > 0 and ram[0x6224+10] < 50
  - after several countdowns one random draw comes out 0 and the blob hops (the script 2B:AA9C: it rises, Y velocity negative, while its thread waits with the tick 3E:D786): room == 185 and ram[0x6128+10] == 0x23 and ram[0x6290+10]*256 + ram[0x627E+10] == 0xD786 and ram[0x6116+10] >= 0x80
forbid:
  - lost a life: lives < 4
  - hurt: hp < 47
---
Coverage movie (cov7, unit en2b). e23_tick_walk counts variable 5 down only while Kirby is near the walking blob
(obj_near, $32 to the sides and $10 up and down); in the corpus Kirby never stayed near long enough. Here main's
Kirby keeps beside the blob on its block in room 185 (search-driven, without touching it) through many countdowns:
the random draws at variable 5 = 0 (2B:AB59-AB5D, random 4 at the first approach and random 3 after a countdown)
and at last a 0, which starts the hop (2B:AB5F-AB6F, the script 2B:AA9C) and its tick routine 2B:AB8B-ABB7.
