# Kirby's Adventure — speedrun & TAS knowledge

Tags: `nnnnM` = TASVideos publication, `nnnnS` = submission, `P#####` = TASVideos forum post (thread https://tasvideos.org/Forum/Topics/57 unless noted), `JPW` = Japanese RTA wiki (seesaawiki.jp/ka_rta), `SRC` = speedrun.com API. Physics and glitch mechanics are in mechanics.md, RAM in ram-map.md, level layouts in walkthrough.md.

## 0. What to build (decision summary)
- **Two different "fastest" goals exist:**
  - **(A) Game-end glitch (GEG)**: a stone-in-water memory corruption in 1-1 jumps to the credits. Best TAS: 6389M, **2044 frames (0:34.011)**, BizHawk 2.10, PRG0.
  - **(B) TASVideos "baseline" any% (no GEG)**: beat Nightmare. Best TAS: 3226M, **123937 frames (34:22.220)**, FCEUX 2.2.2 old PPU, PRG0, published 2016 and known to be "horribly unoptimized" (author's joke, but the improvement list below is real).
- **Our ROM is Rev A = PRG1.** Every TASVideos movie is PRG0/JP/E, so **no published movie will sync as-is** (PRG0 → PRG1 desyncs, P43872). The routes and tricks transfer; exact frames, lag and RNG must be re-found.
  - **GEG outcome differs between PRG0 and PRG1** (MUGG, P370835). A 2013 GEG movie synced on PRG1 until one improvement made it "crash to a pink screen" (GhostSonic, P348458). It also depends on PPU emulation (old vs new PPU gave different results).
  - Test GEG early on our core: it is only about 2000 frames.
- **Recommended plan:**
  1. Replay 3226M's input on Rev A in our emulator to find where it first desyncs, then repair it segment by segment with local brute force. The route is already there.
     - 3226M was made on FCEUX 2.2.2 with the old PPU (`NewPPU 0`). Our harness has a FCEUX-derived core (fceumm) and Mesen, so fceumm is the likelier match for a replay (inference). 6389M was made on BizHawk NesHawk.
     - The input format is `|cmd|RLDUTSBA|...`, where T = Start, S = Select, and cmd 1 = soft reset.
  2. Add post-2016 tricks: pause glitch, MUGG corner clips, DarkRiolu27's 1-1 (−29 f), resets instead of unlock cutscenes.
  3. Separately attempt the GEG on Rev A.
- No category needs 100%. Switches are only for 100%.

## 1. TASVideos publications (game 41, https://tasvideos.org/41G)
| Movie | Goal | Author(s) | Emulator | ROM | Frames | Time | Rerecords | Date |
|---|---|---|---|---|---|---|---|---|
| **3226M** | baseline, current | TASeditor | FCEUX 2.2.2 | (U)(PRG0)[!] | 123937 | 34:22.220 | 1,226,400 | 2016-09-25 |
| 701M | baseline (obs.) | JXQ | FCEU 0.98.12 (text: 0.98.16) | PRG0 | 132330 | 36:45.500 | 29,425 | 2006-10-18 |
| 42M | baseline (obs.) | Bisqwit | Famtasia 5.1 | (E) | 159850 | 44:24.167 | 27,643 | 2004-03-27 |
| **6389M** | game end glitch, current | DarkRiolu27 | BizHawk 2.10 (NesHawk) | PRG0 | 2044 | 0:34.011 | 17,984 | 2025-02-18 |
| 3318M | GEG (obs.) | TASeditor, MESHUGGAH, CoolKirby, Masterjun, MUGG, 0xwas | FCEUX 2.2.3 | PRG0 | 2149 | 0:35.758 | 62,642 | 2017-02-01 |
| 2406M | GEG (obs.) | MESHUGGAH, CoolKirby, Masterjun, MUGG, TASeditor, 0xwas | FCEUX 2.2.1 old PPU | PRG0 | 2158 | 0:35.908 | 27,532 | 2013-06-22 |
| 1947M | GEG (obs.) | MUGG | FCEUX 2.1.5 | PRG0 | 20708 | 5:44.566 | 18,020 | 2012-01-10 |
| **6192M** | "no abilities" (alt.) | keyword | BizHawk 2.8 | **Japan** | 156312 | 43:20.917 | 155,556 | 2024-09-26 |
- PRG0 SHA1 `E099D688760FF0CE114CA8A9FD083E31E41CFADE`. TASVideos catalogs no PRG1 version. Framerate 60.0988138974405.
- Submissions: 172S → 42M; 1307S (kirbymuncher, UFO discovery, rejected as improvable, 42:47.167); 1314S → 701M; 3411S → 1947M; 3976S (CoolKirby, cancelled); 3990S → 2406M; 5227S → 3226M; 5351S → 3318M; 9286S → 6192M; 9484S → 6389M.
- Movie files: `https://tasvideos.org/3226M?handler=Download` (fm2 inside a zip; header `romFilename Kirby's Adventure (USA)`, `romChecksum base64:Nv+hAqy6EbXFdCfYrFrZjg==`, `NewPPU 0`, 123937 input lines) and `https://tasvideos.org/6389M?handler=Download` (bk2, 2044 lines).
  - Session copies (may not persist): `/tmp/claude-1000/-opt-src-nix-lab/21519891-953e-42f0-80b7-0f375b23cb2b/scratchpad/tasvideos-movies/`.
- **3226M input landmarks** (0-based frames, FCEUX):
  - f5 soft reset; Start(+A+B) f65; Start f99; Start f214.
  - Hub: Left f393-417 with Up taps → 1-1 door. Right from f459.
  - 1-1: jumps at f543, f559, f576 (luck); B at f639 and f674 (inhale); Down f888 (swallow); A f917 (stop roulette); UFO flying from f1006 (Up+Right+B charge); **R+D+Select at f1255** (UFO glitch).
  - Select pressed 21× in total (UFO-glitch / ability drops): 1255, 15283, 17973, 22164, 32519, 33212, 33760, 52092, 53575, 56026, 58389, 58826, 64375, 65630, 68122, 68677, 69879, 90366, 91401, 92430, 118162.
  - Start once mid-run, at f81039. No other resets.
- **6389M landmarks** (BizHawk): reset f3; Start f63/f97/f212; Left f400-414, Up f415; Right from f479; last frame 2043 = R+Start (pause on the crash frame).

## 2. Baseline TAS route (3226M, TASeditor; 701M JXQ as the base)
**Core concept**: get **UFO** in 1-1 and keep it for most of the game with the **UFO glitch**: Select on the frame Kirby takes damage (1314S).
- Kept UFO survives stage ends and hits.
- Lasers kill enemies to cut lag; piercing/double-star shots kill bosses.
- Switch to other abilities only where UFO can't go (ladders down, thin platforms, water).
- Uses glitches, takes damage, manipulates luck (5227S).

**Per world** (5227S + TASeditor WIP posts; frame gains are cumulative vs 701M):
- **1-1**: 3 jumps for luck → inhale 3 enemies → roulette → UFO; UFO glitch before leaving room 1. Room 2: ledge boosts upward and many half-interrupts for lag. Room 3: slopes used to kill enemies efficiently. (3-enemy inhale idea: MESHUGGAH.)
- **1-2**: the Warp Star section sometimes spawns a 3rd enemy (lag); quick mid-boss kill. **World 1: about 5 s gained.**
- **2-1/2-2**: JXQ took Wheel in 2-1 because 2-2 has a ladder UFO can't descend, and "wheel is even faster than UFO for the remainder of the level". TASeditor: in 2-2 a Wheelie is swallowed; beaming the trapped staircase enemies is not faster ("the beam creates a lot of lag itself").
- **2-3**: wall clip; was0x's "kill clock" strategy for the Meta-Knights saved 332 f (P370193).
- **2-4**: 4 enemies "crucial to have a specific RNG value", manipulated back in 2-3 (P377035); was0x's mid-boss improvement; per JPW the TAS mixes UFO at the 2-4 mid-boss.
- **World 2 end**: +38.5 s; Wheelie fight 7 f faster.
- **3-2**: a slope-room clip forces losing UFO and is slower because 2 enemies "will always attack" (P379064/P379142). Enemy-spawn prevention was found here (P370827).
- **3-3**: JXQ inhales enemies while falling so the Hi-Jump enemy can spawn.
- **World 3**: +48.15 s.
  - "Cloud displacement"/ledge boost despawns enemies "only if the enemy would appear at the right distance to Kirby" (P383280).
  - 3-6 lasers reflect from the ground.
- **4-1/4-2**: 35 f from lag reduction, 31 of them in 4-2 room 3.
- **4-4**: slope clip, net 48 f (248 saved in the clips, 104 lost in the next room). JXQ: dropping UFO for Wheel then re-mixing was slower by seconds. "Getting UFO from the two enemies in the first room needs a whole cycle in the roulette" (P388839).
- **4-5/4-6**: last room of 4-5: Fireball "creates a lot of lag, but the position gain is still bigger". JPW: the any% TAS takes Burning in 4-5, clips through 4-6, then mixes UFO in 4-6 room 6 (Starman + Sir Kibble, slot 21) and redoes the carry-over. **World 4: +4359 f.**
- **5-1**: +111 f (4472 total). UFO kept; TASeditor says Stone was "definitely slower" (701M: Stone in 5-1 slower too, P95590).
- **5-2**: UFO must be dropped at the start (water).
  - MUGG's wall clip, improved by 49 f, gave +827 f (P416754).
  - "The best way to clip would be in the second room, the next exit will lead to the room where ufo is gotten."
  - Blade Knight is swallowed underwater.
- **5-3**: Wheel is slower. In the big slope room "not touching them saved a lot" (+181 f). At the end you **must collide with an enemy to keep UFO**, or it's lost on the map; a glitch-kept UFO is pink (P416950/P416970). 701M: having UFO already in 5.3 saved 10 s; "speed change bug in 5.3 and 7.3 after UFOing up an incline" (2 s).
- **5-5**: a better room-2 route saved 133 f; slope clip there is slower (143 f); a UFO-compatible 5-5 clip is "335 frames faster" (P416150). **World 5: +6479 f.**
- **6-1/6-2**: went back to World 5 to kill an extra enemy and cycle RNG; about 10 f in 6-1 room 1 (6841 total).
- **6-4**: clip about 70 f faster (7077).
- **6-7 Meta Knight**: hit "each 32 frames, instead of 54". He must be in the corner; dash attack, then an immediate aerial attack. JXQ manipulated fewer blocking pauses. **World 6: +7431 f.**
- **7-1**: TASeditor's WIP note at this point: improved luck manipulation in the (6-7) Meta Knight battle. 701M: 7-1 block room 1 s.
- **7-3**: diagonally avoid the ice hills (speed-cap bug). **7-5**: star currents push Kirby. **World 7: +8242 f.**
- **Orb**: take hits to use the Star Rod a few frames earlier (JXQ). keyword: you can shoot every 20 frames (+lag), bypassed by taking damage.
- **Wizard**: hit as soon as possible; the cape-open animation is never seen (JXQ). **Final: +8393 f** (2:19.88).
- Tools credited: feos's lag Lua, Masterjun's RNG Lua.

## 3. Known improvements over 3226M (sources say so; none combined yet)
1. **Pause glitch** (collision pause, found after 2016): "probably can shave off some time for any%" (TASeditor, thread 25685). RTA NSG uses it in 2-3, 3-1, 3-2 (+3.7 s), 4-2 (~2 s), 5-2, 6-2 (~7 s), 6-4 (~12 s), 7-1 (2-4 s) (JPW). keyword used it in 3-1, 4-6, 5-2, 6-2, 6-3, 6-4.
2. **MUGG corner clips** (2026, P543168; JP ROM, BizHawk 2.9.1; measured on the no-ability route, so UFO-route applicability is **unverified**): 4-6 **1132 f**, 1-3 67 f, World 2 boss 22 f, 3-1 3 f, 3-3 265 f, 6-3 144 f (saves 1 HP), 6-4 212 f (saves 1 HP), 6-5 79 f. 7-4 looks possible; 7-6 improvable.
   - Setup: the frame before "<^B", y pos about .464 (.46 to ≥.48), y speed −300 or −333.
   - Input files: https://tasvideos.org/UserFiles/Info/639242922736222255 (3-1) and the 6392429xxxx series (P545078). "Level doors are not loaded until unlocked."
3. **DarkRiolu27's 1-1** is 29 f faster than 3226M (UserFiles 638745497760453505, BizHawk, 2258 f). "Moving up for one extra frame might save 3 frames of lag" (P534408).
4. **Delayed exits** (deliberately skipped by TASeditor); taking damage to kill enemies in early levels; more enemy despawns (5227S).
5. **0xwas's unsubmitted NMG 100%** beat 3226M in places, "Metaknights fight in 6-6 is most notable" (P481605).
6. **Reset instead of unlock cutscenes**: keyword found reset faster after 2-3 (5 f), 2-4 (52 f), 2-5 (46 f). Clears are saved to battery.
7. 701M-era list: UFO instead of Spark in 5.2 (6 s); World 6 boss behavior (4.5 s); luck/lag (2.5 s). Already in 3226M.

## 4. Game-end glitch (credits warp) — 1-1 only, about 2044 frames
- **Route (6389M)**:
  - Reset → menus → enter 1-1.
  - Room 1: carry slide speed through the room and kill enemies with invincibility frames.
  - Room 2: inhale/exhale kills; inhale the Bronto Burt rather than float.
  - Room 3: kill Poppy Bros. Jr. and Waddle Dee. **Mix in room 3** (the roulette needs two ability enemies; Chanoyu): set up the mix below a ledge so the slide continues while inhaling, and roll **Stone**.
  - **Slope clip** "with the right X subpixel and speed" into the floor, drift into the pool from the side, activate Stone in the water, and press **Start on the crash frame** (last frame 2043: R+Start). Ending graphics depend on the last input: 5351S says change TLR to TDLR on the last frame for normal graphics; MESHUGGAH, in the 6389M thread about an earlier movie: "For corrupt ending, change from S to L+R+S @ frame 2058".
- History: 3976S needed "at least two 1-frame jumps, one right after the other" to slope-clip, then Stone "to drift slowly into the water". 3990S: press Start "and a few other buttons" on the last frame before the crash; 3 inhaled enemies instead of 2 save lag; delaying a room exit changes next-room lag.
- 5351S (3318M): 9 f from movement interrupts, with exact checkpoints:
  - Room 1, 6 f faster: frame 603 jump; 2 lag frames + 134 subpixels at frame 888; 6:224 px ahead at frame 1069; 12:199 at frame 1229.
  - Room 2, 3 f faster: about 2 px sacrificed at frame 1584; 21:8 px ahead at frame 1620.
- Hardware facts:
  - Credits vs crash depends on PPU-register reads at `$3C3F` during the bogus jump, so the buttons pressed change the timing (Masterjun P446900).
  - The DMC timer is not controllable (Alyosha).
  - It worked more reliably after a fresh reset (3411S).
  - After a credits warp only the stages you played are unlocked.
  - NES Classic / Switch Online catch the crash and quit.
  - **Revision risk**: PRG0 and PRG1 outcomes differ (see §0).
- RTA version (JPW Any%):
  - Use file 1. Stone mix in 1-1's first map: swallowing 2 Waddle Doos while holding A/B guarantees Stone.
  - Subpixel setup: slide 5 times in place holding Down-Right, switching to Down during the 3rd slide. Walk right and press A for exactly 1 frame on a specific frame.
  - Enter the water from the side, activate Stone, and press Start 1 frame before the crash. It works only "sometimes".
  - 2-3 is easier for one-shot attempts.

## 5. No-abilities TAS (6192M, keyword) — movement tech applicable everywhere
- Slide (677) off ledges, then jump on the first possible frame. Every ground frame costs 14.
- Damage boosts. Spit while holding the direction to keep speed. 1-frame jumps to turn without skidding.
- RNG: avoid Waddle Doo beams and Sparky sparks via landing/bump sparkles.
- Clips used:
  - Pause clips: 3-1, 4-6, 5-2, 6-2, 6-3, 6-4.
  - Slope clips (middle of a slope, about 160-170 speed, press A that frame): 3-2, 4-2, 4-4, 6-4, 7-1.
  - Corner clips: 7-1, 7-6. Ladder clips: 2-3, 5-2. 5-5: "weird geometry".
- Meta Knight about 20 f faster if damage could be taken. Stay still after Dedede. Orb: shots every 20 f, bypassed by damage (net 9 f vs TASeditor). Pause-glitch wrong warps (1-2 → 1-1, 4-3 → hub) are useless.

## 6. speedrun.com (game `om1mkxd2`, slug `ka`)
- Rules:
  - All categories time **from file select**: "the frame before the screen begins to fade white upon file select".
  - Nightmare categories end on the first frame the screen flashes orange on the final hit. Any% ends on the first frame Whispy appears in the credits.
  - Emulators allowed except for WRs. Regions: USA, PAL, JPN.
- Records (2026-11 snapshot):
  - **Any%** (all glitches, credits warp): 0:39.130 ReinVos (NES USA, 2025-08-08).
  - **Any% NMG** (bans UFO glitch, stone glitch, collision pause; other OOB allowed): 42:38 miririi6 (JPN).
  - **Any% No Stone Glitch**: 36:59 shirokirby (JPN).
  - **100% NMG**: 47:39 swordsmankirby. **100%**: 40:41 shirokirby. **100% Perfect**: 1:18:41. **No Copy Abilities**: 53:18 Pelurilu.
- **NMG ability plan** (TheTerrificTracy split files): 1-1 Tornado · 2-3 clip · 3-2 UFO · 3-3 Hi-Jump & Tornado · 3-5 Tornado/Hammer · 4-1 UFO & Tornado · 4-4 Wheel & UFO · 4-5 Burning · 4-6 Hi-Jump · 5-1 Tornado · 5-5 clip · 6-2 backup Tornado · 6-4 clip · 7-1 clip · 7-2 Hammer · 7-3 Tornado.
  - 2-3 clip: needs an ability that adds nothing to Kirby's look (Tornado, Hi-Jump, Ball OK; Parasol, Hammer, Sword not). "Run and duck off the edge and aim for the corner". Softlock spots exist.
  - The 5-2 OOB clip saves "15-20 seconds".
- **NSG route (JPW stable)**: the closest human analogue of the TAS. Abilities:
  - 1-1: clear, re-enter, mix UFO, leave with the carry-over. Aggressive: mix at the 1-1 start (2 Waddle Doos, UFO slot 8), then the damage carry-over at the Hot Head by the door.
  - 2-2: Wheel.
  - 2-3: pause-glitch route (about 23.5 s faster than re-getting UFO).
  - 3-3: Hi-Jump; then re-enter 3-1 for a UFO mix from 2 Parasol Waddle Dees (slot 14) + carry-over.
  - 5-1: Tornado from 2 Rockys (slot 2). After 5-2, re-enter 5-1 and mix 2 Rockys left alone for a guaranteed UFO + carry-over.
  - Recovery mixes: 4-4 (slot 14), 7-3 (2 Noddies, slot 13).
  - Damage boosts: 3-2, 3-4, 5-4 (3 hits), 6-2, 6-3, 7-1, 7-6.

## 7. Per-stage UFO route notes (JPW NSG, condensed)
Notation: chg = fly while holding a charge; L = laser, Bm = beam, SS = star shot, PS = piercing shot, PG = pause glitch, Sn = room n. These are RTA lines; a TAS should brute-force each kill but can use them as the baseline plan.

### 1-2
- S1: drop 1 tile by the hole, L×2.
- S2: hold B as the Warp Star lands (Bronto Burt flies left); SS at the slope top, then PS the mid-boss.
- S3: L the corridor enemies (one L above Waddle Doo kills Poppy).
- S4: up-right L, PS Cappy; watch Sword Knight's double swing.

### 1-3
- S1: up 1 tile, L Kabu.
- S3: PS Blipper underwater, L Slippy.
- S4: L on entry and climb; kill the top 2 of 4 stacked platforms; **don't kill the last Bronto Burt**.

### 1-4
- S1: L Poppy Jr., PS Mr. Frosty.
- S2: PS before each Kabu, L×3.
- S4: PS before Bronto Burt, finish with Bm.

### Whispy Woods
- Wait at the left edge charging; fire just before his HP bar fills, then move right point-blank for a PS (Doppler), then an SS. Catch the piece from above.

### 2-1
- L×5 for the Coconuts; laser the path; Bronto Burt may attack (luck).

### 2-2
- S4: hold **only Down** in the autoscroll to Grand Wheelie; PS him; L the bottom bomb block.

### 2-3
- S2: Bm×2 down-right, get directly above Sword Knight, **PG at the set spot**, move up, unpause inside the wall, break the bomb block by the door.
- S5: SS everything.

### 2-4
- S1: L chain under the Tomato. S2: PS the mid-boss.

### 2-5
- S3: one PS before Kabu also kills the Sword Knight. S4: 3 beams.

### Paint Roller
- 2 PS + 1 SS (the 1st from the right).

### 3-1
- S3: PS the mid-boss from its right.
- S4: L×2 on entry, **PG** into the right wall, L 2 enemies.
- S6: L×3, the 2nd slightly delayed and the 3rd a lot.

### 3-2
- S4: PG variant +3.7 s (−1 HP) or damage-boost variant +0.5 s.
- S6: PS/SS Bugzzy.

### 3-3
- S1: Starman → Hi-Jump (2 Hi-Jumps to the door).
- S2: mix UFO from 2 Starmen (slot 9) + carry-over.
- S4: while charging, press Left, Up, Left, Up. **Holding Up sends you back** at S3/S4 entries.

### 3-4
- S3: one SS per enemy in a set order.
- S4: take a hit and pass on i-frames if HP ≥2.

### 3-5
- S4 Bonkers: L then PS (faster than PS first because of his i-frames).

### 3-6
- S2: L×3 bounced off walls to break star blocks.
- S5: PS Blade Knight.
- S6: an L at the left end of Sir Kibble's platform hits the Cool Spook.

### Shine & Bright
- PS, SS, SS, close, PS — or PS, SS, PS, SS.

### 4-1
- Travel 1 tile low; PS before Noddy/Twister.

### 4-2
- S1: don't touch the slope peak (it slows you); PG variant about 2 s.
- S3: wait for a Poppy to fall off screen first (otherwise 2 Poppies lag).
- S5: one PS for both Poppy Sr.

### 4-3
- The shortest line snags on the cannon. S4: line up horizontally with the goal first (less enemy travel, less lag).

### 4-4
- S3: avoid the steep hill (slowdown bug).
- S4: move down in the autoscroll; PS + SS the Rolling Turtle.

### 4-5
- S3: fixed SS/PS order. TAS route: Burning here, through S5.

### 4-6
- TAS route: clip at the first 1-tile hole with Burning; S6 mix UFO from Starman + Sir Kibble (slot 21) + carry-over (about 29 s faster than going back to 4-4).

### Kracko
- Straight up, left edge at the 1st Starman, 3 PS.

### 5-1
- UFO route, or Tornado mix (2 Rockys, slot 2) in the hidden room under the cloud. Stone/Ball fallbacks cost 5-7 s.

### 5-2
- Drop UFO in S1 (or carry Tornado); dive while inhaling Blade Knight; S3 **PG while falling right**, hover straight up into the door; S11 inhale/spit Waddle Dees.

### 5-3
- S1-S2: Hi-Jump.
- S3: inhale 2 Wheelies while falling → UFO slot 16; damage carry-over on the 3rd Wheelie; stay off the up-slopes.

### 5-4
- S2: fixed kill order. S3: chg 2 tiles above the waterfall into the hidden room (skips S4). S5: tank 3 hits (faster).

### 5-5
- S3: **acute-angled ledge clip** (Kirby's left edge just over the flat tile, slightly above it, move right) → S6. Entering partway = softlock.

### Heavy Mole
- 2 PS + 1 SS (Doppler).

### 6-1
- S2: L the first 3 Flamers; a PS kills the 6th + Sparky.

### 6-2
- S2: PG at a set height near the left edge, unpause near the door (about 7 s).
- S3: contact-kill 2 Scarfys on i-frames from Gordo.

### 6-3
- S2: PS + SS Bonkers. S5: damage-boost through the Scarfys.

### 6-4
- S2: kill 2 Broom Hatters, **PG**, through the wall (about 12 s).

### 6-5
- S4: up-right until the scroll stops.

### 6-6
- S2: tank the UFO enemy's hit. S7: SS all of them in a fixed order.

### Meta Knight
- Slash as his i-frames end; wait above for the piece.

### 7-1
- S2: long beam/laser block sequence; PG variant needs ALL upper star blocks broken with 2 beams first.
- S3: optional damage boost through a Shotzo.

### 7-2
- Take the hidden door (4 mid-bosses instead of 7; PS + SS each).

### 7-3
- S2: climb diagonal slopes holding only Right/Left.

### 7-4
- Beams through the U-halls.

### 7-5
- S2: PS Grand Wheelie; S3: stay high to kill the Flamer (otherwise you get pushed into the pit).

### 7-6
- S7: contact-kill the 3rd Scarfy on i-frames.

### King Dedede
- 4 PS from the left edge; then drop UFO and hover or crouch.

### Nightmare Orb
- Skip the demo with A/Start; mash A+B; take ≥2 hits.

### Nightmare Wizard
- 6-hit plan (walkthrough.md). If it isn't dead after 6, big time loss.
