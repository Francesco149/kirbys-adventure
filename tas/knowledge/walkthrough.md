# Kirby's Adventure — walkthrough (agent-facing)

Grep keys: `## World N`, `### N-M`, `### Boss`. "rooms" = room IDs in `$055E/$055F`, from the RA/Data Crystal tables (hex, 16-bit), side rooms included. Room order and contents come from WiKirby per-stage pages (WK) and StrategyWiki (SW). Exact per-room route inputs are in speedrun.md. "Opt" = optional for any%.

## Start: power-on → first stage
1. **Cold boot**: HAL logo (slot-0 script `$68`), then the "Drawing Song" intro (Kirby being drawn), then a camera pan down to the **title**. With no input the title appears at about frame 561 (LOC runtime trace, Mesen). Idling on the title plays a demo, then the story.
2. **Skip**: a reset makes a warm boot, which goes straight to the title (`$07F4=0`). TASes reset on **frame 5 (FCEUX)** or **frame 3 (BizHawk)** (forum; 3226M/6389M files). JPW: reset before starting (A+B+Start+Select on hardware); it also "fixes the first enemies' movement".
3. **Title → file select → new game.** Published inputs after the reset:
   - 3226M (FCEUX, PRG0): Start (+A+B) at f65, Start f99, Start f214. In the hub: Left f393-417 with Up on f413 and f415-417 (enter the 1-1 door). Right from f459 (in 1-1).
   - 6389M (BizHawk, PRG0): reset f3; Start f63, f97, f212; Left f400-414; Up f415; Right from f479.
   - So: title Start at reset+60, file-select Start at +94, third Start at +209 (probably the new-game/intro confirm; on-screen meaning **unverified**). The hub spawns Kirby right of door 1: walk left and press Up.
   - Timings will differ by a few frames on Rev A, so re-find them by brute force.
4. **File select**: 3 battery files (each shows % and progress) plus Delete. Use **file 1** (JPW) on a **clean SRAM**: TASVideos movies start from clean SRAM. The harness must delete the .sav before every run. A cleared file shows Main Game / Bonus Games / Extra Game.
5. A **new game** plays the Vegetable Valley intro (Kirby duels a Blade Knight), then the Warp Star drops Kirby in the hub. Every world has a first-visit intro. Skippability: not documented; the TAS presses Start once (f214).
6. Pause (Start): shows the ability text. In a **cleared** stage it offers exit to the map (used by the pause carry-over).

## Global rules
- Stage doors unlock one at a time in order. Clearing a stage plays a door-opening cutscene; resetting can be faster (9286S).
- Boss door: appears after all stages of the world are cleared. Beating the boss sends Kirby to the next hub automatically.
- **Any% needs every regular stage + boss of worlds 1-7, then the Fountain of Dreams fights.** No switches are needed. 100% = all 17 Big Switches + game clear.
- Hub extras, one line each, **all Opt**:
  - **Museum**: pedestal enemies to swallow for a free ability. RTA uses 5-1's museum for Tornado/Stone.
  - **Arena**: mid-boss fight; win = Maxim Tomato + ability.
  - **Warp Star Station**: warps between worlds.
  - **Mini-games**: Crane Fever, Egg Catcher, Quick Draw; each can be played once.
  - **Switch** doors (100% only).
- Pressing **Up when a room starts** sends you back through the door (JPW).
- Every non-boss stage ends with the **Goal Game** (spring): press A/B on the first frame of the 36-frame window (see mechanics.md).

## World 1: Vegetable Valley
Hub (room 00) opens left to right.
- Clear 1-1 → Crane Fever; clear 1-3 → Museum (Sword); clear 1-4 → boss door + Warp Star Station.
- No switches, no Arena.

### 1-1
- Rooms 2B-2E. Order:
  1. Plains, with the first ability enemies.
  2. Waterfalls over pits, thin floors.
  3. Pool (Maxim Tomato at the bottom) → exit.
- Enemies: Bronto Burt (2 stacked), UFO → UFO, Hot Head → Fire, Waddle Dee, Poppy Bros. Jr., Waddle Doo → Beam, Sparky → Spark.
- Hidden door under the leftmost waterfall block → UFO enemy. Opt.
- TAS: room 1 inhale 3 → mix UFO; UFO glitch before leaving room 1.
- Credits warp (GEG): slope clip into the room-3 pool + Stone.

### 1-2
- Rooms 2F-34. Order:
  1. Walkway with invincible Shotzo and Gordo; Warp Star at the end.
  2. Warp Star ride → slope → drop into the **Poppy Bros. Sr.** arena (mandatory, gives Crash; HP 30).
  3. Half-flooded cave; take the upper door (the lower branch has a Tomato behind star blocks).
  4. Switchback climb to the exit (Sword Knight, Cappy).
- Abilities: Sir Kibble → Cutter, Sword Knight → Sword, Sparky, Hot Head, Waddle Doo; Shotzo and Gordo are invincible.
- TAS note: a 3rd enemy can appear in the Warp Star section and cause lag (5227S).

### 1-3
- Rooms 35-38. Order:
  1. Field with Shotzos on star blocks; a Kabu blocks the door.
  2. Encased Flamer → Fireball; waterfalls over the abyss.
  3. Winding drop into a pool; swim to the dry door.
  4. Rocky deck (Tomato underneath) → exit.
- Abilities: Flamer (Fireball), Sparky, Waddle Doo, Hot Head.

### 1-4
- Rooms 39-3C. Order:
  1. Ladder up to **Mr. Frosty** (mandatory; Freeze; HP 20; spit his ice blocks; the door appears after).
  2. Log bridges.
  3. Climb inside a hollow trunk (Spiny → Needle).
  4. Canopies (Meta Knight drops an Invincible Candy; 1-Up) → exit.
- Abilities: Blade/Sword Knight (Sword), Sparky, Spiny (Needle), Waddle Doo.

### Boss: Whispy Woods (1-5, room 08, HP 60)
- Drop through the wooden platforms to the ground.
- Pattern: stationary; Air Bullets and falling Apples (inhale an apple and spit it back).
- Fastest: UFO piercing shot point-blank while moving toward him ("Doppler"), then a star shot (JPW). Spark/Freeze against the trunk without UFO (SW).
- Take the Star Rod piece from directly above. The dance plays, then the Ice Cream Island hub.

## World 2: Ice Cream Island
Hub (01): small at first, grows up and right. Boss door in the castle at the right end.
- Unlocks: 2-1 → Egg Catcher; 2-2 → Crane; 2-3 → Museum (Fire, Laser); 2-4 → Arena (Mr. Frosty); 2-5 → boss door + Warp Star.
- Watch for re-entering earlier doors by accident (JPW: don't enter the 2-1 door on the way to 2-2).

### 2-1
- Rooms A9-AC, visited 169 → 170 → 172; 171 is a grotto side room behind the side door in 169 at (584,137) (measured in w2-seq). Order:
  1. Shore with falling, exploding Coconuts (grotto side room: Pep Drink, Parasol Waddle Dee).
  2. Beach: Sword Knight, Bomber → Crash.
  3. Log path: Twister → **Tornado** → exit.
- Scarfy explodes if you try to inhale it; it chases you.
- JXQ 701M took Wheel here for 2-2's ladder.

### 2-2
- Rooms AD-B1. Order:
  1. Small room, 2 enemies.
  2. A bomb block opens the way.
  3. Warp Star.
  4. Desert with encased Sword/Fire/Spark enemies; **Grand Wheelie** (mandatory; Wheel; HP 25). Autoscroll into his arena: hold only Down (JPW).
  5. → exit.
- A ladder here can't be descended by UFO (JXQ).
- Softlock: Grand Wheelie may not appear if you advance while the Hot Head and Sparky on the left cause lag (JPW).

### 2-3
- Rooms B2-B7. Order:
  1. Two landmasses.
  2. Winding red cave, partly flooded, with spikes. Left: a bomb-block wall → **UFO side room** + Tomato (open it with Beam, or Sword from the leftmost star block). Ceiling bomb block → 1-Up.
  3. **Meta-Knights** ambush (mandatory; shared HP bar; door appears after).
  4. Pond (2 Blippers) → exit.
- Glitch spot: stone glitch in a tight bottom passage that re-enters water from the side (3411S). Ladder clip (9286S). Pause-glitch skip in room 2 (JPW).
- Don't break the leftmost star block in room 2, or the bomb block can't be broken (JPW).

### 2-4
- Rooms B8-BE. Order:
  1. Cloud-tops (1-Up side room; Tomato in an overhead star-block cache).
  2. Parasol/Fire/Stone enemies, then **Mr. Tick-Tock** in a pit (mandatory; Mike; HP 25; spit his notes).
  3. Cloud steps past Scarfies.
  4. Laser Ball (bounce the laser off a slope into a ceiling bomb block → 1-Up).
  5. Beach with pits → exit.
- TAS: RNG for 4 enemies here is set up in 2-3.

### 2-5
- Rooms BF-C5. Order:
  1. Water-level forest (Shotzos).
  2. Beach with Wheelies; take the **upper door** (the lower path is a snack room).
  3. Clouded walkway (an arched window → Flamer side room).
  4. Cloud chute: Starman → Hi-Jump; star-block grid; Bombers.
  5. Cloud platforms (Poppy Jr. riding a Tomato) → exit.

### Boss: Paint Roller (2-6, room 09, HP 60)
- One room: floor, 2 upper decks, 4 canvases. He skates to a canvas and paints an object that comes alive:
  - Ball → Ball; Bomb → Crash (one use, kills half his HP); Car → Wheel; Cloud → Spark; Mike → Mike; Parasol → Parasol; Kirby/Waddle Dee → nothing.
- Touching him hurts; crouch to avoid it. He speeds up at low HP.
- Fastest (UFO): 2 piercing + 1 star shot; the first from the right, the rest from the left (JPW). Tap Up alone briefly on the hub to avoid the 2-5 door.

## World 3: Butter Building
Hub (02): vertical; each door is above the last, boss door at the top.
- Unlocks: 3-1 switch → Arena (Grand Wheelie); clear 3-3 → Museum (Hi-Jump); 3-4 → Quick Draw; 3-6 switch → Egg Catcher; clear 3-6 → boss door + Warp Star.

### 3-1
- Rooms C6-CB. Order:
  1. Tower base, Bomber.
  2. Ceiling opened by a bomb (2 Rockys above).
  3. **Mr. Tick-Tock** (mandatory; Crash kills him fast).
  4. Double bridges: start on the lower one; the exit is visible but unreachable.
  5. Blue-walled room (Pep Drink); a door above returns to the upper bridge; the exit is left.
- Switch: Opt.
- RTA: room-4 pause glitch skip (Any%). UFO recovery mix from 2 Parasol Waddle Dees: slot 14.
- MUGG corner clip: 3F.

### 3-2
- Rooms CC-D2. Order:
  1. Tall room (Poppy Jr. carrying a Tomato at the top).
  2. Spinning tower balcony; the door appears near the right edge.
  3. Vertical cave with falling Rockys.
  4. Long spike road (opt side passage: Grand Wheelie).
  5. Two Pengys (bomb blocks; crumbling floor).
  6. **Bugzzy** (mandatory; Backdrop; HP 30; spit his 2 ladybugs). Exit right after.
- TAS: a slope-room clip forces losing UFO (TASeditor). Enemy-spawn prevention found here.
- RTA: pause glitch in room 4 (+3.7 s, costs 1 HP); damage boost (+0.5 s).

### 3-3
- Rooms D3-D7. Order:
  1. Up-and-down hallway, Bronto Burts, Starman → Hi-Jump.
  2. Spinning balcony.
  3. Two mirrored door rooms: 3rd door from the bottom = 1-Up; the highest reachable door (past the star blocks) → next to the exit.
- JXQ: inhale enemies while falling so the Hi-Jump enemy can spawn (sprite limit).
- MUGG corner clip saves 265F.

### 3-4
- Rooms D8-DD. Order:
  1. Warp Star up the tower.
  2. **Meta-Knights** (mandatory).
  3. Thin-floor room.
  4. Updraft column (inflated Kirby rises fast) → exit at the top.

### 3-5
- Rooms DE-E2. Order:
  1. Invincible Candy.
  2. Spinning tower.
  3. Short hall going left.
  4. **Bonkers** (mandatory; Hammer; HP 27; spit the stars from his hammer and his coconuts).
  5. Stake room → exit.

### 3-6
- Rooms E3-EB. Order:
  1. Trapped Laser Ball.
  2. Sloped hallway (Bombers).
  3. Brick climb (Tomato).
  4. Rotating exterior (room 230): the exit door appears only after the tower rotates; wait in place (a random search with `.*30` waits found it, w3-sonnet).
  5. Cloud steps outside the tower (switch side door, Opt).
  6. Dark hall: Cool Spook → Light.
  7. Narrow tower climb (Starman) → exit at the top.
- 3-6's lasers reflect from the ground (TASeditor).

### Boss: Mr. Shine & Mr. Bright (3-7, room 0A, 30+30)
- One is in the sky and invulnerable; the grounded one is the target. They swap.
- Inhale the sky one's stars: Shine's → Cutter, Bright's sunbeam → Fire. Crouch under Shine's charge and cutter.
- A defeated one stays in the sky attacking.
- UFO: pattern A = PS, SS, SS, move close, PS; pattern B = PS, SS, PS, SS (JPW; which you get is unclear).
- Without a kept UFO: inhaling both Shine's and Bright's stars and swallowing them can roll UFO (1307S forum: UFO "at the third boss").

## World 4: Grape Garden
Hub (03): large; doors in palace towers and on platforms.
- Unlocks: 4-1 switch → Crane; clear 4-2 → Quick Draw; 4-3 switch → Museum (Sleep, Ball); Arena (Bugzzy) after 4-3 (WK) or 4-4 (SW); 4-6 switch → Warp Star.

### 4-1
- Rooms EC-F1. Order:
  1. Broken cloud walkway.
  2. Stacked soft clouds (Needle).
  3. Starry room with a **UFO** enemy (appears twice).
  4. Night area: Bubbles → Ball; star-block grid with the switch door.
  5. Winding tunnel → exit.

### 4-2
- Rooms F2-F7. Order:
  1. Outside the castle; blow the bomb on the left.
  2. Small room, Poppy Jr.
  3. Labyrinth with pools (upper door onward).
  4. Spike hall (Pep Drink on the upper route).
  5. **Twin Poppy Bros. Sr.** (mandatory; 30 each; Crash from the first kills the second) → exit.
- TAS: 31 of the World-4 lag savings (35 frames) came from 4-2 room 3. Slope clip used here (9286S).

### 4-3
- Rooms F8-FE. Order:
  1. Fuse cannon (Opt 1-Up).
  2. Windy blimp sky (wind pushes right); middle bottom door onward.
  3. Propeller hall, Bomber, Warp Star.
  4. Cloud steps with Laser Balls → exit.
- Pause-glitch wrong warp → level-4 hub exists (useless).

### 4-4
- Rooms FF-103. Order:
  1. Straight path (turbines).
  2. Platforms over a pit.
  3. Slopes down (race a bomb-block spark with Wheel → 1-Up; both doors converge).
  4. Fire/Spark enemies, then **Rolling Turtle** (mandatory; Throw; HP 30).
  5. Tunnel → exit.
- TAS: slope clipping first used here (48 frames). JXQ: dropping UFO for Wheel was slower.
- Recovery UFO mix from 2 Parasol Waddle Doos: slot 14 (JPW).

### 4-5
- Rooms 104-10A. Order:
  1. Meta Knight's Candy; Stone; right door onward.
  2. Stairs to the palace.
  3. **Meta-Knights** (all 4 types).
  4. Tall hall: Flamer → Fireball.
  5. Hall of Gordos over spikes → exit.
- TAS: Fireball in the last room ("creates a lot of lag, but the position gain is still bigger").

### 4-6
- Rooms 10B-110. Order:
  1. Watery hall with bomb blocks (take the lower door).
  2. **Mr. Tick-Tock** (mandatory).
  3. Dark hall with a Cool Spook (switch door left of a pillar, Opt).
  4. Back in room 1 near the top door.
  5. Stake room with a Rocky.
  6. Short climb → exit.
- MUGG 2026 corner clip: **1132 frames** saved here. JPW "Burning clip" TAS route.

### Boss: Kracko (4-7, room 0B, HP 60)
- Phase 1: Kracko Jr. (invulnerable) chases while you climb clouds with **Hi-Jump** (swallow a Starman). Jr. destroys clouds if you linger; falling = death. RA `$051C=1` here.
- Phase 2, Kracko: swoops, eye beam, sweeping lightning (fly above him when he moves sideways), drops Starmen.
- Kill: UFO — keep going straight up, move to the left edge at the 1st Starman, 3 piercing shots (JPW). Otherwise Hi-Jump into him or spit Starmen.

## World 5: Yogurt Yard
Hub (04): vertical canyon.
- Unlocks: 5-1 switch → Crane; clear 5-1 → **Museum (Stone, Tornado)**; 5-3 → Egg Catcher; 5-4 switch → Arena (Bonkers); 5-5 switch → Quick Draw; 5-6 switch → Warp Star.

### 5-1
- Rooms 111-115. Order:
  1. Clouds with Shotzos (right door straight on; a door under a nearer cloud leads to a detour room with 1-Up + 2 Rockys → Stone).
  2. Long fall past enemies; land on a star-block walkway with a door.
  3. Ground deck, Pengys → exit.
- RTA: Tornado mix from 2 Rockys = slot 2; leaving the roulette alone = UFO.

### 5-2
- Rooms 116-11C, interleaved; can't be done as UFO (water, ladder). Order:
  1. Grotto.
  2. Flooded cave (ignore the upper doors).
  3. Scarfies/coconuts.
  4–6. Corridors.
  7. Ladder → **Bonkers** (mandatory) → back outside, slope → exit.
- Skips: MUGG's wall clip (+827 frames over TASeditor's prior route). Sword clip skips most of the stage (TAS). Ladder clip. Pause glitch in room 3 (JPW). The speedrun.com OOB clip saves "15-20 s".

### 5-3
- Rooms 11D-122. Order:
  1. Tall ascent past Shotzos (Hi-Jump).
  2. Wind shaft (inflate to rise).
  3. Wheel road, spikes near the end.
  4. Star-block bridge (Stone room).
  5. Spiky zigzag down → exit.
- TAS: at the end you must touch an enemy to keep UFO, or it's lost on the map. Kept UFO is pink.
- Speed bug after UFOing up an incline (701M notes).

### 5-4
- Rooms 123-129. Order:
  1. Spike tunnel.
  2. **Meta-Knights**.
  3. Cliffs and waterfalls: the door disguised as a water conduit → cave whose upper door goes onward and **skips room 4**.
  4. Gordo river (skippable).
  5. Long waterfall fall → exit at the bottom.
- RTA: tank 3 hits in room 5 (faster).

### 5-5
- Rooms 12A-130. Order:
  1. Logs over an abyss.
  2. Warp Star.
  3. Castle exterior.
  4. **Fire Lion** (mandatory; Fireball; HP 27).
  5. Wooded path → exit at the bottom.
- RTA/TAS: acute-angled ledge clip in room 3 skips to room 6 (JPW). A UFO-compatible 5-5 clip was "335 frames faster" (TASeditor).

### 5-6
- Rooms 131-135. Order:
  1. Ramps full of Wheelies.
  2. Race the bomb-block barrier while Rockys fall.
  3. Beach → islet door → flooded room; the exit is a few steps right.

### Boss: Heavy Mole (5-7, rooms 0C/0D, HP 60)
- Autoscroll tunnel; he digs right with erratic moves; falling behind = crushed. Spiked arms hurt.
- Rear missiles: red (eye closed) → Sleep, avoid; yellow (eye open) → Hammer.
- UFO: 2 PS + 1 SS, the 1st from the left edge, the 2nd while closing in (JPW).
- After the kill you are moved to room 0D for the piece (special exit, ROM `$055E=$0C` check). JP version refills HP here.

## World 6: Orange Ocean
Hub (05): doors along the bottom; every stage has a switch.
- Unlocks: Museum (Wheel), Arena (Fire Lion), Crane, Egg Catcher, Quick Draw, Warp Star, all via switches.

### 6-1
- Rooms 3D-42. Order:
  1. Big pool (side door: Rolling Turtle).
  2. Platforms, each with a Flamer + another ability enemy (mix pairs).
  3. Narrow islands → exit.
- The block under the mid-boss room's door can become water → stone glitch / rare credits warp.

### 6-2
- Rooms 43-49. Order:
  1. Stones past a waterfall (bomb block, hidden 1-Up/Rocky).
  2. Sky pillars, Bomber.
  3. Tunnel to a garden (short-lived UFO, Tomato).
  4. Treetops over a pit → exit.
- RTA: pause glitch in room 2 (about 7 s).

### 6-3
- Rooms 4A-55. Order:
  1. Shore, crates, board the ship.
  2. **Bonkers** → ladder.
  3. Mast-side door.
  4. Masts → Warp Star.
  5. Island → exit.
- MUGG corner clip: 144F, saves 1 HP.

### 6-4
- Rooms 56-5B. Order:
  1. Split path.
  2. Watery tunnels.
  3. Two Parasol wielders.
  4. Shaft past falling Coconuts.
  5. Coconut hillside → exit on an islet.
- Clips: TAS clip about 70 frames faster (TASeditor); MUGG 212F. RTA pause glitch in room 2 (about 12 s).

### 6-5
- Rooms 5C-60. Order:
  1. Icebergs.
  2. Tall climb (Tomato).
  3. Ice tunnel (a bomb block floods it).
  4. Grey hillside with detonators → exit at the top.
- MUGG corner clip: 79F.

### 6-6
- Rooms 61-6B. Order:
  1. Icy cliff.
  2. Space room full of UFOs.
  3. Bomb block, then a fork: upper = 2 Poppy Sr. (SW-recommended); lower = 2 Mr. Frosty.
  4. Paths rejoin.
  5. **Meta-Knights** on a slippery floor → exit.

### Boss: Meta Knight (6-7, room 6C, HP 60)
- Touch the sword in the middle ("GET IT!"); it replaces your ability. Sword is forced.
- He blocks, Down Thrusts, and uses a Sword Spin / Upward Thrust if you stay airborne. He is briefly invulnerable after each hit.
- TAS:
  - He can be hit "each 32 frames, instead of 54": get him in a corner, dash attack, then an immediate aerial attack (TASeditor).
  - Manipulate fewer blocking pauses (JXQ). About 20 frames are available from damage-boost slides (keyword).
  - 0xwas's NMG 100% run had a notably faster fight.
- Afterwards wait directly above, drop after he flies off, and catch the piece (JPW). Beating him first try gives your old ability back (WK).

## World 7: Rainbow Resort
Hub (06): opens fully after 7-6; no Museum/Arena. Switches: 7-1 → Crane; 7-6 → Warp Star.

### 7-1
- Rooms 6D-70. Order:
  1. Dark slopes (Laser).
  2. Star-block tunnel with 90° bends (normal route via the lower door).
  3. Outdoors, Shotzos on star blocks → exit.
- Clips: slope clip and corner clip (9286S). Block room: about 1 s saved in 701M. RTA pause glitch: 2-4 s.

### 7-2 Tower of mid-bosses
- Rooms 71-8F (31 IDs, 7F-84 unused); no music.
- Main route: Poppy Sr. → Tick-Tock → Frosty → Bonkers → Rolling Turtle → Bugzzy → Fire Lion, then out the top to a Warp Star → exit.
- **Hidden door** at the start (upper tower) → only 4 fights (Bonkers, Turtle, Bugzzy, Fire Lion) → rejoins the main path. The RTA route takes it (JPW).

### 7-3
- Rooms 90-93. Order:
  1. Starry walkway (Noddys → Sleep).
  2. Icy diamond climb.
  3. Meta Knight's Candy, ice.
  4. Rocky path past waterfalls → exit.
- **Avoid coasting over ice hill tops** (speed cap bug, JXQ). Recovery UFO mix from 2 Noddies: slot 13.

### 7-4
- Rooms 94-99. Order:
  1. Field with Bubbles.
  2–5. U-shaped star-block halls with 4 Bubbles / Bounders / Bronto Burts / Flamers.
  6. Pillars with Gordos and bomb blocks → exit.

### 7-5
- Rooms A3-A7. Order:
  1. Hanging Bombers.
  2. **Grand Wheelie** (mandatory).
  3. Alternating up/down star currents (they push Kirby; the down ones lead into the pit).
  4. Fuse cannon (Opt); exit just right of it.

### 7-6
- Rooms 9A-A2. Black-and-white Kirby's Dream Land homage. Order:
  1. Green Greens.
  2. Woods.
  3. Castle Lololo dark hall.
  4. Bright interior.
  5. Float Islands.
  6. Tunnel maze.
  7. Bubbly Clouds (Scarfies).
  8. Palace climb → exit on the highest platform.
- Clips: corner clip (9286S).

### Boss: King Dedede (7-7, room 0E, HP 100)
- Flat arena. He hovers and chases, inhales, swings his hammer, Head Slides, and does the Super Dedede Jump. The hammer and the jump make stars to spit back.
- UFO: the fight starts when you touch the ground; 4 piercing shots from the left edge (JPW). A YouTube "Dedede manipulation" guide exists (speedrun.com).
- After the kill: drop UFO and hover or crouch (JPW), and stand still (9286S); moving delays the fade.

## World 8: Fountain of Dreams (final)
- Cutscene: Kirby plants the Star Rod; Nightmare bursts out; Dedede inhales Kirby and spits him after it. Skip the demo with A or Start (B doesn't work, JPW).

### Boss: Nightmare's Power Orb (room 0F, HP 60)
- Autoscroll flight; Kirby always has the Star Rod. Shots go straight ahead; keep left.
- Orb: 1-4 star volleys, charges, fast waves.
- A hidden time limit (sky whitening) ends in a crash that costs a life.
- You can shoot every 20 frames (+lag). Taking hits lets you fire sooner (JXQ, keyword). RTA mashes A+B and expects to take 2+ hits.
- It may softlock with screen corruption when killed (rare).

### Boss: Nightmare Wizard (room 10, HP 60)
- Normal controls with the Star Rod. Weak spot: his body under the cape, open when he stops to shoot and during the top-spin. He recoils and teleports after each hit.
- About 6 hits. Hit him as early as possible; the TAS never sees the cape-open animation (JXQ).
- JPW 6-hit plan: hit 1 at a set distance timed to the BGM; get behind him for hits 2 and 4; hover for hits 3, 5 and 6.
- Dying restarts the Wizard. Entering at low HP and dying at once can make Nightmare never appear (softlock).
- **Timing ends here**: RTA NMG ends on the last hit; TAS movies end when input stops.

## Mid-boss quick table (ability, HP from JPW)
Poppy Bros. Sr. (Crash, 30) · Mr. Frosty (Freeze, 20) · Mr. Tick-Tock (Mike, 25) · Grand Wheelie (Wheel, 25) · Bugzzy (Backdrop, 30) · Bonkers (Hammer, 27) · Rolling Turtle (Throw, 30) · Fire Lion (Fireball, 27) · Meta-Knights (no ability; Axe 6, Javelin 4, Trident 6, Mace 8; shared bar).
- Mid-bosses must be knocked down before they can be inhaled. They are immune to air bullets and slides (WK).
- RTA trick: drop your ability as the mid-boss drops its star, then inhale both for a strong bullet (WK).
