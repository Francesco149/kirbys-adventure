# Sources (every source actually read for this knowledge base)
Format: URL or path — what it gave. Pages that failed to load are listed at the end and were **not** used.

## Local (read-only)
- /opt/src/nes-disasm-tool/docs/findings/memory-map.md — RAM catalog for our ROM (SHA1 F324E7C8…). Probe covered boot → hub → start of 1-1; some labels contradicted by other sources (see ram-map.md).
- …/findings/collision-detection.md — entity coordinate tables (`$70/$82/$94,x`, `$A6/$B8/$CA,x`, Kirby = slot 1), Kirby physics vars, probe stats.
- …/findings/scene-transition.md — `$056A` transition types, stage-clear code (`$0520`, `$0558`, `$0531`), checkpoint copy `$E581`.
- …/findings/entity-ability.md — `$05E3/$05E2/$0598`, slot categories, runtime script IDs (`$68` HAL, `$69` title, `$6C` intro). Its ability-ID names are wrong.
- …/findings/main-loop.md — `$01A5` handshake (NMI sets, main loop clears at `$CD6D`), `$603D`, `$39`.
- …/findings/controller-read.md (via memory-map) — `$3A/$3C/$6021`, soft-reset timer `$67`.
- /opt/src/nes-disasm-tool/projects/kirbys-adventure/src/ram.s — label catalog (same content as memory-map).
- /opt/src/nes-disasm-tool/probes/memory-map-trace.lua — what the "22/22 verified" checks actually test (HP `$2F`, lives 4, world/stage/room).
- /opt/src/kirbys-adventure/roms/usa-rev-a.nes — byte checks this session: PRG CRC32 8FFF3F32; no `RGKK_SetStillX` at 0x7FFF0; `$C371-$C37E` NMI code (`STA $01A5`, `INC $39`); `$C323` RTS; stage-clear routine at `$E4E0-$E540`; `$CABE` bit table.
- /opt/src/kirbys-adventure/tas/knowledge/ram-seed.json — the harness agent's emulator-verified X/Y (`$6075/$6087`, `$6099/$60AB`), HP 47 = full, −8 per hit, room 43 in 1-1.

## TASVideos
- https://tasvideos.org/41G — game id 41, versions, current publications, forum links.
- https://tasvideos.org/Games/41/Versions/List — PRG0 / E / JP hashes (no PRG1 entry).
- https://tasvideos.org/Games/PublicationHistory/41, https://tasvideos.org/Games/41/Goals/List, https://tasvideos.org/Movies-List-41G-Obs — publication chains and goals.
- https://tasvideos.org/Subs-List?GameId=41 — 10 submissions, status, judges.
- https://tasvideos.org/42M, /701M, /3226M, /1947M, /2406M, /3318M, /6192M, /6389M — publication pages.
- https://tasvideos.org/api/v1/publications/{id}, https://tasvideos.org/api/v1/submissions/{id} — frames, rerecords, emulator, ROM.
- https://tasvideos.org/172S, /1307S, /1314S, /3411S, /3976S, /3990S, /5227S, /5351S, /9286S, /9484S — author notes (route, tricks, RAM table in 3411S).
- https://tasvideos.org/GameResources/NES/KirbysAdventure — speed table, tricks, glitches, lag reduction, luck manipulation (no RAM table).
- https://tasvideos.org/UserFiles/Game/41 — WIP files and notes (TASeditor savings, DarkRiolu27 1-1 −29 f, MUGG corner-clip files).
- https://tasvideos.org/UserFiles/Info/638757648157501502, …/638757645500544857, …/638735711231534860, …/638328218865392835 (handler=Download) — TASeditor KirbyLogger.lua (`$05E1` states), keyword/WaddleDX viewer Lua (`$8B+i`, `$62AB+i`, `$67EE`).
- https://tasvideos.org/Forum/Topics/57 (pages 1-20) — main thread: PRG0/PRG1 sync, reset trick, RNG `$3E/$3F`, lag Lua, corner clips, rev differences.
- https://tasvideos.org/Forum/Topics/653, /4512, /4538, /12212, /14123, /14173, /18402, /18753, /25685, /25995, /2491 — submission threads (GEG PPU dependence, pause glitch remark, 6389M frame saves).
- https://tasvideos.org/3226M?handler=Download, https://tasvideos.org/6389M?handler=Download — movie files (headers, input landmarks).
- https://tasvideos.org/Games/193 — wrong game (Star Wars); not used.

## Scripts / code
- https://pastebin.com/raw/pT0hbSXN — Masterjun/feos Lua: RNG `$3E/$3F` 11-round step, enemy action tables `$C6DD/$C7DD`, lag hook at `$C373`/`$C323`, camera `$DD/$DE`.
- https://pastebin.com/raw/qLA90Fjq — MUGG Lua: X/Y position `$83/$95/$71`, `$B9/$CB/$A7`, speed `$05B9/$05BD`, lag `$01A5`.
- https://pastebin.com/raw/aAUh2Wtf, …/A7VXpUze, …/UiMj3GXE — further MUGG/forum Lua (`$95`/`$CB` "Map" = screen).
- https://raw.githubusercontent.com/WaddleDX/TAS/main/Other/KA_SpriteViewer.lua — player/enemy coordinates, camera, tile attributes.
- https://github.com/Nathan-R-Og/kirbyadventure (README, kirbysadventure.mlb, split.yaml) — Mesen labels for "USA (Rev 1)", our revision.
- https://raw.githubusercontent.com/devinacker/kale/master/kah.lua — room word `$0562`, `$055F=FF` warp, start screen/point.
- https://raw.githubusercontent.com/aquova/KA-Rando/master/docs/aquova_ka_notes.txt — `$6021` = controller input.

## Community RAM maps / wikis
- https://retroachievements.org/dorequest.php?r=codenotes2&g=1479 (POST) — 95 code notes: room-ID table, states, ability IDs, boss HP `$61D3`; hashlibrary (our MD5 listed).
- https://web.archive.org/web/2025id_/https://datacrystal.tcrf.net/wiki/Kirby%27s_Adventure/RAM_map — progress bits, HP/lives/ability, score.
- https://web.archive.org/web/2025id_/https://datacrystal.tcrf.net/wiki/Kirby%27s_Adventure/Notes — power IDs, Kirby state table, tile attributes, enemy data format, room IDs.
- https://web.archive.org/web/2026id_/https://datacrystal.tcrf.net/wiki/Kirby%27s_Adventure (and /ROM_map) — dumps PRG0/PRG1, mapper.
- https://web.archive.org/web/20261012113919/https://tcrf.net/Kirby%27s_Adventure (also 20250405193657 copy) — revision differences (Rev 0 / Rev 1, `RGKK_SetStillX`, Mike underflow fix).
- https://web.archive.org/web/2025id_/https://tcrf.net/Bugs:Kirby%27s_Adventure — 6-1 stone glitch block, crash outcomes.
- https://bacteriamage.wordpress.com/2018/11/29/unboxing-kirbys-adventure/ — PRG1 CRC32 8FFF3F32, PRG0 CRC32 9077A623.
- https://wikirby.com/wiki/Kirby%27s_Adventure (?action=raw) and the 7 world pages, all 46 `<World>_-_Stage_N` pages, The_Fountain_of_Dreams_(level) — room order, enemies, switches, hub unlocks.
- WiKirby boss/mid-boss pages: Whispy_Woods, Paint_Roller, Mr._Shine_%26_Mr._Bright, Kracko, Kracko_Jr., Heavy_Mole, Meta_Knight, King_Dedede, Nightmare, Bonkers, Bugzzy, Fire_Lion, Grand_Wheelie, Mr._Frosty, Mr._Tick-Tock, Poppy_Bros._Sr., Rolling_Turtle, Meta-Knights — patterns, drops.
- WiKirby misc: 100%25_completion, Extra_Mode, Boss_Endurance, Goal_Game, Warp_Star_Station, Museum, Arena_(Kirby%27s_Adventure), Big_Switch, Crane_Fever, Egg_Catcher, Quick_Draw_(Kirby%27s_Adventure), Drawing_Song, Cutscene, User:ShadowKirby/Title_screen, Glitches_in_Kirby%27s_Adventure, Speedrunning, Pause — menus, glitches, extras.
- https://strategywiki.org/wiki/Kirby%27s_Adventure/{Vegetable_Valley … The_Fountain_of_Dreams, Gameplay, Controls, Copy_Abilities, Items, Mini-games, Hidden_switches, Walkthrough, Enemies} — walkthrough, boss hit counts, switches.
- https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAAPE_en.pdf — manual: controls, file select, save, game over.

## speedrun.com / RTA
- https://www.speedrun.com/api/v1/games?name=Kirby%27s%20Adventure, /api/v1/games/om1mkxd2 (+/categories, /variables, /levels, /derived-games), /api/v1/series/2qnl90n5/games — game id, 9 categories and rules.
- https://www.speedrun.com/api/v1/leaderboards/om1mkxd2/category/{id}?top=5&embed=players, /api/v1/runs?game=om1mkxd2&category=… — records, platforms, regions.
- https://www.speedrun.com/api/v2/GetGameSummary?gameUrl=ka, …/GetGuideList?gameId=om1mkxd2, …/GetResourceList?gameId=om1mkxd2 — rules, timing, guides (goal-game frame info), resources.
- https://www.speedrun.com/api/v2/GetThread?id=43q9n, 8jt5o, t3crs, ajhwz, kcppk, 04u5s, 17o56, xqqex (and GetThreadList forumId 792x51z6) — timing change, Tornado control, stone-glitch timing, 2-3 clip, 5-2 OOB clip.
- https://web.archive.org/web/2025id_/https://www.speedrun.com/static/resource/1oy3u.zip?v=7ddff9e and …/shbuz.zip?v=2448803 — TheTerrificTracy NMG split files (ability per stage).
- https://seesaawiki.jp/ka_rta/ — JP RTA wiki: Any% (credits warp), overall route (ability switches, heal points), actions (physics, roulette, UFO charge frames, damage), glitches, lag, goal game, enemy HP, version differences, pages for 1-2 … 7-6, every boss.
- YouTube descriptions: elaKaDakA_U, AbYdqh3I-XY, JrdF8La7OjI, 6Sq0Kah5pao, DedIVeM6Q3I, w--YbSGMFeg, s-nImGEkzuY, XiMINtCzmMQ, uYrwL1UCo60, A4MYsoqKhhc, fyLPs_XIYk0, tE8K5EUKBfw — run platforms/versions, guide links.

## Failed / not used
- GameFAQs (403), kirby.fandom.com (402/403), manualzz (403), live tcrf.net and datacrystal.tcrf.net (Cloudflare/anti-bot; archived copies used instead), retroachievements.org web pages (403; API used), speedrun.com HTML pages (403; API used), the NMG Google Doc route (410), pastebin LYRHm83S (404), YouTube captions (empty).
