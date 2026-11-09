# Notes (w12-scratch validation run)

## State
- Steps 1-4 done (Paint Roller arena world1 stage7 room9 entered f48834). Paint Roller killed f49849 (checkpoint prdead f50089), piece caught ~f50240, stage clear trans 0->5 at f50786, hp refilled 47.
- Movie at f50889: "LEVEL 3 BUTTER BUILDING" intro screen playing. NEXT: play .*N (maybe a few hundred frames; press nothing / try T if stuck) until world==2 and room==2 (W3 hub) -> then milestone 'paintroller' and call finish (task's last step = W3 hub). Update recipe table first.
- Budget: ~$23.5 of $35 spent.

## Facts
- W2 hub: Paint Roller door at (696,121) (top of right castle). (488,121) star door = mid-boss Arena (room 37, Mr Frosty) - NOT the boss.
- Paint Roller with Hi-Jump: 8 hits x 8 dmg (fhp=$61D8), random-mode one hit per call 54-109 f. At hp 7 the 7th-hit state was a death trap (all continuations died); fix = from fhp=4 state, play a survival rollout found in lab until the boss moved away, then random search found the last hit (343f).
- Death resets fhp to 0 -> goal "fhp<4" gives false hits without avoid hp>47.
- After boss kill Kirby ignores A until D pressed; piece caught with D*2 L*4 A*20.
