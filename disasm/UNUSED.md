# What the game never shows

Kirby's Adventure (USA, Rev A) holds code and data that no corpus movie reaches: 200 movies and 13.0 million
frames, covering the whole game, every ability, the minigames, the 100% file, the Extra Game and the sound test.
The units `bank_ends`, `dead_kirby`, `dead_en1`, `dead_en2` and `dead_sys` describe those bytes from the ROM itself.
Every entry there is marked `never = true`, and the gate fails if a movie ever runs it. Where it is possible, the
description is checked by running the dead code: an `effect` claim patches the ROM or pokes RAM at a corpus frame,
then compares the result with the untouched run.

Each picture below is the last frame of such a run. The command under it reproduces the picture (`./kd try`, from
`disasm/`), and the claim named next to it checks what the text says.

Some of this content is not cut at all, only unplayed: the corpus never went there. That content is listed
separately at the end, and a new movie will move it into the documented part of the game.

## Leftovers of an older build

The ends of many banks hold what an earlier build left there. Some of it is copies of live code and data at a
fixed shift, and the rest is the random power-up state of the build machine's memory. Every relocated copy that
calls the fixed bank calls it $43 bytes higher than the live code does, so they all come from one older build. That
build had German text in it.

### A staff page with another name

![The older staff page](unused/bank_ends-credits.png)

`./kd try --on cov2-save-finished@148830 --frames 60 --patch '13:B55E=$7D' --patch '13:B58B=$BF' --png unused/bank_ends-credits.png`

13:BF7D (`old_13_credits_2`) is an older copy of the second page of staff names in the demo that ends the game. It
reads SPECIAL THANKS TO / HALKEN DEBUGGERS / NINTENDO DEBUGGERS / CLAUDE M. MOYSE. The released page shows DAN
OWSEN in that row, and nothing else differs. The page before it (13:BF23) is a byte-for-byte copy of the live first
page. Both copies sit $B1 bytes after their live versions. Claim `bank_ends.credits.copy`.

Claude M. Moyse wrote for the German *Club Nintendo* magazine, including the 1996 Kirby comic *Kirbys Grösster Fall*
([Kirby Wiki](https://kirby.fandom.com/wiki/Kirby%27s_Biggest_Case)). Together with the German texts below, this
suggests the older build was a German localization, crediting its translator where the US release credits its
own. That reading is an inference from the ROM. Whether a released European version shows the name is not
checked here, because the project has only the US ROM.

### German pause texts

![ZEPTER](unused/bank_ends-zepter.png)

`./kd try --on cov4-d-pause@2990 --frames 80 --patch '38:B45C=$63' --patch '38:B477=$BF' --png unused/bank_ends-zepter.png`

Bank 38's end holds two texts and a routine from the older build:

- 38:BF21: the end of a German version of pause text 24, "Nun kannst Du auf [4] verschiedene Arten angreifen".
- A complete packed text for the Star Rod: ZEPTER, "Das magische Sternzepter bekämpft die schlimmsten Alpträume, die
  man sich denken kann". The font has no ä, and tile $C5 draws as a red bar.
- `pause_unpack` with its jump pointing $43 bytes higher.

Bank 35's end keeps the last 18 bytes of an older minigame menu stream, where the live one says QUIT and this one
says …ASSEN (VERLASSEN?). Claim `bank_ends.pause_de.patch`.

### An older swim stroke

18:B699 is a 751-byte older copy of 18:B3AA-B698: the swallow scripts, the mouth-full water states, the swim gravity
and the bump. Apart from relocated addresses, one value differs. A swim stroke with the mouth full set Kirby's
vertical speed to $FF1A (-0.90 px per frame), where the released game uses $FF40 (-0.75). Claim
`bank_ends.kirby18.copy`.

Other older copies:

- the ending's palette and fade code, with THE END (2E:BC3D);
- the rematch tables (3D:BF57);
- a sound-frame helper (3F:F8E7);
- `obj_land_old` (3F:F0A2), the object landing test as one routine, before it was split into bank 22's
  `obj_test_land` and `obj_floor_approach`. It accepts any distance of 0 or more as landed (now 0-8), and has no
  8-pixel depth limit. Patched in, objects still land (`dead_sys`).

### Noise

43 regions, 22,539 bytes in all, are no code, no table and no copy. Bits of mask $55 are set 1.6 times as often as
bits of mask $AA, and even addresses have 1.6 times as many set bits as odd ones (both ratios are about 1 in the rest
of the ROM). How full of set bits the noise is changes by groups of banks. No 16-byte run of it occurs twice.
This is what uninitialised memory looks like, written into the ROM image by the build.

## Cut or unreachable

### A debug row picker in the goal game

![Goal game debug](unused/dead_kirby-goal-debug.png)

`./kd try --on main@2350 --frames 120 --patch 19:A0F5=3,0xA1 --input '.*70 A*1 .*5 A*1 .*5 S*1 .*77' --png unused/dead_kirby-goal-debug.png`

19:A103 (`goal_debug`) sits right after the jump table of the goal game's landing rows, and nothing names it. Every
frame it reads the pad:

- A and B step the landing row (0-6, wrapping);
- Select drops Kirby again on the chosen row, which then gives that row's dance and prize;
- Start ends the game.

Patched into entry 0 of the table, A, A, Select lands Kirby on row 2, and the score ends 300 points above the
untouched run. Claim `dead_kirby.goal_debug.effect`.

A similar picker for the level card (34:ACD1) steps `card_world` through 0-6 with A and B and ends the card with
Start. Nothing calls it (`dead_en2`).

### The cannon's other shots

![The cannon flies off](unused/dead_en1-cannon-3.png)

`./kd try --on cov3-a-cannon@60470 --frames 265 --patch '23:A6E7=3' --png unused/dead_en1-cannon-3.png`

The cannons have four shot kinds. Kind 0 fires Kirby up, and kind 1 fires him diagonally (world 6; fired in
`cov9-b-cannon`, see the last section). Two kinds can never be fired:

- Kind 2 fires him straight right, and no cannon is given kind 2.
- Kind 3 makes the cannon itself fly off, with no Kirby in it. Only an object kind that no room lists would use it.

Claims `dead_en1.cannon.kind2` and `kind3` (kind 1's patch claim is now `cov9.cannon_kind1_patch`).

![Kind 2](unused/dead_en1-cannon-2.png)

### Crane Fever: the sixth layout, and the claw with its doll

![Layout 6](unused/dead_sys-crane-layout6.png)

`./kd try --on cov-minigame-crane@3400 --frames 200 --patch '3B:B6EA=$A2,$14,$EA,$EA,$EA,$EA,$EA,$EA' --png unused/dead_sys-crane-layout6.png`

The crane's table of doll layouts holds all six orders of three places, but the game picks one with random(5), so
the sixth order (2, 1, 0) never comes up.

![Claw and big doll](unused/dead_sys-crane-bigdoll.png)

`./kd try --on cov-minigame-crane@3500 --frames 10 --patch '3A:89C0=$B5,$88' --png unused/dead_sys-crane-bigdoll.png`

Two pose tables (3A:87CE and 3A:88AF) draw the closed claw and its doll, small or big, as one picture. The game draws
the claw and the doll as two separate objects instead.

### Quick Draw's hats as background tiles

![Hats as tiles](unused/dead_sys-qd-marks.png)

`./kd try --on cov-minigame-quickdraw@39900 --frames 2140 --patch '3C:ABD4=$4C,$E5,$AB' --png unused/dead_sys-qd-marks.png`

3C:ABE5 would draw one 2x2 hat for each decided round, as background tiles on the ground. The game draws its hats
as sprites (on the right). The fifth tile hat's tiles are not in the loaded graphics and show as boxes.

### Star Rod states no ability reaches

The Star Rod has a complete set of states for water, a ladder, dropping through a thin floor and bouncing after a
dive breaks a block (21:8DA5 onward). Each is a copy of the Hammer's state in the same place, with the rod's poses.
The rod is held only in the last fight (rooms 15 and 16), which has no water, ladder or thin floor. The same
states of the Sword, the Hammer and the Parasol were played in the ninth batch (`cov9-b-sword`, `cov9-b-hammer`,
`cov9-b-para`). The one real change is in the rod's middle water-walk cycle, which steps
up twice and down twice, where the Hammer's steps up three times and back by 6.

![Rod ladder](unused/dead_kirby-rod-ladder.png)

`./kd try --on cov4-c-hammer@91690 --frames 12 --patch 21:8DA5=0xF5 21:8E94=0xA6 --png unused/dead_kirby-rod-ladder.png`

Hammer Kirby on a ladder, running the rod's ladder state. The rod's pose numbers are drawn with the Hammer's sprite
map.

### Branches the code itself rules out

The tenth batch's triage sorted every one-sided branch of the corpus. Some cannot go the other way by the code alone
(static verdicts, each checked against the ROM by a claim of unit `cov10`):

- **Up at a door in 29 of Kirby's states**: where `pad_up_held`, `pad_a_up_held` or `swim_stroke_test` comes earlier in
  the chain, Up has already taken its exit before `pad_up_door` asks (falling, diving, floating, standing and walking
  in water, for every ability family; `cov10.up_before_door`).
- **The UFO at a door**: its door test needs Up held with no direction, which only Up + Down or Up + Left + Right give,
  and `joypad_store` drops both pairs before anything sees the pad (`cov10.ufo_door`). The drops themselves (3E:C2E8,
  3E:C2F6) are reachable on hardware with a pad that reports opposite directions; the emulator the movies are made with
  filters such pairs, so they are only unplayable here.
- **The sleeping Noddy's distance test** (25:AC4C): it needs variable 3 at 0 while variable 2 is not, and the frame that
  takes variable 3 to 0 is the frame variable 2 reaches 0, which wakes it first (`cov10.noddy_dead_test`).
- **A spin with no rectangle**: the high bytes of the Sword's, the Star Rod's and the Hammer's spin rectangle tables are
  never 0 (`cov10.spin_rects`). Also always one way: `hub_pan_setup` comparing |dx| with itself, a `beq` after
  `lda #$00` in `room_pick_kind`, and a sum in the sound engine that cannot carry (`cov10.hub_pan_same`,
  `cov10.room_pick_beq`, `cov10.snd_no_carry`).
- **The lunging squid in water**: only rooms 158 and 245 place it (`cov10.lunger_rooms`); 158's sits on the top row and
  leaves the room upward, and 245 has no water.

The eleventh batch's triage (banks 23-2F) found more, each checked by a claim of unit `cov11`:

- **A branch right after a load that sets its flag**: `lda #$00` / `beq` in `e12_slope_test` (24:AA6D), `lda #$78` /
  `sta` / `bne` in the saucer's `e24_tick_fly` (2B:A156), `ldy #$01` / `bne` in the mane's `e4d_grip_pose` (2A:A807),
  `ldy #$FE` / `bne` in Kracko's `e3d_glide_start` (2F:A66B), `and #$03` / `bpl` in Paint Roller's `e44_pick_route`
  (2C:A1FF), and `random(2) + 2` / `bne` in `e4c_pick` (28:A460), which is never 0 (`cov11.static.*`). The code
  behind two of them, the saucer's far-in-height pass and Paint Roller's random-bit pick, is reached by other branches
  and was played (below).
- **Kracko's floating rows 0 and 8**: `e3d_choose` sends a floating Kirby above Y $61 to row $10 before it picks the
  side's routine, and nothing between changes the three bytes it tests, so `e3d_choose_0` and `e3d_choose_1` repeat a
  test that can no longer pass: rows 0 and 8 of `e3d_choices` are never drawn (`cov11.choose_float_dead`).

### Smaller things

- 22:9385: a script subroutine that writes an object's countdown into the lives counter every frame. Patched in, the
  HUD counts down from 60 (`dead_en1.lives_count.run`).

  ![Lives countdown](unused/dead_en1-lives-count.png)
- 21:816F: a second slope table, entry n = 16·n·2/√5, the speed along a 1-in-2 slope. Nothing reads it. Pointed at, it makes Kirby run further up a 45-degree floor (`dead_kirby.slope2.table`).
- The end of the Invincible Candy (the music comes back and the palette fades): a script nothing reaches. The grab
  throws that end at a ceiling ($E7) or in water ($E1) are different: states do enter them, by an ordinary
  `water_entered` test in each throw's chain (16:A739-16:A98C) and a ceiling test in `kirby_st_drop_a` (16:A936); no
  movie threw anything into water or against a ceiling. The hurt Kirby falling into water ($EB) was played in the
  tenth batch (below).
- Routines in the fixed bank that nothing calls: one counts an object's script threads (3E:D74C), and another,
  `obj_thread_nth`, has a bug: it overwrites its counter after one step.
- Script opcodes that no script uses: `add_e2`, `add_z`, `call_table_far`.
- An older 3x4 gravity table for Egg Catcher's eggs, a simpler camera for the crane, three Quick Draw parts that
  nothing creates, two type $0D effects, and sprite groups drawn mirrored where the draw routines mirror by
  themselves.

## Reachable, and now played

The eleventh batch (unit `cov11`, 21 movies): **rooms no movie had loaded**: the arena chain behind room 113's lower
door (rooms 114-126, with the class-0 turtle, shell, beetle and mane mid-bosses), room 62 under room 61's water (the
shell mid-boss), room 209 behind a bomb block (a Grand Wheelie whose small wheels roll into walls and vanish) and room
301 (the only class-0 mane in a stage room, with its flame hop). **Enemy moves no movie had seen**: the lance knight's
thrown spear (an arcing throw whose hit record sits in bank 27 instead of 39; `cov11-b-lleap`), the axe knight's
jumping throw with Kirby above it (`cov11-b-lance`), the trident knight's hop back off its ledge (`cov11-b-trident`),
a dashing axe knight turning at the screen's edge (`cov11-b-axedash`), the fleeing fish's second script and the
chasing fish resuming the chase after a pause, the runner leaping off the top of the screen after its third change of
side (`cov11-c-runner`), the mane bouncing off a wall out of its burning dash (state 10, `cov11-c-mane`), the shell
mid-boss landing after a bounce and rocking, the last boss's tenth placement and the reversed star burst of attack 0
(`cov11-c-wiz`). **The bosses**: Kracko's mirrored lightning sweep and attack 2, its slide across the screen (state
1) and its choice while Kirby floats (`cov11-d-kracko`); King Dedede's low-hp jump speed, his flight at the upward
limit and Kirby on his right at swing 2 (`cov11-d-ddd`); a slide into Heavy Mole knocking Kirby back (`cov11-d-mole`);
Paint Roller's random-bit route (`cov11-d-paint`).

The tenth batch (unit `cov10`): **a hurt Kirby falling into water** (the splash, then the end of the hurt;
`cov10-a-pool`), and **the walking squid's life in water** (`cov10-c-squid`): in room 158 a walker that walks off the
pier sinks, bobs up, leaps out toward Kirby and walks on the pier again. With them, exits of Kirby's states that no movie
had taken: the Parasol at doors, the dive bounces' buttons, the Hammer's flap and puff into the sea, Ball Kirby into the
ceiling, Up in the Star Rod's dive, the Star Rod's flight ending during a shot.

The ninth batch: these were listed here as features of the released game that no movie had reached. The ninth
batch of coverage movies played them, and unit `cov9` documents them from the evidence:

- **The Warp Star Stations** (rooms $1E-$24): `cov8-warp-star`, a ride from world 1's station to world 0's (unit cov8).
- **The cannon's diagonal shot** (kind 1) in 7-5's room $A6: `cov9-b-cannon` fired it, and Kirby flew up and to the
  right into room $A7 with the camera following in both axes. The movie's maker noted that a fuse spark left far
  behind the camera vanishes and the cannon then never fires.
- **Sixteen of the pause screen's ability texts** (Spark, Cutter, Sword, Laser, Mike, Sleep, Needle, Ice, Freeze,
  Ball, Tornado, Crash, Light, Back Drop, Throw: `cov9-a-rocky`; the Star Rod, in the last fight: `cov9-a-w7card`).
  The Needle text writes "It's" with the font's lowercase l, which in this font looks nearly the same
  (`unused/dead_sys-pause-needle.png`). Only entry $1A of the table (Sword's text again) is never read.
- **Kracko steering at a Kirby who floats** for 120 frames during the climb: `cov9-b-kracko` (the UFO dropped).
- **The scene before the last fight**, which every movie had skipped with a button: `cov9-a-w7card` played it out
  into the last fight. The rest of World 4's card too (`cov9-a-rocky`, after a CONTINUE).
- **Dropping through a thin floor** with the Parasol (`cov9-b-para`), the Sword (`cov9-b-sword`) and the Hammer
  (`cov9-b-hammer`), and the Parasol's dive bounce. The Star Rod's drop stays unreachable (above).
- **THE END's second set of twinkles**, 10,205 frames after the screen begins: `cov9-a-theend`. Nothing ends the
  screen.
- **B on the file select's file list**: state 2 is the ordinary list, which every start of a game passes;
  `cov9-a-fselb` pressed B there and the box lowered back to the title.
- **King Dedede's swing 2** (Kirby floating high when he comes with the hammer: a high leap) and his hurt reaction
  during the flight: `cov9-b-ddd`.
- **The Cutter's blade bouncing off a wall** (16:B611, hops back under gravity, spins at a quarter speed:
  `unused/dead_kirby-cutter-wall.png`) and **the end of Sleep** (Kirby wakes and loses the ability): `cov9-a-rocky`.

### Kracko's floor breaker and walker

![Kracko breaks the floor](unused/dead_en2-kracko-floor.png)

`./kd try --on main@59700 --frames 150 --input ".*150" --poke 620F=7 079E=0xC8 079F=0 07A1=0xE8 07A2=7 --png unused/dead_en2-kracko-floor.png`

The static round said nothing stores Kracko's state 7. Something does: at the end of each dash (state 6) the eye
takes state 7 when its variable 8 is set, and the charge sets it when Kirby stands on a floor as the charge begins.
In `main` Kirby climbs as the UFO and never stands; `cov9-b-kracko` (the UFO dropped) stood on the cloud floor and
played it (claim `cov9.e3d_dash_state7`). The picture is the poked run of the static round, from `main`:

1. The eye flies back to where Kirby was when its last charge began.
2. It shakes and creates a block breaker.
3. The breaker erases the two-block column at that point, then every block of those rows to the left and right.

The claim sees 32 blocks of the cloud floor go. States 9 and $0A belong to the same path. Claim
`cov9.e3d_point_poke`. In `cov9-b-kracko` the point lay more than a screen below the camera when the breaker came:
it emptied the two-block column there, and its left and right halves freed themselves at once (off the screen), so
only that column went.

![Kracko's walker](unused/dead_en2-kracko-walker.png)

`./kd try --on main@60750 --frames 100 --patch 2F:B085=4 --png unused/dead_en2-kracko-walker.png`

Kracko's attack choice for a long fight (2F:B0D6) and its attack 4, a small walker dropped from the cloud (at most two
at a time), were played in `cov9-b-kracko`; the picture is the patched run of the static round. The mirrored lightning sweep,
with the X speeds negated, was played in the eleventh batch (`cov11-d-kracko`, from frame 62673).

