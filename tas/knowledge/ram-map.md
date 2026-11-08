# Kirby's Adventure (USA, Rev A) — RAM map for the TAS agent

## ROM identity (read first)
- Our file `roms/usa-rev-a.nes`: SHA1 `F324E7C8C3AD102ECDCCA011ECC494F6F345D768`, headerless MD5 `758744ec2d2fa3d1f2020586401f97e8`, PRG CRC32 `8FFF3F32`.
- **Rev A = PRG1 = "Rev 1".** Three checks agree: a blog lists PRG1 = PRG CRC32 `0x8FFF3F32`; TCRF says US Rev 0 has the string `RGKK_SetStillX` at file offset 0x7FFF0 ("random data in every other version"), and ours has random bytes there; our headerless MD5 is in RetroAchievements' hash list for the game.
- **Every TASVideos movie uses PRG0** (or JP/E). PRG0 movies desync on PRG1 (TASVideos forum). So addresses from PRG0 sources are hints until checked here. No source documents a RAM difference between the revisions, and the core variables below agree across PRG0 and PRG1 sources.
- `$C371 LDA #$01 / $C373 STA $01A5` and `$C323 RTS` (end of the controller read) are at the same addresses Masterjun's PRG0 Lua hooks. I checked this from the bytes of our ROM.

## Source tags
`LOC` = /opt/src/nes-disasm-tool findings (built on our ROM). Its probes only covered boot → title → hub → start of 1-1, and much of it is static analysis. Some LOC labels are wrong; see "Conflicts".
`ROM` = byte check of our ROM in this session.
`SEED` = `knowledge/ram-seed.json`, written by the harness agent from emulator observation.
`MLB` = Nathan-R-Og/kirbyadventure Mesen labels, from a disassembly of "USA (Rev 1)", i.e. **our revision**.
`TV` = TASVideos 3411S RAM table (MUGG, PRG0).
`MJ` = Masterjun/feos Lua (pastebin pT0hbSXN, PRG0).
`WDX` = WaddleDX KA_SpriteViewer.lua.
`TE` = TASeditor KirbyLogger.lua.
`KALE` = devinacker/kale kah.lua.
`DC` = Data Crystal RAM map/Notes (revision not stated).
`RA` = RetroAchievements code notes, game 1479.
Status: **V** verified (runtime or ROM bytes), **C** corroborated (≥2 independent sources), **S** single source, **X** conflicting.

## Player position / physics
| Addr | Meaning | Sources | St |
|---|---|---|---|
| `$0083` / `$0095` / `$0071` | Kirby X: pixel lo / page hi / subpixel. World X = `$95*256+$83` (+`$71/256`) | TV, MJ, WDX, KALE, MLB (`kirby_x_lo/hi`), RA, LOC (table `$70,x/$82,x/$94,x` with Kirby = slot 1) | C |
| `$00B9` / `$00CB` / `$00A7` | Kirby Y: pixel lo / page hi / subpixel. Down = larger. MUGG's Lua reads the hi byte as signed. | TV, MJ, WDX, KALE, MLB, RA | C |
| `$6075` / `$6087` | Kirby X again: the slot-1 entry of the WRAM table `$6074,x/$6086,x` (MLB: `OBJ_store_x`). SEED says "verified". | SEED, LOC, MLB | V |
| `$6099` / `$60AB` | Kirby Y, store copy | SEED, LOC | V |
| `$05B9`/`$05BA` | Kirby X velocity, signed 16-bit, subpixels/frame (256 = 1 px) | TV, WDX, MLB, LOC | C |
| `$05BB`/`$05BC` | \|X speed\| (unsigned). JXQ: above 460, ground speed drops 14/frame. | JXQ forum, MLB, LOC | C |
| `$05BD`/`$05BE` | Kirby Y velocity, signed 16-bit. TE's gradient uses max 880. | TV, WDX, MLB, LOC | C |
| `$60E1`/`$60F3`, `$6105`/`$6117` | Slot-1 object velocity X / Y (table `$60E0,x`) | SEED ("per disasm"), LOC, MLB | S |
| `$00DD`/`$00DE` (+`$00DC` frac) | **Camera X** (scroll). Kirby screen X = KirbyX − camX. | MLB, MJ, WDX; LOC mislabels this as Kirby X | X→camera |
| `$00E0`/`$00E1` (+`$00DF`) | **Camera Y** | MLB, WDX; RA notes `$E1` as "Screen Number Y" | C |
| `$00EB` / `$00EA` | Temporary scroll X / Y | KALE, WDX, MLB, LOC | C |
| `$05C0-$05CD` | Camera min/max scroll X, Y; min/max allowed Kirby X; min Kirby Y (16-bit each) | MLB | S |
| `$05F4` | MLB: slope state (2 level, 3/4 gentle up/down, 5/6 steep up/down). LOC: facing (0 R, 1 L). | MLB vs LOC | X |
| `$05F7` | MLB: underwater flag. LOC: ground contact. | X | X |
| `$05FB` | Kirby flags. bit6 = "hyper" (invincibility candy) per RA, MLB and LOC. MLB also gives 04 = grounded, 20 = can't discard ability, 80 = can't pause; LOC gives bit2 = ducking, bit3 = floating. | RA, MLB, LOC | C (bit6) |
| `$05F9` | Post-hit invincibility timer. RA: "Invisibility after being hit"; MLB: `kirby_yellow_flash_timer`; LOC: knockback timer. | RA, MLB, LOC | C |
| `$05E1` | Kirby action state: 0 stand, 1 walk, 2 run, 3 stop, 4 jump, 5 fall, 6 duck, 7 slide, 9 inhale, 10 spit, 11 swallow, 12 power use, 13 fly | TE; RA (Inhale = 9) | C |
| `$62C7` | Kirby pose/animation (slot-1 entry of `$62C6,x`). DC has a table: 22/23 jump, 24/25 fall, 2E/2F duck, 52-55 fly (RA: 52/54 flying), ... | DC, RA, MLB (`OBJ_pose`) | C |
| `$05E0` | Kirby primary mode. RA: "power-up animations, 0x0B = in Ball form". LOC: 0 normal, 1 mouthful, 2 ability, ... | S/X |

## Location: world / stage / room
| Addr | Meaning | Sources | St |
|---|---|---|---|
| `$0558` | World: 0 Vegetable Valley ... 6 Rainbow Resort, 7 Fountain of Dreams. The boss-clear code does INY and stores into $0557/$79E9/$0528, and writes $0558 only when the result ≥7. | RA, MLB, LOC, ROM (`$E4E0` region), SEED (0 in 1-1) | V |
| `$0520` | Stage index within the world (0-based; 7 = boss). Used as X in the stage-clear bitmask code. | LOC, ROM, SEED (0 in 1-1) | V |
| `$0559` / `$055A` | RA: "Current Stage [Entered]" / "Current World [Entered]"; MLB: `current_stage` / `room_055A` | RA, MLB | S |
| `$055E`/`$055F` | **16-bit room ID** (lo/hi). 1-1 r1 = `$002B` (SEED read 43). Full table: RA note on $055E, also DC Notes. Examples: 0x08..0x10 boss rooms (0x0C = Heavy Mole, 0x0F/0x10 Nightmare), 0x2A = goal game, 0x6C = Meta Knight, 1-1 = 2B-2E, 1-2 = 2F-34, 2-1 = A9.., 3-1 = C6.., 4-1 = EC.., 5-1 = 111.., 6-1 = 3D.., 7-1 = 6D... `$055F=$FF` is written as a "reload" sentinel. | RA, MLB, DC, SEED, ROM (stage-clear code tests `$055F:$055E == $000C`, which RA lists as World 5 boss, the one with a special exit) | V |
| `$0562`/`$0563` | KALE: destination room word (max 0x146). Writing it and setting `$055F=$FF` warps rooms. LOC: spawn X/Y regs. MLB: `room_0562`. | KALE vs LOC | X |
| `$0564` / `$0565` | KALE: start screen / start point in the room | KALE (LOC: dir/action) | X |
| `$0566-$0569` | Checkpoint copy restored into `$0562-$0565` by `$E581` | LOC (static) | S |
| `$0570` | RA: "Screen in Stage"; LOC: horizontal nametable page | RA/LOC | S |
| `$057B` / `$057C` | Camera reference X/Y (RA: "Screen X/Y") | RA, LOC, MLB | C |
| `$67EE` / `$67EF` | Room width / height in screens. `$67F0` CHR set, `$67F1` palette, `$67F4` music, `$67F6..` screen order list, `$68C8..$74C7` tilemap (16×12 metatiles per screen) | MLB, DC, WDX, KALE | C |
| `$7F00-$7FFF` | Metatile collision attribute table. DC values: 00 air, 0D solid, 0E two-way platform, 0F one-way, 10-17 slopes, 1C star block, 1D/1E breakable, 20 bomb block, 23 ladder, 24 spikes, 25 post/stake, 28 door?, 30 water, 31-3C currents, 03/05/06/09 wind | DC, LOC, WDX | C |

## Game mode / state
| Addr | Meaning | Sources | St |
|---|---|---|---|
| `$056A` | Scene transition request: 0 none, 1 room/door, 2 respawn, 3 death (DEC lives), 4 stage reload, 5 stage clear, 6 warp star, 7 area exit. Edge-trigger on ≠0 to detect doors and clears. | LOC (static code), SEED | S+ |
| `$051E` | RA: 0 transition?, 1 in game, **7 paused**. LOC: camera mode, 7 = scroll disabled. | RA, LOC | C |
| `$0180` | Raster/split mode. 1 = in-game HUD split (RA "In-Game HUD Visible"); RA: 6 = main menu. | LOC, RA, MLB | C |
| `$051C` | RA: 0 normal, 1 "Hi-Jump minigame" (the Kracko climb), 3 boss | RA | S |
| `$00F4` | Mode: 0 normal, 1 Extra Game, 2 VS Boss | RA, MLB (`extra_game_flag`) | C |
| `$6128` (slot 0) | Slot-0 script ID gives the scene: `$68` HAL logo, `$69` title, `$6C` level intro (LOC runtime trace). `$6128+1` = Kirby slot (< `$80` = active). | LOC (runtime) | V |
| `$0783` | Music ID: 0x35 title, 0x22 Vegetable Valley, 0x2C ICI, 0x2D BB, 0x23 GG, 0x24 YY, 0x15 OO, 0x06 RR, 0x08 stage end, 0x14 arena, 0x03 credits. Cheap state cue (credits = GEG success). | RA, LOC | C |
| `$0782` | SFX ID (0x1F splash, 0x21 1-Up) | RA, LOC | C |
| `$07F4` | Boot type: 1 = cold → HAL logo + drawing intro; 0 = warm reset → straight to title. This is why TASes reset on frame 3-5. | LOC (runtime), MLB (`is_cold_reset`) | V |
| `$0517-$051B` | ASCII "KIRBY" cold-boot marker | LOC, MLB | V |
| `$0190` | RA calls it "Game State" (0x27 ingame, 0x26 paused/quick draw, 0x21 title, ...), but MLB places `$0182-$01A1` = palette buffer. Probably a palette byte that correlates with the mode; don't rely on it. | RA vs MLB | X |
| `$61DC` | Game-over cursor (0 Continue, 1 End) | LOC | S |
| `$0528` | Progress: 00-06 = world N+1 in progress, 08 = game cleared, 09 = Extra cleared | DC, LOC, ROM | C |
| `$0521-$0527` | Per-world stage-clear bits (bit k = stage k+1) | DC, RA, MLB (`level_progress`) | C |
| `$0529-$0530` | Per-world switch bits (DC `$052B-$052F`, worlds 3-7) | MLB, RA, DC | C |
| `$0531-$0538` | Per-world flags; bit 7 = boss defeated (`$0538` = Nightmare phase 1). ROM: on stage clear the game sets bit `$0520` of `$0531+$0558`. | RA, DC, MLB, ROM | V |
| `$05FE` / `$05FF` | Goal game: landing slot (1 = top "7" ... 7 = "1") / secret-order counter | RA | S |

## HP, lives, ability, bosses
| Addr | Meaning | Sources | St |
|---|---|---|---|
| `$0597` | HP. Full = `$2F` (47) = 6 bars, −8 per hit ("count by 8"). Stage clear copies `$0596`→`$0597` (full heal; ROM `$E4FD`). | LOC probe, SEED, DC, RA, ROM | V |
| `$0596` | Max HP (`$2F`) | LOC, DC, MLB | V |
| `$0599` | Lives (start 4; display max 99) | LOC probe, SEED, DC, RA | V |
| `$059D` | Lives/status-bar display | DC, RA | S |
| `$0593-$0595` | Score ÷ 10, 24-bit | DC, RA, MLB | C |
| `$05E3` | **Copy ability**: 00 Fire, 01 Spark, 02 Cutter, 03 Sword, 04 Fireball (JP Burning), 05 Laser, 06 Mike, 07 Wheel, 08 Hammer, 09 Parasol, 0A Sleep, 0B Needle, 0C Ice, 0D Freeze, 0E Hi-Jump, 0F Beam, 10 Stone, 11 Ball, 12 Tornado, 13 Crash, 14 Light, 15 Backdrop, 16 Throw, **17 UFO**, 18 Star Rod, 19 "Bye Bye", FF none. This order equals the JP RTA wiki's roulette order. LOC's ID→name list (Beam=0, UFO=$10, ...) is **wrong**. | DC, RA, JPW; address C with LOC/MLB | C |
| `$05E2` | Ability of the enemy in Kirby's mouth (FF = none) | DC, RA, LOC | C |
| `$0598` | Uses left for Mike/Crash/Light (DC, RA); LOC says Mike 3, Crash 1, Sleep 1 | DC, RA, LOC | C |
| `$05E5` / `$05E6` | Inhaling count / inhaled count (MLB); RA `$05E7` = "copy enemies inhaled" (≥2 → roulette) | MLB, LOC, RA | S |
| `$66EB` | RA "22-mix" (roulette-related?); MLB: "MAYBE copy ability icon" | RA, MLB | S |
| UFO-glitch check | After the glitch, `$05E3` reads FF ("normal") while Kirby is still a UFO. TASeditor: the kept UFO is drawn pink instead of orange. Detect it from the pose/sprite, not from `$05E3`. | TV forum (inferred) | S |
| `$61D3` | Boss HP ("dynamic"). This is `$61CA,x` (MLB `OBJ_var0`) for slot 9, the first enemy slot, so enemy HP is probably `$61CA+slot` (inferred). Boss HP values: 60, Dedede 100, Shine/Bright 30+30 (JPW). | RA (S); structure: MLB/LOC | S |
| `$059B` | "Boss indicator" (FF none, F0 active) | RA | S |

## Objects / enemies (18 slots)
- Slots: 0 = scene/main task, 1 = Kirby, 3-5 = Kirby particles, 6-8 = Kirby projectiles, 9-17 = enemies/stage objects. LOC runtime trace; WDX enemy viewer uses slots 9-17.
- Per slot x: X = `$82+x`/`$94+x` (+frac `$70+x`), Y = `$B8+x`/`$CA+x` (+`$A6+x`). Script ID `$6128+x` (≥`$80` = empty). Collision class `$6200+x` (0 Kirby, 1 enemy, 3 inhalable, 5 hazard, 7 boss; LOC). Velocity `$60E0+x`/`$60F2+x`, `$6104+x`/`$6116+x`. Pose `$62C6+x`.
- WDX's "slot exists" test: `$62AB+i ≠ $80` for i = 0..8, i.e. `$62A2+x` for x = 9..17 (LOC: bit 7 = sleeping/suppressed).

## Frame, input, lag, RNG
| Addr | Meaning | Sources | St |
|---|---|---|---|
| `$003A` | Pad 1 held: bit7 A, 6 B, 5 Select, 4 Start, 3 Up, 2 Down, 1 Left, 0 Right | RA, LOC probe (0x81 = A+Right) | V |
| `$003C` | Pad 1 newly pressed (`held & ~prev`), computed at main-loop start (`$C32C`). `$6021` = previous held. `$E6`/`$E7` = gameplay copies of held/pressed. | LOC, MLB, KA-Rando | V |
| `$0067` | Soft-reset timer: init `$10` (16), counts down while A+B+Select+Start are held, RESET on underflow | LOC, RA | C |
| `$0039` | NMI counter: incremented each NMI (`$C37C INC $39`), cleared by the main-loop wait. MLB: `nmi_done_flag`. Not a monotonic frame counter. | LOC (runtime), ROM | V |
| `$603D` | Main-loop frame counter. Incremented once per completed game frame (`$CD75`); bit 0 selects the OAM page. **Unchanged over an emulated frame ⇒ lag frame** (derived, verify). | MLB (`frame_counter`), LOC (runtime) | V/derived |
| `$01A5` | **Lag flag / NMI handshake.** The NMI writes 1 at `$C373` (STA) and the main loop clears it at `$CD6D` when its frame is done. Lag test (MJ/feos, works on Rev A, ROM-checked): on execution of `$C373`, if `$01A5 == 1` the previous frame was lag. When polled once per frame, `$01A5 == 1` at frame end means the game was still waiting. MLB labels it `use_dynamic_chr0_bank`, but the runtime evidence wins. FCEUX and BizHawk lag counters are wrong for this game (forum). | TV 3411S, MJ, LOC (runtime 112/112 toggles), ROM | V |
| `$01ED` | JXQ's PRG0 lag flag. MUGG: "doesn't work at all". Ignore. | forum | X |
| `$003E`/`$003F` | **RNG** (16-bit). Each call runs 11 rounds of shift/rotate/xor (MJ `nRNG`). Landing-star direction = `$3E % 8` (0 up, clockwise). Enemy action 0-3 comes from ROM tables `$C6DD`/`$C7DD` (Waddle Doo: 0 jump, 1 walk, 2-3 attack). LOC calls these "sound params" (init `$77`); that label is wrong. | MJ (Masterjun P348723), MLB (`random_number`), TV 3990S | C |
| `$0042-$0047` | CHR bank shadows (sprite 0-1, 2-3; BG 0-3) | DC, MLB, LOC | C |

## Conflicts to settle once in the emulator (cheap checks)
1. `$0083/$0095` vs `$6075/$6087` for Kirby X. Both should track Kirby (zero-page live vs WRAM store copy). Log both while walking in 1-1 and pick the one that updates first.
2. `$05F4` (slope vs facing), `$05F7` (underwater vs grounded), `$05FB` bit 2.
3. `$0562-$0565` semantics (KALE room word vs LOC spawn X/Y).
4. `$0520` vs `$0559` as the stage index (both may be valid: entered vs selected).
5. `$61D3` boss HP: watch it drop by the JPW damage values (laser 3, star shot 10, piercing 25).
6. Lag: compare `$603D` deltas with the `$01A5` test over 1000 frames.
