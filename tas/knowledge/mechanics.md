# Kirby's Adventure — mechanics for TAS planning

Units: speeds are subpixels/frame (256 = 1 px/frame). NTSC runs at 60.0988 fps. Sources: `GR` = TASVideos GameResources page; `JPW` = Japanese RTA wiki seesaawiki.jp/ka_rta (actions/glitches pages); `MAN` = manual; `WK`/`SW` = WiKirby/StrategyWiki; `nnnnS` = TASVideos submission notes. RAM addresses are in ram-map.md.

## Controls
- **A**: jump. In the air, tap A or hold **Up** to inflate and float. **B**: inhale. With something in the mouth, B spits a star; spitting 2+ objects gives a stronger double star. B while floating fires an air pellet and Kirby drops. (MAN, WK)
- **Down**: duck. With a mouthful, Down swallows (copy ability, or a roulette if 2+ ability enemies were swallowed). **Down+A or Down+B**: slide.
- **Double-tap L/R**: run. GR: release and re-press the direction before the speed reaches 0. Landing with speed also starts a run (JPW).
- **Up** at a door: enter. Up on ladders: climb. Up in water: swim up, also **A+direction**; B underwater = water gun.
- **Select**: drop the copy ability as a star. **Start**: pause; the screen shows the ability description. In an already-cleared stage the pause menu offers an exit to the map (WK; JPW uses this for the pause carry-over).
- **A+B+Select+Start**: in-game soft reset after 16 frames held (`$67`; LOC).
- Input is polled every frame, lag frames included (TASVideos forum, True). Inputs given during a lag frame may still be read.
- The game clears both bits of an opposite pair: L+R → neither, U+D → neither (sanitizer `$C2E0`, LOC controller-read probe: raw `$43` → held `$40`). Never brute-force opposite-direction combos.

## Normal movement (JPW actions page; GR agrees where both list a value)
- **Walk**: +32/frame on flat ground, max **332**. **Run/dash**: +32/frame, max **460**. **Release**: −14/frame. JXQ: above 460, ground speed decays −14/frame.
- **Slopes**: walk uphill 160/208, downhill 400/480; run uphill 320/352, downhill 608/704 (gentle/steep).
- **Slide**: starts at **677**, then −14/frame down to 201, then 0 on the next frame. GR gives the average as 15415/39 = 395.
  - If you slide off a ledge while holding the direction, the speed is kept until landing. Jumping on the first frame after landing keeps most of it.
  - keyword's no-ability TAS uses slide → ledge → jump chains as its main movement (9286S).
- **Jump**: Y speed starts at 880 and drops −32/frame while A is held, down to a minimum of −640 (falling).
  - Releasing A while rising freezes Kirby for 1 frame and sets Y speed to 144.
  - GR: "Every jump will cause to stop movement for one frame when A is released"; "Abort jumping: by pressing A again the jump can be cancelled"; jumping is faster than running.
  - **1-frame jump**: there is no landing sparkle, so it does not advance the RNG (GR). It is also used to turn in the air without skidding (9286S) and is the basis of the slope clip.
- **Hover (float)**:
  - Vertical: holding Up gives +80/frame to max **333**; with no input, −20/frame to −256.
  - Horizontal: +22/frame to max **192**, −9/frame decay.
  - Hovering is slow, so a TAS avoids it except where it must climb.
- **Input blocking**: B/Select are ignored while Kirby is frozen and on the landing frame (JPW).
- **Spit while moving**: holding the travel direction keeps your speed (9286S).

## Speed table by ability (X max; average in brackets)
| Movement | X | Y / notes |
|---|---|---|
| Walk / Run / Slide | 332 / 460 / 677 (395) | fall −640, hover fall −256 |
| UFO | 640, diagonal 512 (uphill 453/640) | Y 512 (diagonal 256). Flies freely, no gravity. |
| Tornado | 1024 (avg 750 = 47993/64) | Hold B to rise, release to descend (speedrun.com forum). Invincible while spinning. |
| Fireball / Burning | 1024 (avg 635 = 28576/45) | Backs up first, unless a wall is behind Kirby. Breaks metal blocks, lights fuses. |
| Wheel | 1024 | X speed depends on Y speed. Turn before hitting walls in the air (GR). Can't stop quickly. |
| Hi-Jump | 512 | Y 1024 straight up |
| Ball | 460 | Fall −1280 (fastest descent) |
| Stone / Parasol fall | — | Stone −1024 (invincible); parasol −128 |
| Sword | swim attack gets you to walking speed underwater (GR) | |

## UFO details (the TAS ability; 701M/3226M)
- **Charge by holding B** (no lag): 1-8 frames = beam, 9-33 = laser, 34-64 = star shot, 65+ = piercing shot (JPW). JXQ lists the same order: "beam, laser, star, double-star".
- **Firing freezes movement**: a beam stops Kirby for 1 frame; laser and stronger for 2 (JPW); GR says releasing stops movement for 1 frame.
- **Turning** freezes Kirby for 1 frame, except while charging: holding a charge removes the stop and makes turns 2 frames faster. A/B/Select are ignored for 2 frames after a turn and for 1 frame when switching between moving and stopped (JPW).
- **Doors**: UFO enters doors with no "turn and enter" animation (JXQ). It exits 1 frame faster with "...D,L/R+U" than "...L/R+D,U" (GR).
- **Ledge boost**: pressing L/R near a permeable ledge boosts UFO upward (GR). Thin platforms hit horizontally from slightly below also boost (JXQ). Hitting an incline horizontally is faster than following it (JXQ).
- **Limits**: UFO can't go down ladders or drop through thin platforms (JXQ).
  - 7-3 (JXQ) and 5-3/7-3 (701M revision notes): coasting over ice hills or "UFOing up an incline" triggers a speed-reduction bug. Avoid the hill tops.
- **Lag**: the laser is the least laggy kill. The beam spawns many effects; star and piercing shots are slow, so they linger (JPW). Kill enemies the moment they appear on screen (JPW). JXQ uses lasers for enemies and the double star for bosses.
- UFO is normally lost at stage end. Keeping it needs the UFO glitch (Glitches).

## Copy abilities: which give what (enemy → ability; ID in `$05E3`)
Hot Head → Fire 00 · Sparky → Spark 01 · Sir Kibble → Cutter 02 · Blade/Sword Knight → Sword 03 · Flamer, Fire Lion → Fireball 04 · Laser Ball → Laser 05 · Mr. Tick-Tock → Mike 06 · Wheelie, Grand Wheelie → Wheel 07 · Bonkers → Hammer 08 · Parasol Waddle Dee/Doo → Parasol 09 · Noddy → Sleep 0A · Spiny → Needle 0B · Pengy → Ice 0C · Chilly, Mr. Frosty → Freeze 0D · Starman → Hi-Jump 0E · Waddle Doo → Beam 0F · Rocky → Stone 10 · Bubbles → Ball 11 · Twister → Tornado 12 · Bomber, Poppy Bros. Sr. → Crash 13 · Cool Spook → Light 14 · Bugzzy → Backdrop 15 · Rolling Turtle → Throw 16 · UFO → UFO 17 · Star Rod 18 (final fights only). (WK/SW/DC)

**Mix / roulette** (JPW):
- Swallowing 2+ ability enemies starts a roulette in ID order (Fire → ... → UFO → Fire).
- It **starts on the ability after the last-inhaled enemy's ability**. Each slot lasts 4 frames on the first lap and slows on later laps. Press A to stop it; if untouched it stops on the 7th slot.
- Holding A/B while swallowing guarantees Stone after 2 Waddle Doos (Beam → Stone).
- Examples:
  - 2 Rockys (Stone): Tornado is slot 2; left alone, UFO (5-1).
  - 2 Waddle Doos: UFO is slot 8 (1-1).
- TAS 1-1: three jumps manipulate luck, inhale 3 enemies, roulette → UFO (5227S). Getting UFO from two enemies "needs a whole cycle in the roulette" (TASeditor).

**Damage** (JPW): air pellet 2, beam 3, laser 3, ice/cutter/wheel 4, sword/fireball/fire 5, tornado 6, freeze 6, stone/spark/needle/hi-jump 8, UFO star 10, backdrop 10, hammer 10, mike 10, ball 16, throw 18, **UFO piercing shot 25**, crash 29.
- Star Rod: shooting 1, star 10, body 2.
- HP: Whispy, Paint Roller, Kracko, Heavy Mole, Meta Knight, Nightmare Orb, Nightmare Wizard 60 each; Shine & Bright 30+30; Dedede 100.
- Mid-bosses: Grand Wheelie 25, Bugzzy 30, Fire Lion 27, Poppy Sr. 30, Bonkers 27, Tick-Tock 25, Mr. Frosty 20, Rolling Turtle 30. Meta-Knights: Axe 6, Javelin 4, Trident 6, Mace 8.
- Planning examples: 2 piercing + 1 star = 60 (Whispy, Heavy Mole); 4 piercing = 100 (Dedede).

**Best abilities by job**:
- Movement: UFO (free 8-way, fast, lasers), Tornado, Wheel, Fireball. Wheel is faster than UFO on long flat ground (JXQ, 2-1/2-2).
- Bosses: UFO piercing shots, Crash (29), Mike (10 × 3 uses, full screen). Meta Knight forces Sword.

## Damage, i-frames, death
- A hit costs 8 HP units (1 bar). After a hit `$05F9` counts invincibility; the duration is **not documented** (measure it).
- **Damage boosts**: TASes take hits to pass enemies and spikes on i-frames and to kill enemies by contact (5227S, 9286S; JPW lists boosts in 3-2, 3-4, 5-4, 6-2, 6-3, 7-1, 7-6).
- Stage clear refills HP from max (ROM `$E4FD`). Maxim Tomato = full heal; Pep/energy drink = partial.
- Death restarts the room checkpoint and costs a life (`$056A=3`). It is useful only as a deliberate warp; no route uses it.

## Rooms, doors, transitions
- A door is entered with Up while overlapping it. Normal Kirby plays a turn-and-enter animation; UFO doesn't.
- **Holding Up when the next room starts sends Kirby back through the door** (JPW, several stages). Release Up on the transition.
- **Delayed exits**: the exit frame changes the next room's lag (one lag frame or none every second delayed frame, GR). It is only worth it with unkillable enemies (Gordo, cannons). TASeditor ignored delayed exits, so they are a known improvement.
- **Warp Star**: an autoscroll ride between rooms. **Goal Game** after every non-boss stage: press A/B within a 36-frame window on the spring.
  - Frame 1 = fastest, frame 2 = +10 frames; frames 3-36 cost between +4 and +430 (the frame-4 option is +4, landing on 6).
  - Not pressing costs +63 frames (JPW; speedrun.com's guide says 64).
  - **Press on the first possible frame.**
- **Stage unlock cutscenes**: after clearing a stage the hub plays the next door opening. keyword's WIP found a soft reset faster than watching these after 2-3 (5f), 2-4 (52f) and 2-5 (46f) (9286S WIP). Clears are saved to battery.
- **Boot**: a cold boot plays the HAL logo and the "how to draw Kirby" intro. A warm reset jumps to the title (`$07F4`). TASes reset on frame 5 (FCEUX) or frame 3 (BizHawk). JXQ measured the reset trick at about 110-117 frames.
- After Dedede, stand still: moving delays the fade-out (9286S). After the Dedede kill in a UFO run, drop the UFO and hover or crouch, or the transition is slower (JPW).

## Lag (the dominant cost)
- The game lags whenever 2+ moving objects or effects are on screen (JPW). Sparky's spark and Waddle Doo's beam are the worst (JXQ, 9286S).
- Fixes:
  - Kill enemies with a UFO laser as soon as they spawn.
  - Avoid enemy attack animations through RNG.
  - **Movement interrupt**: release the D-pad for 1 frame. It usually removes 1 lag frame, sometimes 2.
  - **Half-interrupt**: press Up/Down while moving horizontally. Speed drops to 2 px/frame but lag frames can be saved.
  - **Edge-boost despawn**: on vertical levels, an edge boost can stop enemies at the right distance from spawning.
  - Don't over-kill: some kills create more lag than they remove (GR).
- Measure lag with the `$01A5` test (ram-map.md), not the emulator's counter.

## RNG
- `$3E/$3F` advance whenever a random number is drawn (GR, MJ):
  - landing sparkles and wall/ceiling bumps (non-UFO only);
  - inhale air particles, which depend on how long you inhale;
  - swallow sparkles;
  - some abilities' sparkles, including enemies that use those abilities;
  - kill sparkles (killing, not inhaling);
  - enemy action rolls (Waddle Doo: 0 jump, 1 walk, 2-3 attack).
- Deliberate slowdowns (extra jumps, inhale length) are the tools. The TAS's 1-1 opens with 3 jumps for luck. Bosses (Meta Knight, Dedede) and mid-boss patterns are manipulated. In 2-4, "4 enemies ... crucial to have a specific RNG value" were set up back in 2-3 (TASeditor).
- JP and NA "play almost exactly the same", but movies don't sync across them (9286S). RNG "reportedly" differs slightly (JPW).

## Glitches (see speedrun.md for where they are used)
- **UFO glitch / permanent ability ("carry-over")**: drop the ability with Select on the exact frame you take damage (1-frame window).
  - The ability is kept while the game thinks you have none. It survives stage ends and further hits (1314S/GR/JPW).
  - Timing tell: too early and you hear the ability-release sound; too late and you hear the damage sound (JPW).
  - Pause variant: press Start+Select on the same frame, then exit the (cleared) stage from the pause menu.
  - Warp-star variant: drop on the frame you board the Warp Star.
  - Works with UFO, Sword, Hammer, Parasol. Other abilities become a useless "splash" ability.
  - The dropped UFO star can't be re-eaten to get UFO back (1307S).
- **Collision pause glitch**: pause on the exact frame an enemy loads. The enemy keeps acting; when it hits Kirby you can move inside the pause screen.
  - While paused, terrain collision is read from another part of the map ("top-left room", 9286S), so you can pass through walls. Doors and spikes still work while paused.
  - Floating is needed; jumping or inhaling unpauses. Banned in RTA NMG.
- **Slope clip**: at the top/middle of a slope, a 1-frame A press with the right X subpixel and speed clips through.
  - Speed requirements differ by source: about 160-170 (9286S), or above 256 in walking state (JPW).
  - The credits-warp setup in 3976S needs two 1-frame jumps in a row.
- **Corner clip** into 2-tile-high walls (9286S); MUGG (2026): 1-tile ledges, "should be possible on all right corners", y about .46-.48 with y speed −300/−333. **Ladder clip** (2-3, 5-2). **Pit-crouch clip**: press Down just before a 1-tile pit; the ability must not change Kirby's look. **Acute-angled ledge clip** (5-5). "Hit while hitting" clip (GR, undocumented). **Sword clip** skips most of 5-2 (TAS).
- **Stone glitch / credits warp**: activate Stone while in water that was entered from below or the side (normally only reachable by clipping). Memory gets corrupted; pausing on the right frame jumps to the credits.
  - The outcome depends on input and PPU/CPU timing, and on the revision: MUGG says PRG0 and PRG1 differ.
  - Locations: 1-1 (room 3 pool, via slope clip), 2-3, rarely 6-1 (the block under the mid-boss door can become water).
- Other: pause-collision wrong warps 1-2 → 1-1 and 4-3 → level 4 hub (useless). Mike counter underflow at a switch edge in JP/PRG0, fixed in PRG1 (TCRF).
- Softlocks: 2-2 Grand Wheelie not appearing (lag from the Hot Head/Sparky on the left); Orb kill screen corruption; entering the Nightmare Wizard fight with low HP and dying at once; Fire Lion beaten mid-grab.
