w3-continue report (recipe v1.1 validation), status at $8.7: 3-1..3-5 cleared, 3-6 in progress (room 228, f75229).
Per stage (frames / $): 3-1 ~?/0.7; 3-2 3-2 61565 total split, ~4.5 (Bugzzy slot diag); 3-3 3337/1.4; 3-4 4285/0.6; 3-5 4036/0.6; 3-6 so far ~0.65+.
Held: built-in beam + flow2 for traversal; random-mode search for fights (one hit per call); milestone per stage keeps episodes cheap (3-3..3-5 ~0.6-1.4 each).
Wrong/missing: (1) boss HP slot varies per branch - must re-read objects each fight (cost ~$2 in 3-2). (2) 'hp < N' avoid misses hp=255 while dying. (3) Score x alone gets trapped in pockets (3-6 room 228 at x457): needed a y/region bonus term. (4) Enemy chasing at 1 HP bar prunes all branches; dying on purpose = cheap HP refill (lives 3 kept via respawn). (5) Mirrored door rooms need walkthrough order; doors appear after scroll; roominfo lists no doors in some rooms (228) and warp stars/minigame doors misleading. (6) Star blocks need break search: goal tile byte change.
Not finished within budget: 3-6 rest, Shine&Bright, W4 hub.
Helpful tool: roominfo listing doors for all rooms; distance-field beam built into search.


FINAL (ep16, $9.47): 3-6 not cleared; stuck in room 230 (exit unknown). Random search (3000 samples, door/up/move alphabet) and beams (-y, y) found no room change; Kirby can float to y=36 (screen top) but no exit seen. Steps 2 (Shine&Bright) and 3 (W4 hub) not reached; step 1 (3-1 entered) held. Missing tool: door/exit listing for rotating-tower rooms; walkthrough lacked 3-6 room-230 exit.


UPDATE ($9.75): room 230 exit found by random search w/ '.*30' wait + 'U*5 .*3' alphabet (rotating tower door appears over time) -> 231 (cloud steps) -> door at top near Sword Knight (random search incl. inhale/spit) -> 232 (switch side room, breakable star blocks via slide search) -> 233 -> back to 231; true 3-6 exit still not located. Lesson: for time-varying doors include wait actions in the alphabet. Final: task steps 2-3 not reached, budget exhausted.


FINAL RESULT ($10.56, f87667): all 3 steps reached. Shine&Bright: ~$0.3 (random search, one 10-dmg hit per call; bar var). After both bars 0 the Star Rod piece is object slot 4 (class 12) -- fly to it (beam score, 33 frames), then goal game (A press), trans 0->5 at ~f+680, W4 hub world3 room3 ~400 frames later. Missing: 3-6 exit location in walkthrough, door listing for rotating rooms; boss-end pickup identification took 3 turns.
