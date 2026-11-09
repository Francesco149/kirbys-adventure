# Report (w12-scratch) — final, 69,781 frames, ~$14.4 total (budget $20)
All 5 steps reached (W3 hub world2 room2 at f69751). ~4,840 f/$ overall.
Segments (frames / $): 1-1+1-2 10,418f/$1.41. 1-3,1-4,Whispy +14,452f/$1.82. 2-1+2-2 +12,252f/$1.83. 2-3 +7,060f/$2.48 (low HP Meta-Knight ambush). 2-4 +11,349f/$4.73. 2-5 +9,349f/$1.1. Paint Roller + exit ~4,900f/~$1.0 (fight ~$0.5 via random search, 7 calls; ~$1 lost to the exit puzzle).
Worked: per-room routine; recipe alphabet; hub-door inputs; goal game .*60 A*3; random search with goal 'boss_hp<cur' kills bosses cheaply; waypoint beams in water rooms.
Corrections / missing:
- BOSS EXIT (Paint Roller, and probably any boss): after the kill the game does NOT leave by waiting. A white circle (the item/star) sits mid-room; Kirby must touch/inhale it (float up above it, then press Down to inhale/drop onto it; goes to a roulette-ish screen), then ~400 frames later trans 0->5 (stage clear), +~400 frames the hub. I wasted ~$1 and many turns waiting 2000+ frames. Recipe wrongly implied 'just wait ~2000f' (Whispy movie happened to touch it). Check the object slots / screenshot for a pickup after a boss kill.
- ram tool: addr decimal unless 0x-prefixed.
- flow2 ONEWAY={0x23,0x0f} makes field INF through ladders/thin platforms -> patch ONEWAY=set(); solids wrongly blocked breakables; needs __main__ guard.
- flow2 stalls in water rooms; waypoint beams work better.
- Normal Kirby breaks bomb blocks by inhaling; kills Blippers by inhale.
- Low HP before ambush rooms (2-3 Meta-Knights) made it very slow; protect HP / pick up Tomato.
- Long searches (300-500s) ~$0.18 each with no gain; cap time_limit ~100s.
- Scroll-lock mid-boss rooms need an ability. Warp star: board then wait ~450f. hp reads 255 while dying. Milestone per stage clear.
Tool wishes: object-slot viewer; python state persistence; WRAM indexable in python; look/play picture at post-boss states.
