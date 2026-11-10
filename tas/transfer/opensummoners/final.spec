# final.spec — boot -> title -> New Game -> control in the first playable room -> cross it -> talk to the mother
# (rt.py spec tokens; text after '#' is a comment; check.py compiles this to final.jsonl and verifies it)
700:enter/4            # title menu: Start (cursor starts there)
800:down/4 840:down/4  # new-game config: cursor to "Start Game"
900:enter/4            # confirm -> prologue
1000:enter/3%10*182    # Enter every 10 frames: skips the prologue, advances every cutscene dialogue;
                       #   the last press (f2810) dismisses the movement-tutorial line = control starts
2815:right/290         # walk across the shop and up the stairs (lx 19200 -> 87552, ly 52000 -> 36000)
3110:c/4               # jump at the top of the stairs ...
3112:left/82           # ... to the left: lands on the kitchen floor (ly 32800), stops right of the mother
3225:x/4               # talk (X = attack/confirm; Enter and Up do not talk)
3260:enter/3%10*25     # advance the mother's lines ("... spare crates and barrels in our bedroom ... through the door");
                       #   the conversation is over before f3500
3520:left/76           # walk left to the bedroom door on the same floor (68 frames stops short; 72..84 work)
3621:up/6              # enter the door -> room 210141
3700:enter/3%10*40     # advance whatever plays on arrival
4150:right/40          # move in the new room
