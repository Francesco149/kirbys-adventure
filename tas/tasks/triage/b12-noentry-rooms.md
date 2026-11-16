# Batch 12, part C: the rooms no door leads into (static research)

Question: rooms 7, 20-23, 127-132, 168, 310, 311 and 313-326 have no door record leading into them from a live room.
Does the game load any of them another way? Answer: **no. None of these rooms can be reached by play.** The only
way in is a forced state (pokes) or a ROM patch, and the recipe is at the end of this file. Pictures of every room
are in `tas/tasks/triage/b12-png/roomNNN.png`. They were made with that recipe from main@5000, where Kirby happens to
be riding the UFO, so he shows up as the UFO in them.

## 1. Every way a room number gets into `room` / `room_return` / `$055A`

Sources: `kd xref` (room, room+1, room_return, $0564/5, $055A-$055D, door_index) plus a **static byte scan of the
whole PRG**. The scan looked for STA/STX/STY/INC/DEC abs, STA abs,X/abs,Y onto $055A-$0569, and for the script
opcodes set_mem8 ($11) / set_mem16 ($27) aimed at those addresses. It found every corpus writer and only two places
that never ran:

| writer | room it loads |
|---|---|
| room_pick → room_goto (door, kind 0 / 1-7 / 8 / 9 / $D / $E) | the door record's destination |
| room_pick_kind kind $10 | room $2A, with the door's destination in room_return |
| room_pick_kind kinds $A-$C (minigames) | none (room_return_save keeps the door's destination) |
| room_pick_boss kind $F | boss_room[world] = 8, 9, 10, 11, 12, 108, 14 |
| room_pick, room 12 | room 13 |
| room_pick, room+1 = $FF | room_return, else $055A-$055D (written only by kinds 1-7 / $F = the room being left, demo_init, new_game_room) |
| demo_init (demo_setup col +$20/+$28) | demos 0-7: **$138 = 312**, 8, 9, 10, 11, 12, 108, 14 |
| new_game_room (12:9215) | 0 |
| continue_setup (continue_room) | 0-6, 15, 16 |
| fsel_rematch_room / rematch_next (rematch_room_0..3) | 8, 9, 10, 11, 12, 108, 14, 15 |
| e06_demo_room (e06_hub_rooms) | 30-36 |
| credits_to_the_end / e4e_end / ending_to_fountain / finale_leave / save_game_complete | 18 / 17 / 19 / 16 / 6 |
| e6f_press, room_return_save → room_return_restore | the current room / a door's destination |
| save_load / save_transfer (file → RAM) | whatever room_return the game saved (a hub) |
| scripts: 29:B13C, 2E:B089, 38:B052 | only bytes 2-3 of room_return, room+1 = 0, or $FFFF |
| **never ran:** 13:A171 (door kind $70) | room_return_saved: only room 310's door has kind $70 |
| **never ran:** 3D:BF57 old_3d_rematch | dead older copy of rematch_next; its tables give the same rooms |

door_index is written only by door_find / kirby_door_here (the door at Kirby's position, from the room's own list)
and by e06_leave / e06_shot_tick_diag (door 0). Nothing remaps room numbers in the Extra Game. game_mode ($F4) is
read in the room code only by room_pick_kind, for minigame_level. room_extra_load only patches blocks. The 41 bytes
before room_doors (12:9214, `door_recs_spare`) hold an old copy of boss_room (8, 9, 10, 11, 12, 108, 14). The only
door kinds the ROM uses are 0, 1-6, $10, $18-$1F, $2A-$2C and $70.

The one gap in the proof: an indirect store (`sta (zp),y`) that never ran could not be ruled out by the byte scan.
The only indirect writer the corpus saw is save_transfer.

**Doc bug found on the way:** demo 0 (the tutorial demo) plays in room **312** ($055A = $38, $055B = 1:
`kd watch 055E 055F --on attract@1100+30` shows $38/$01). It is not room 56 as `db/attract.toml` (demo_setup) and the
`attract` corpus note say. Room 312 is a 9-screen room (tile set 7) whose only door leads to 314.

## 2. The groups

### Rooms 20, 21, 22, 23 and 310: five more museum rooms. Unreachable.
All five are one screen with tile set 17, the museum tile set that live museums 24-29 also use (hub doors of kind
$18). Each holds type-$0A exhibits (variable 0 = the exhibit, inhale number from e0a_abilities):
- 20: exhibit $F, door to hub 5 (cell 5, $75). That is the spot of hub 5's kind-$2A minigame door, which is also
  where room 19 (the fountain room) exits. room_data_bank bit 7 is set (entering it would put the room left into
  room_return). Its screen is **identical to room 310's**.
- 21: exhibits $E, $F, door to hub 1 (1, $E7): the spot of hub 1's arena door (kind $19 → 37) and of room 37's exit.
- 22: exhibit 9, door to hub 3 (0, $35): column 3, next to hub 3's kind-$1C door at (0, $39).
- 23: exhibits 0, $C, door to hub 4 (1, $53), next to hub 4's own museum door (1, $55 → 28).
- 310: exhibit $D. Its only door has **kind $70**: room_pick_kind 13:A171 loads room_return_saved, so you leave by
  going back to wherever the last minigame or boss door was headed. That is the only kind-$70 door in the ROM, and it
  is the only user of that never-run path.

Rooms 22 and 23 use a different palette and layout (red curtain stands, a checkered wall). Rooms 20, 21 and 310 look
like the live museums (pedestal with a star). None of them has an identical stream to a live room. Reading: these are
museums that were planned for, or replaced at, hub spots that now hold minigame or arena doors. 310 is a "return to
caller" museum. Picture: room020/021/022/023/310.png.

### Room 311: a cut arena for World 4. Unreachable.
Tile set 20 (the arena tile set of rooms 37-41). Its screen is **identical to rooms 37-40**. It holds kind $B0 =
type $48 (the walrus-like mid-boss) with obj_param **0**, while every live arena (37-41) uses the obj_param-1 kinds.
Its door leads to hub 3 (cell 4, $C4), the same exit as live arena 39 (which has the beetle $4A, class 1). So it is
an earlier or alternate arena for hub 3. Picture: room311.png.

### Rooms 127-132: the cut start of 7-2's second mid-boss gauntlet. Unreachable.
Room 113 (7-2's first room, hub 6 kind-2 door) has three doors. The lower one ($88/$89) leads to the class-0 chain
114 → 126 (arena, corridor, arena, ...), and that chain was first loaded in cov11-c-arena7. The upper one ($82) leads
to **133**, which main takes (main@111443). The class-1 chain is 127 (Poppy Bros Sr-like $22, kind $BD) → 128
corridor → 129 (blue turtle $4F, $BB) → 130 → 131 (walrus $48, $B1) → 132 → **133** (hammer ape $4C, $B3) → 134 → 135
($4B) → 137 ($4A) → 139 ($4D) → 141. It mirrors 114-139 room by room: the arenas' screens are **identical** to 114,
116 and 118, and the corridors 128/130/132 have streams **identical** to 115, 117, ... 138. Only the object kinds
differ ($10 in the vars byte = obj_param 1, the harder pattern). Since room 113's upper door enters at 133, the first
three class-1 fights (127-132) are skipped. They are complete rooms with no way in. Picture: room127-132.png.

### Room 168 and its satellites 7, 313-326: a developer test hub. Unreachable.
Room 168 is one screen with tile set 14 and no objects. It has six doors: (1,2) → **7**; (2,8) → 19 (the ending's
fountain room); (4,8) → 317; (6,8) → **312** (the tutorial demo's room); (8,8) → 325; (10,8) → 313. Only 316, 324 and
326 lead into it, so it is closed from the outside. It is the hub of a test area:
- **Room 7**: tile set 3 (World 7's palace tiles, as in rooms 142-167). It shows a two-floor pink palace with seven
  doors (kind 0): upper floor → hubs 0, 1, 2, 3, lower floor → hubs 4, 5, 6. In other words, a world select. No
  objects. Picture room007.png.
- **313-316**: four one-screen arenas with tile set 9 and identical screens. In each, one class-1 mid-boss: 313 beetle
  $4A ($B7), 314 Poppy Bros Sr $22 ($BD), 315 shell $4B ($B9), 316 blue turtle $4F ($BB). Chain 313 → 314 → 315 → 316
  → 168. The tutorial room 312 also exits into 314. A mid-boss test.
- **317-324**: eight one-screen rooms with tile set 0 and the same header. Blue brick, bare platforms, no objects,
  doors chained 317 → ... → 324 → 168. A door/platform test. They resemble no live screen (24 or more blocks
  differ from the nearest).
- **325 → 326**: tile set 12. 325 holds a cannon (type $06 variable 6, kind $F9), its fuse (type $0B, kind $FB) and
  exhibit 1. The cannon's flight ends with door 0, which is 325's only door, to 326. 326 (no objects) leads back to
  168. A cannon test.
- 168 → 19 → hub 5 and 168 → 7 → any hub give the way back into the real game.

None of these screens or streams is a copy of a live room (nearest live screen: 168 vs room 113's cell 1, 80 blocks
differ). This is cut debug content, not a copy of a live area.

## 3. Showing them (forced state, no ROM patch needed)

From any gameplay frame: room + 1 = $FF, room_return = (room lo, room hi, cell, position), leave_code = 1. The next
frame's room_enter loads it.

```
cd disasm
./kd try --on main@5000 --frames 150 --poke 055F=0xFF --poke 0562=<lo> --poke 0563=<hi> \
    --poke 0564=<cell> --poke 0565=<pos> --poke 056A=1 --png ../tas/tasks/triage/b12-png/roomNNN.png
```

Entries used: 168 (0,$55); 7 (0,$55); 310 (0,$D9); 311 (0,$19); 20 (0,$D9); 21 (0,$89); 22 (0,$B9); 23 (0,$79);
127 (0,$D9); 128/130/132 (1,$37); 129/131 (0,$29); 313-316 (0,$55); 317 (0,$77); 318-321 (0,$28); 322 (0,$48);
323 (0,$26); 324 (0,$78); 325 (0,$55); 326 (0,$22).

A kt movie could start the same way (pokes at a hub frame) and then walk 168 → 7 → a hub, or fight the 127/313
arenas. It would be coverage of cut content under a forced state, not play, so it belongs to the dead_* /
UNUSED.md side (`never = true` style) and not to a normal coverage task. A one-byte ROM patch also works for a
door-based route: point one live door's byte 2/3 at the room, for example room 113's upper door (its record is
12:96AF; `--patch 12:96B1=0x7F` sends it to 127 instead of 133; untested).

## 4. Coverage tasks

None. No room in these groups is reachable by play.
