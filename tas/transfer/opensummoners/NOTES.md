# Transfer test: the trace-authoring recipe on a replay-only target (Fortune Summoners under rhost/wine)

Current state, not a diary. Target: `/opt/src/OpenSummoners` (read-only, untouched), `rhost.py ... --target wine`,
edition `enold`. Everything of ours is in this directory. Measured 2026-11-10.

## Result

`final.spec` (macro) -> `final.jsonl` (4190 input frames, replayed for 4310): boot -> title -> New Game ->
control in the first playable room -> across the room, up the stairs, onto the kitchen floor -> talk to the
mother -> through the bedroom door into a second room -> control there. `python3 check.py` replays it twice
and evaluates the predicates below: VERDICT PASS (`check.out`), four replays in two batches all end
`frame=4310 tick=3116 rng=8a54b40d state_semv=4a00df1a54543412`.

| # | predicate | first holds | evidence |
|---|---|---|---|
| P1 | title scene entered | f47 | trap 0x56aea0; `world==0` at f690; shot f690 (menu, cursor on Start) |
| P2 | new-game config scene entered | f752 | trap 0x564780 (Enter at f700); shot f780 |
| P3 | in game, first room loaded | f1222 | trap 0x586010 #1; `room_id==210110` at f1300; shot f1300 (town arrival cutscene) |
| P4 | house interior loaded, still scripted | f2696 | trap 0x586010 #3; `room_id==210140`, `w2760==1` at f2700 |
| P5 | control: `w2760==0 and dlg==0` in 210140 | f2810 | write watch on both words; dump f2811 |
| P5b | control is real: Right moves the leader | f2826 (`lx` > spawn+1000; Right from f2815) | per-frame `lx` trace (watch); a twin with Right from f2811 moved at f2812 (batch b07 `ctl`) |
| P6 | crossed the room, climbed the stairs | f3107 (`lx>=87500`), `ly==36000` | watch + dump f3109 (spawn was 19200,52000); shot f3109 |
| P6b | jumped onto the kitchen floor | `ly==32800` at f3222 | dump; shot f3222 |
| P7 | talked to the mother (G3) | script f3225 (`w2760->1`, X at f3225), box f3271 | watch + dump f3290; shot f3290 |
| P8 | conversation over, control back | by f3505 (dump) | `w2760==0, dlg==0` |
| P9 | left the first room through a door (G2) | door script f3621 (Up at f3621), room setup f3646 | trap 0x586010 #4; `room_id` 210140 at f3615 -> 210141 at f3700; shots f3615 / f3700 |
| P10 | control in the second room | by f3900 (dump) | `w2760==0, dlg==0` in 210141; Right from f4150 moves `lx` 44800 -> 54760 |
| never | crash, extra room load, back to title | - | no `AV` line, 4 room setups exactly, `world != 0` at the end |

Determinism: `frame / tick / rng / state_semv` equal across replays (same batch and across batches).
`state_sem` and `state_full` differ between replays on wine (they include wine-volatile words; the one word
that differed in a raw dump diff of two identical replays was 0x8a93ec, a window-handle-like value). rhost's
own wine gate is `state_semv`.

Screenshots looked at: `shots/final_contact_sheet.png` (16 key frames of the final replay) and the single
frames `shots/final_shot_f*.png`; from the search: `shots/explore_*.png`.

## Named state

| name | how to read it | meaning | validated on |
|---|---|---|---|
| `world` | `*(0x8a9b50)` (.data) | 0 until the first room exists | 0 at title/config/prologue dumps, non-0 after the first room setup |
| `room_id` | `*( *(world+0x1038) )` | packed room id | 210110 town arrival, 210120 house front, 210140 house interior, 210141 bedroom: each matches its screenshot |
| `lx`, `ly` | `world+0x2784 -> +0x200c -> +0x9f4 -> +0x40 -> +4 / +8` | leader (Arche) position, px*100 | spawn 19200,52000; +240/frame while Right is held; floors at ly 52000 / 36000 (stairs top) / 32800 / 16800 |
| `w2760` | `*(world+0x2760)` | 1 = a script owns the game (cutscene, conversation), 0 = free roam | 1 in every cutscene/conversation dump, 0 in every free-roam dump (>60 dumps, 4 rooms) |
| `dlg` | `*( *(world+0x1044) + 0x54 )` | open dialogue box object, 0 = none | non-0 exactly where the screenshot shows a box |
| scene entry | `--trap VA` hit frames | 0x56aea0 title runner, 0x564780 new-game config, 0x586010 room setup (one per room load), 0x439690 script beat | line up with the screenshots |

`world` / `room_id` / `lx` are from the target's knowledge base (`src/world_layout.h`). `w2760` and `dlg` were
found by mark -> act -> diff: dump with the tutorial dialogue open vs. free roam in the same room, minus the
words that also differ between two free-roam dumps, restricted to the known objects (world, room, event
runner, room loop); 27 candidates, 3 obviously right, validated on every dump of two runs.

Heap addresses are run-to-run stable (rhost's fixed arena), also across different input timing, as long as
the room history is the same. In room 210140: `w2760` 0x20075b90, `dlg` 0x20070e44, `lx` 0x20397084,
`ly` 0x20397088, `roominfo ptr` 0x20074468.

## Game facts found (first playable room = Arche's house, 210140)

- Title: Enter on Start (cursor there). Config menu: Down, Down, Enter (Start Game). Enter skips the prologue
  and advances dialogue; Enter every 10 frames from f1000 reaches the house at f2696, the tutorial line closes
  with the press at f2810.
- Keys: arrows move, C jumps (and cancels a dialogue), X talks / confirms, Up enters doors. Enter confirms but
  does not talk; Z does nothing near an NPC.
- Front door (Up at spawn): father refuses ("we still need your help around here"), before and after the
  mother's errand. Ground-floor right door and the kitchen-floor door: "The door is locked." until the mother
  has been talked to; then the kitchen-floor door (lx about 48100..51000) leads to the bedroom 210141.
- Walking: 240 units/frame, hold N frames => about 240*N + 1400 units including the slide. Left wall 6400.
  Holding Right from spawn climbs the stairs to (87552, 36000). Walking left from there goes back down; a
  jump (C) with Left lands on the kitchen floor (32800). Holding Left there leads up to the top floor (16800).

## Tooling facts (rhost on wine, what bit)

- `--watch VA` (periodic read) on a heap address faults at frame 0; the batch then hangs in `winedbg --auto`
  (batch b02; ended by terminating that batch's six pids). `rt.py` refuses non-.data addresses now.
- `--watch-write VA@F` (4 hardware watchpoints) gives a per-frame trace of a heap word, but under wine the
  watchpoints stop firing when a dialogue closes / a script ends. Arming a later slot re-arms the earlier
  ones, so slots get staggered arm frames (`rt.py --ww name=VA@F`). After 40 hits a slot logs only value
  changes.
- All runs of a batch share one set of `--dump-at / --shot-at / --frames` options.
- Dumps are 13 MB each; this session wrote about 21 GB of them (removed afterwards, except the last check).
- Speed depended on the machine's load, not on rhost: 9..33 fps per replay while the box had a load average
  of 45..70 (other jobs), 70..133 fps once it dropped below 30.

## Files

- `rt.py` — spec -> trace, batch runner, dump reader (pointer chains), dump diff, write-watch / trap parsing,
  cost ledger. `check.py` — the verifier. `final.spec` / `final.jsonl` — the result. `check.out` — last verdict.
- `cands/<batch>/*.jsonl` — every candidate trace (the spec is its first line). `bNN.out` — each batch's report.
  `batches.jsonl` — cost ledger (`python3 rt.py cost`).
- Run directories (logs, shots): `/mnt/ephemeral/opensummoners/wine/root/runs/20261110-01*-run`, `...-02*-run`.
