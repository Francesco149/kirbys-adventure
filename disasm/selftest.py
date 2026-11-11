"""selftest.py - do the gates fail when they should?

Each case copies db/ to a scratch directory, plants one known error, runs `kd check` on the unit and expects
it to FAIL with the right complaint. Two more cases corrupt a corpus movie and a rendered source file. A gate
that cannot fail proves nothing, so this is run after every change to the tools (`kd selftest`).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
KD = os.path.join(HERE, "kd.py")

# (name, unit, file, old text (regex), new text, what the output must contain)
CASES = [
    ("wrong model of a routine", "rng", "rng.toml",
     r'expect = "\(rx << 8 \| ra\) == a \* x"', 'expect = "(rx << 8 | ra) == a + x"', "FAIL  rng.mul8.model"),
    ("wrong formula for a table", "rng", "rng.toml",
     r"== n \* n // 2 for n", "== n * n // 4 for n", "FAIL  rng.tables.values"),
    ("'only X writes it' with a writer left out", "rng", "rng.toml",
     r"'demo_init', 'random', 'video_init'\}", "'demo_init', 'random'}", "FAIL  rng.state.writers"),
    ("scratch claimed for a live variable", "rng", "rng.toml",
     r'poke = \{ "000D" = 0xA5,', 'poke = { "003E" = 0xA5,', "FAIL  rng.scratch.dead"),
    ("wrong per-frame relation", "rng", "rng.toml",
     r"== \(n\('random'\) > 0\)\"", "== (n('random') == 0)\"", "FAIL  rng.state.frames"),
    ("a name on an operand byte", "rng", "rng.toml",
     r'at = "3E:C8DD"', 'at = "3E:C8DE"', "not the first byte of an instruction"),
    ("a name in the wrong bank window", "rng", "rng.toml",
     r'at = "3E:C698"', 'at = "3E:8698"', "is mapped at"),
    ("a data region over executed code", "rng", "rng.toml",
     r'at = "3E:C7DD"\nlen = 256', 'at = "3E:C7DD"\nlen = 300', "were executed as code"),
    ("the same name twice", "rng", "rng.toml",
     r'name = "half_square_hi"', 'name = "half_square_lo"', "is defined twice"),
    ("a claim about a name that does not exist", "rng", "rng.toml",
     r'about = \["mul8"\]', 'about = ["mul9"]', "is not a defined name"),
    ("script opcode with an operand it does not have (the older notes' layout)", "vm", "vm.toml",
     r'name = "zero_e2"\nargs = \[\]', 'name = "zero_e2"\nargs = ["u8"]', "FAIL"),
    ("script opcode one byte short", "vm", "vm.toml",
     r'name = "set_vx_w"\nargs = \["u16"\]', 'name = "set_vx_w"\nargs = ["u8"]', "FAIL"),
    ("script opcode missing from the table", "vm", "vm.toml",
     r'\[\[opcode\]\]\nop = "38"\nname = "zero_vel"', '[[opcode]]\nop = "4F"\nname = "zero_vel"', "has no [[opcode]] entry"),
    ("wrong meaning for a script opcode", "vm", "vm.toml",
     r'expect = "wr\[0x6360 \+ thread\] == args\[0\] and length == 2"',
     'expect = "wr[0x6360 + thread] == args[0] + 1 and length == 2"', "FAIL  vm.op.wait"),
    ("jump condition inverted", "vm", "vm.toml",
     r"\(next == args\[0\]\) == \(rd\[0x63E0 \+ thread\] == 0\) or", "(next == args[0]) == (rd[0x63E0 + thread] != 0) or",
     "FAIL  vm.op.jeq"),
    ("poses (a CHR bank byte first) declared as plain sprite groups", "sprites", "sprites.toml",
     r'name = "poses_1C_8030"\nformat = "poses"', 'name = "poses_1C_8030"\nformat = "sprites"', "FAIL  sprites.format"),
    ("a pointer list that code indexes declared as a pose table", "sprites", "sprites.toml",
     r'name = "sprite_ptrs_31_9BC7"\nformat = "ptr16:31"', 'name = "sprite_ptrs_31_9BC7"\nformat = "poseptr:31"',
     "FAIL  sprites.format"),
    ("a sprite region left out of the database", "sprites", "sprites.toml",
     r'name = "sprites_38_A3DA"\nformat = "sprites"', 'name = "sprites_38_A3DA"\nformat = "bytes"', "FAIL  sprites.format"),
    ("the backwards copy of unpack modelled as a forwards copy", "unpack", "unpack.toml",
     r"v = out\[ref - i\] if c == 6 else out\[ref \+ i\]", "v = out[ref + i]", "FAIL  unpack.model"),
    ("a packed stream that expands to another number of bytes", "unpack", "unpack.toml",
     r'name = "packed_00_AA00"\nformat = "packed"\nunpacked = 2906', 'name = "packed_00_AA00"\nformat = "packed"\nunpacked = 2905',
     "FAIL  unpack.format"),
    ("a packed stream left out of the database", "unpack", "unpack.toml",
     r'name = "packed_00_AF9F"\nformat = "packed"', 'name = "packed_00_AF9F"\nformat = "bytes"', "FAIL  unpack.format"),
    ("a table of stream addresses without its table of banks", "unpack", "unpack.toml",
     r'format = "packlo:tileset_hi:tileset_bank"', 'format = "packlo:tileset_hi"', "FAIL  unpack.format"),
    ("a screen of 16 x 16 blocks instead of 16 x 12", "rooms", "rooms.toml",
     r"return \(len\(out\) == 218 \+ 192 \* \(max\(out\[8:8 \+ w \* h\]\) \+ 1\)\n            and all\(wr",
     "return (len(out) == 218 + 256 * (max(out[8:8 + w * h]) + 1)\n            and all(wr", "FAIL  rooms.load.data"),
    ("a door record of 4 bytes instead of 5", "rooms", "rooms.toml",
     r"\+ 5 \* rd\[0x56B\]", "+ 4 * rd[0x56B]", "FAIL  rooms.door.model"),
    ("Kirby's entry row read from the column nibble", "rooms", "rooms.toml",
     r"\(pos & 0x0F\) \* 16 \+ 9", "(pos >> 4) * 16 + 9", "FAIL  rooms.place.model"),
    ("an object list whose kinds start at byte 1 past the positions (not at the number of objects)", "rooms", "rooms.toml",
     r"and w\(0xF1\) == a \+ 2 \+ nc \+ total", "and w(0xF1) == a + 2 + nc + romrd[o + 1]", "FAIL  rooms.objs.head"),
    ("the lower tiles of a block taken from tables 1 and 2 instead of 2 and 3", "tiles", "tiles.toml",
     r"lower = 0x200 if py & 8 else 0", "lower = 0x100 if py & 8 else 0", "FAIL  tiles.row.model"),
    ("the second copy of a tile row 30 rows down the plane (a whole name table) instead of 24", "tiles", "tiles.toml",
     r"    p = t \+ 24\n", "    p = t + 30\n", "FAIL  tiles.row.model"),
    ("an attribute field whose vertical half is the same in both copies", "tiles", "tiles.toml",
     r"s = \(bx & 1\) \* 2 \+ \(r & 1\) \* 4", "s = (bx & 1) * 2 + (by & 1) * 4", "FAIL  tiles.attr_set.model"),
    ("a queue record with the address low byte first", "tiles", "tiles.toml",
     r"for b in \[n, hi, lo\] \+ data:", "for b in [n, lo, hi] + data:", "FAIL  tiles.ppu_write.model"),
    ("a block's index in its screen with column and row exchanged", "inroom", "inroom.toml",
     r"w\[0x10\] = rest & 0xF0 \| x >> 4", "w[0x10] = x & 0xF0 | rest >> 4", "FAIL  inroom.prop.model"),
    ("a door record's cell read from the high nibble of byte 0", "inroom", "inroom.toml",
     r"if romrd\[o\] & 15 == cell and", "if romrd[o] >> 4 == cell and", "FAIL  inroom.door.model"),
    ("a replaced block 8 after the old one instead of 8 before", "props", "props.toml",
     r"new = rd\[k\] - rd\[0x56D\] & 0xFF", "new = rd[k] + rd[0x56D] & 0xFF", "FAIL  props.break.model"),
    ("the two numbers of prop_extra exchanged", "props", "props.toml",
     r"return \(1, e\[0\] & 3, e\[0\] >> 2\)", "return (1, e[0] >> 2, e[0] & 3)", "FAIL  props.pair.model"),
    ("a current's direction and strength exchanged in the table index", "kblocks", "kblocks.toml",
     r"i = 3 \* \(e\[0\] & 3\) \+ \(e\[0\] >> 2\)", "i = 3 * (e[0] >> 2) + (e[0] & 3)", "FAIL  kblocks.current.model"),
    ("water_left answering carry set for a block that is water", "kblocks", "kblocks.toml",
     r"\[1 - \(rp & 1\)\] == bit7\(romrd\)", "[rp & 1] == bit7(romrd)", "FAIL  kblocks.water.left"),
    ("a sweep of Kirby's rectangle one column and one row short", "kblocks", "kblocks.toml",
     r"- first & 0xFF\) // 16 \+ 1", "- first & 0xFF) // 16", "FAIL  kblocks.break.rect0"),
    ("a broken block of shape 9 creating object $12 and one of shape $B object 3", "kblocks", "kblocks.toml",
     r"\(3 if s in small else 0x12\)", "(0x12 if s in small else 3)", "FAIL  kblocks.break.test0"),
    ("a camera that lets Kirby 144 pixels from its left edge instead of 128", "kmove", "kmove.toml",
     r"0xDD, 0x70, 0x80,", "0xDD, 0x70, 0x90,", "FAIL  kmove.move.model"),
    ("kirby_min_y applied as the largest Y instead of the smallest", "kmove", "kmove.toml",
     r"if s16\(\(py - u16\(rd, mem, 0x5CC\)\) & 0xFFFF\) < 0:", "if s16((py - u16(rd, mem, 0x5CC)) & 0xFFFF) >= 0:", "FAIL  kmove.move.model"),
    ("a locked camera whose right limit is its right edge (255) instead of 239", "kmove", "kmove.toml",
     r"cx \+ 0xEF & 0xFFFF", "cx + 0xFF & 0xFFFF", "FAIL  kmove.locked.model"),
    ("kirby_at_top answering for a downward velocity", "kmove", "kmove.toml",
     r"return bool\(rd\[0x5BE\] & 0x80\) and", "return not rd[0x5BE] & 0x80 and", "FAIL  kmove.at_top"),
    ("the two halves of a floor that rises over two blocks exchanged (classes 6 and 7)", "probes", "probes.toml",
     r"6: 15 - \(x >> 1\), 7: 7 - \(x >> 1\)", "6: 7 - (x >> 1), 7: 15 - (x >> 1)", "FAIL  probes.down.model"),
    ("a floor-only block (classes 2 and 3) that is a ceiling for probe_up as well", "probes", "probes.toml",
     r"    if c == 1:\n        c2 = below", "    if c in (1, 2, 3):\n        c2 = below", "FAIL  probes.up.model"),
    ("probe_left measuring to column 0 of a solid neighbour instead of its last column", "probes", "probes.toml",
     r"return \(0, -1 - x, k\)", "return (0, -x, k)", "FAIL  probes.left.model"),
    ("the handler at 3F:F600 given the formula of its sister cases (with the column)", "probes", "probes.toml",
     r"return \(0, -1 - 2 \* y, k\)", "return (0, y - 16 - x, k)", "FAIL  probes.right.model"),
    ("the block below the bottom row of a screen taken from the second row of the next screen", "probes", "probes.toml",
     r"i - 0xC0\)", "i - 0xB0)", "FAIL  probes.down.model"),
    ("the slope corrections of Kirby's left and right foot exchanged", "kcoll", "kcoll.toml",
     r"-6: \{4: 3, 6: 6, 3: -3, 5: -6\}, 6: \{3: 3, 5: 6, 4: -3, 6: -6\}", "-6: {3: 3, 5: 6, 4: -3, 6: -6}, 6: {4: 3, 6: 6, 3: -3, 5: -6}", "FAIL  kcoll.feet.left"),
    ("floor_approach with the velocity sums of the two 45 degree floors exchanged", "kcoll", "kcoll.toml",
     r"\{5: vx \+ vy, 6: vy - vx,", "{5: vy - vx, 6: vx + vy,", "FAIL  kcoll.approach.floor"),
    ("a foot that lands up to 16 pixels deep in a floor instead of 11", "kcoll", "kcoll.toml",
     r"if d == 0 or d >= 0xF5:\n        st\['land'\]", "if d == 0 or d >= 0xF0:\n        st['land']", "FAIL  kcoll.floor"),
    ("a wall that stops Kirby however deep he is in it", "kcoll", "kcoll.toml",
     r"return d if t < 0x80 else None", "return d", "FAIL  kcoll.wall"),
    ("the corrections of the side probes under a sloped ceiling with the wrong sign", "kcoll", "kcoll.toml",
     r"-6: \{7: -6, 8: 6\}, 6: \{7: 6, 8: -6\}", "-6: {7: 6, 8: -6}, 6: {7: -6, 8: 6}", "FAIL  kcoll.ceiling.model"),
    ("track streams declared as envelope streams", "snddata", "snddata.toml",
     r'format = "sndtrack"', 'format = "sndenv"', "FAIL  snddata.format"),
    ("a run of track streams left out of the database", "snddata", "snddata.toml",
     r'\[\[data\]\]\nat = "1D:9168"\n(?:.*\n){4}', "", "FAIL  snddata.format"),
    ("a run of track streams one byte short", "snddata", "snddata.toml",
     r'at = "1D:8DBC"\nlen = 932', 'at = "1D:8DBC"\nlen = 931', "FAIL  snddata.format"),
    ("a wrong note length in row 2 of the sound engine's length table", "sound", "sound.toml",
     r"\(2, 9\), \(3, 7\)", "(2, 8), (3, 7)", "FAIL  sound.tables.len"),
    ("the channels held by live sounds counted without the last slot", "sound", "sound.toml",
     r'rd\[0x6DA\] \| rd\[0x6DB\]"', 'rd[0x6DA]"', "FAIL  sound.sfx_chans"),
    ("a finished loop that drops two bytes of the stream's stack instead of three", "sound", "sound.toml",
     r"wr\[0x26\] == rd\[0x26\] \+ 3", "wr[0x26] == rd[0x26] + 2", "FAIL  sound.flow.loop"),
    ("an object's foot that counts as near a floor up to 7 pixels above it instead of 8", "ocoll", "ocoll.toml",
     r"1 if c or d >= 9 else 0", "1 if c or d >= 8 else 0", "FAIL  ocoll.test.land"),
    ("an object's wall test to the left that ignores a flat face at distance 0", "ocoll", "ocoll.toml",
     r"\(d >= 0 if flat else d > 0\)", "(d > 0)", "FAIL  ocoll.test.left.flat"),
    ("the answers of an object's walk for a wall and for a ledge exchanged", "ocoll", "ocoll.toml",
     r"9 if s == 1 else 5\)", "5 if s == 1 else 9)", "FAIL  ocoll.walk.model"),
    ("a speed above a profile's top braked whatever the keep flag says", "kvel", "kvel.toml",
     r"        if romrd\[O\('speed_keep'\) \+ y\]:\n            return sp\n", "", "FAIL  kvel.speed_step.model"),
    ("the slope table of Kirby's X velocity used on floor kind 6 instead of 5", "kvel", "kvel.toml",
     r"if rd\[0x5F4\] != 5:", "if rd[0x5F4] != 6:", "FAIL  kvel.vx_apply.model"),
    ("gravity's limit applied whatever the sign of the velocity", "kvel", "kvel.toml",
     r"    if \(v \^ acc\) & 0x8000:\n        return v\n", "", "FAIL  kvel.gravity.model"),
    ("the far call's bank byte and address exchanged in the model of its inline bytes", "frame", "frame.toml",
     r"    \(o0, lo\), \(o1, hi\), \(o2, bank\) = it", "    (o0, bank), (o1, lo), (o2, hi) = it", "FAIL  frame.far_call.model"),
    ("a lost life that does not refill the health", "frame", "frame.toml",
     r"r\('lives'\) == pr\('lives'\) - 1 and r\('hp'\) == r\('hp_max'\)", "r('lives') == pr('lives') - 1 and r('hp') == pr('hp')",
     "FAIL  frame.leave.life"),
    ("the bit of a finished stage taken from stage_kind instead of the stage door", "frame", "frame.toml",
     r"\| 1 << rd\[0x559\], 0x55F: 0xFF\}", "| 1 << rd[0x520], 0x55F: 0xFF}", "FAIL  frame.stage_mark_done.model"),
    ("lives without their limit of 99", "frame", "frame.toml",
     r"expect = \"r\('lives'\) == 99 and", "expect = \"r('lives') == 100 and", "FAIL  frame.lives_add.limit"),
    ("a fade step of 8 instead of 16 per level", "video", "video.toml",
     r"c = c \+ 16 \* lv & 0xFF", "c = c + 8 * lv & 0xFF", "FAIL  video.color_fade.model"),
    ("the status bar's split one line early", "video", "video.toml",
     r"0xC000: 0xAF, 0xC001: 0xAF, 0xE001: 0xAF", "0xC000: 0xAE, 0xC001: 0xAE, 0xE001: 0xAE", "FAIL  video.split_setup.model"),
    ("the Y scroll register sent from the wrong byte", "video", "video.toml",
     r"0x2005: rd\[0xEA\] \+ rd\[0x1A4\] & 0xFF", "0x2005: rd[0xEB] + rd[0x1A4] & 0xFF", "FAIL  video.scroll_send.model"),
    ("the shut bit of a hub door giving the open door's block", "roomtick", "roomtick.toml",
     r"c = 0xFE if rd\[0x78D3\] & bit else 0xFA", 'c = 0xFA if rd[0x78D3] & bit else 0xFE', "FAIL  roomtick.doors.model"),
    ("the hub's floating marks at half speed", "roomtick", "roomtick.toml",
     r"4 \* sx8\(g\(pos \+ 6 \+ x\)\)", '2 * sx8(g(pos + 6 + x))', "FAIL  roomtick.anim.model"),
    ("wind streaks that go up starting at Y = $B0", "roomtick", "roomtick.toml",
     r"w\[0x78DF \+ x\] = 0xA0\n", 'w[0x78DF + x] = 0xB0\n', "FAIL  roomtick.wind.model"),
    ("an hp bar per 8 points with none for the first", "hud", "hud.toml",
     r'else \(hp >> 3\) \+ 1', 'else (hp >> 3)', "FAIL  hud.update.model"),
    ("the score without its fixed last digit", "hud", "hud.toml",
     r'buf\[13\] = 0xDC', 'buf[13] = 0x81', "FAIL  hud.update.model"),
    ("the enemy's bar of type $47 scaled to a half instead of 5/8", "hud", "hud.toml",
     r'v = \(\(v >> 2\) \+ v\) >> 1', 'v = v >> 1', "FAIL  hud.update.model"),
    ("the card in a hub one tile off", "hud", "hud.toml",
     r'buf\[1\] = buf\[1\] - 0x10 & 0xFF', 'buf[1] = buf[1] - 0x0F & 0xFF', "FAIL  hud.update.model"),
    ("Kirby's body one pixel wider for the objects' hit test", "hit", "hit.toml",
     r'0x6087\), 4, rd\.get\(0x50E, 0\)\)\"', '0x6087), 5, rd.get(0x50E, 0))"', "FAIL  hit.kirby.box"),
    ("the last score amount 25000 instead of 20000", "hit", "hit.toml",
     r'8000, 10000, 20000\] and', '8000, 10000, 25000] and', "FAIL  hit.score.tables"),
    ("a shot's survivor reaction read from the wrong record byte", "hit", "hit.toml",
     r'hit_strike\(dmg, 0x0C, 9, rd, wr, romrd, mem\)\n\ndef hit_all', 'hit_strike(dmg, 0x0F, 9, rd, wr, romrd, mem)\n\ndef hit_all', "FAIL  hit.shot.box7"),
    ("Kirby's low body box used for action 9 instead of 6", "khelp", "khelp.toml",
     r'rd\[0x5E1\] == 6 else 0', 'rd[0x5E1] == 9 else 0', "FAIL  khelp.upkeep.model"),
    ("a double tap allowed within 32 frames instead of 16", "khelp", "khelp.toml",
     r'0xFF if t \+ 1 >= 0x10 else', '0xFF if t + 1 >= 0x20 else', "FAIL  khelp.pad.double_tap"),
    ("a ladder as shape 2 instead of 1", "khelp", "khelp.toml",
     r'shapes\(romrd\) == \[1\]\)', 'shapes(romrd) == [2])', "FAIL  khelp.ladder"),
    ("an object's fall limited to 4 pixels a frame instead of 3", "ohelp", "ohelp.toml",
     r'oh_fall\(oh_w\(rd, 0x6104, 0x6116, rx\), 0x15, 3\)', 'oh_fall(oh_w(rd, 0x6104, 0x6116, rx), 0x15, 4)', "FAIL  ohelp.gravity"),
    ("an object that turns its back to Kirby", "ohelp", "ohelp.toml",
     r'\(0x40 if oh_dist\(oh_wx\(rd, rx\), oh_wx\(rd, 1\)\)\[1\] else 0xC0\) and calls', '(0xC0 if oh_dist(oh_wx(rd, rx), oh_wx(rd, 1))[1] else 0x40) and calls', "FAIL  ohelp.face.kirby"),
    ("an object's flicker by bit 0 of the frame counter instead of bit 1", "ohelp", "ohelp.toml",
     r'0xE7 if rd\[0x603D\] & 2 else 0x89', '0xE7 if rd[0x603D] & 1 else 0x89', "FAIL  ohelp.flicker"),
    ("the UFO's diagonal as fast upward as straight up", "kst17", "kst17.toml",
     r"UVY = \[-0x200, -0x100", 'UVY = [-0x200, -0x200', "FAIL  kst17.ufo_velocity.model"),
    ("the Star Rod walk with the pad sides exchanged", "kst17", "kst17.toml",
     r"0x01 if face & 0x80 else 0x02", '0x02 if face & 0x80 else 0x01', "FAIL  kst17.rod_walk.model"),
    ("the Star Rod skid one exit short", "kst17", "kst17.toml",
     r"'kirby_st_rod_skid': \(3,", "'kirby_st_rod_skid': (2,", "FAIL  kst17.rod.frames"),
    ("Sword Kirby's stand reading the wrong pad bit", "kst15", "kst15.toml",
     r"\('15:A069', held\(rd, 0x04\)\)", "('15:A069', held(rd, 0x08))", "FAIL  kst15.sword.stand"),
    ("Sword Kirby's flap reading the next table byte", "kst15", "kst15.toml",
     r"0x4280A in romrd", '0x4280B in romrd', "FAIL  kst15.sword.flap"),
    ("the hub's camera pan stepping X by the Y distance", "kst15", "kst15.toml",
     r"\(cx \+ step16\(dx\)\)", '(cx + step16(dy))', "FAIL  kst15.hub.pan_setup"),
    ('Down while standing leading to the slide instead of the duck', 'kst14', 'kst14.toml',
     r'\("14:A7CA", A\("kirby_s_duck"\)\)', '("14:A7CA", A("kirby_s_slide"))', 'FAIL  kst14.stand.model'),
    ('the duck given script number $0E', 'kst14', 'kst14.toml',
     r'0x0F: "kirby_s_duck"', '0x0E: "kirby_s_duck"', 'FAIL  kst14.scripts.table'),
    ('a held jump of 24 frames instead of 23', 'kst14', 'kst14.toml',
     r"n\('kirby_st_jump_held'\) == 23 and", "n('kirby_st_jump_held') == 24 and", 'FAIL  kst14.jump.effect'),
    ("two entries of the effects' jump table exchanged", "kfx", "kfx.toml",
     r"0xAC72, 0xAC7B", '0xAC7B, 0xAC72', "FAIL  kfx.start.table"),
    ("the bubble's fourth sway velocity wrong", "kfx", "kfx.toml",
     r"\(0x100, 0x40, 0xFF00, 0xFFC0\)\[v\]", '(0x100, 0x40, 0xFF00, 0xFF40)[v]', "FAIL  kfx.bubble.tick"),
    ("the run dust two pixels off for one facing", "kfx", "kfx.toml",
     r"placed\(rd, wr, \(-4, 4\)", 'placed(rd, wr, (-4, 6)', "FAIL  kfx.dust.place"),
    ("the walker's wait before its first jump $40 frames instead of $50", "en24a", "en24a.toml",
     r"wr\[v2\] == 0x50 and e24_script\(wr, 0x19, 0xA0\)", 'wr[v2] == 0x40 and e24_script(wr, 0x19, 0xA0)', "FAIL  en24a.e0e.tick_air"),
    ("the cannon's last shot life wrong", "en24a", "en24a.toml",
     r"E10_LIFE = \[0xD6, 0x96, 0x6B, 0x53\]", 'E10_LIFE = [0xD6, 0x96, 0x6B, 0x63]', "FAIL  en24a.e10.tables"),
    ("the hopping blob's high hop tied to hop kind 3 instead of 1", "en24a", "en24a.toml",
     r"\(0x60, 0xFC00\) if rd\[0x6236 \+ rd\[0x6E\]\] == 1 else", '(0x60, 0xFC00) if rd[0x6236 + rd[0x6E]] == 3 else', "FAIL  en24a.e11.hop_set"),
    ("the wave flier's turn velocity one unit off", "en26a", "en26a.toml",
     r"E38_VY = \(0x028A", 'E38_VY = (0x028B', "FAIL  en26a.e38.tick_wave"),
    ("the sitting flier taking off at 48 pixels instead of 64", "en26a", "en26a.toml",
     r"e26_dx\(rd\)\[0\] < 0x40", 'e26_dx(rd)[0] < 0x30', "FAIL  en26a.e38.tick_sit"),
    ("the spiked ball's hover and rise paths exchanged", "en26a", "en26a.toml",
     r"\(A\('e39_hover'\), A\('e39_rise'\)", "(A('e39_rise'), A('e39_hover')", "FAIL  en26a.e39.start.path"),
    ("a wrong pose in the wheel's pose table", "kst18", "kst18.toml",
     r"\[8, 8, 10, 12, 12, 14\]\[wr\[0x61CB\]\]", '[8, 8, 10, 12, 14, 14][wr[0x61CB]]', "FAIL  kst18.wheel_pose.model"),
    ("the spit with a mouthful on A instead of B", "kst18", "kst18.toml",
     r"\('18:AFBC', 0x58, new\(rd, 0x40\)\)", "('18:AFBC', 0x58, new(rd, 0x80))", "FAIL  kst18.full_stand.model"),
    ("the tornado spinning on A held instead of B", "kst18", "kst18.toml",
     r"ran\('18:AB17'\) == \(1 if rd\[0xE6\] & 0x40 else 0\)", "ran('18:AB17') == (1 if rd[0xE6] & 0x80 else 0)", "FAIL  kst18.tornado_spin.model"),
    ("the hopper's table of slopes it walks up changed", 'en24b', 'en24b.toml',
     r'E12_SLOPE = \[1, 0, 0, 1, 1, 0, 0, 1\]', 'E12_SLOPE = [1, 0, 1, 0, 1, 0, 0, 1]', 'FAIL  en24b.e12.tables'),
    ('the thrown rider hittable one frame early', 'en24b', 'en24b.toml',
     r'\("e12_hit" in calls\) != \(r8 <= 1\)', '("e12_hit" in calls) != (r8 <= 2)', 'FAIL  en24b.e12.tick_thrown'),
    ("the laser ball's hold timer one frame off", 'en24b', 'en24b.toml',
     r't, n3 = 0x37, \(n3 - 1\) & 0xFF', 't, n3 = 0x38, (n3 - 1) & 0xFF', 'FAIL  en24b.e16.tick_hold'),
    ("the blade fighter's third lunge step slower", 'en25a', 'en25a.toml',
     r'E2B_LUNGE = \[0x0480, 0x0300, 0x0240', 'E2B_LUNGE = [0x0480, 0x0300, 0x0200', 'FAIL  en25a.e2b.tables'),
    ("the parasol carrier's two sway timers exchanged", 'en25a', 'en25a.toml',
     r't = \(0x1B if ran\("25:A10B"\) else 0x48\) \+ 1', 't = (0x48 if ran("25:A10B") else 0x1B) + 1', 'FAIL  en25a.e2a.tick_float'),
    ("the jumper's odds always out of 16", 'en25a', 'en25a.toml',
     r'lim = rd\[0x6236 \+ s\] or E2C_ODDS_MAX\[row\]', 'lim = rd[0x6236 + s] or 16', 'FAIL  en25a.e2c.choose'),
    ("the walk with an ability declared to keep the plain walk's order of tests", 'kst14b', 'kst14b.toml',
     r'"walk": \("order"', '"walk": ("same"', 'FAIL  kst14b.mirror.static'),
    ("the ladder's climbing speed wrong", 'kst14b', 'kst14b.toml',
     r'0x0133 if ran', '0x0100 if ran', 'FAIL  kst14b.ladder.model'),
    ("Select leaving Kirby in the ability's set of states", 'kst14b', 'kst14b.toml',
     r'ram\[0x5E0\] == 0 and ctl\[0x5E3\]', 'ram[0x5E0] == 2 and ctl[0x5E3]', 'FAIL  kst14b.select.effect'),
    ("one weight of the wall climber's choice changed", 'en24c', 'en24c.toml',
     r'E19_ODDS = \[0x3C, 0x50, 0x50', 'E19_ODDS = [0x3C, 0x50, 0x51', 'FAIL  en24c.e19.tables'),
    ("the fire spitter's wait one frame longer", 'en24c', 'en24c.toml',
     r'wr\[v3\] == 1 and wr\[v2\] == 0x3C', 'wr[v3] == 1 and wr[v2] == 0x3D', 'FAIL  en24c.e29.tick_walk'),
    ("the wall climber's leap planned for half the gravity", 'en24c', 'en24c.toml',
     r'vy = \(q - 16 \* t\)', 'vy = (q - 8 * t)', 'FAIL  en24c.e19.leap_set'),
    ("a created object's facing offset not mirrored for a creator that faces left", 'khelp2', 'khelp2.toml',
     r'\(f - b\[3\] if left else f \+ b\[3\]\)', '(f + b[3] if left else f - b[3])', 'FAIL  khelp2.spawn_rec'),
    ("an effect's rank stored with its bit 7", 'khelp2', 'khelp2.toml',
     r'1: v1, 2: rank & 0x7F, 3: num', '1: v1, 2: rank, 3: num', 'FAIL  khelp2.fx_create.model'),
    ('the resume answering run only above the run speed', 'khelp2', 'khelp2.toml',
     r'2 if 0x14C < sp < 0x8000 else 1\), True', '2 if 0x1CC < sp < 0x8000 else 1), True', 'FAIL  khelp2.resume.model'),
    ("one of the breath's Y velocities wrong", "en26b", "en26b.toml",
     r"E3A_VY = \(0xFEF0, 0x0200", 'E3A_VY = (0xFEF0, 0x0180', "FAIL  en26b.e3a.breath_vel"),
    ("the roller's wait the same for both speed classes", "en26b", "en26b.toml",
     r"kw\['v5'\] = \(0x3C, 0x1E\)\[rd\[0x784 \+ o\]\]", "kw['v5'] = (0x3C, 0x3C)[rd[0x784 + o]]", "FAIL  en26b.e3c.tick"),
    ("the dust puff on the wrong side of its maker", "en26b", "en26b.toml",
     r"\(2, 0xFE\)\[rd\[0x61DC \+ o\] >> 7\]", '(0xFE, 2)[rd[0x61DC + o] >> 7]', "FAIL  en26b.e59.place"),
    ("the coconut's second gravity wrong", "en25b", "en25b.toml",
     r"E1A_GRAV = \[0x15, 0x30\]", 'E1A_GRAV = [0x15, 0x20]', "FAIL  en25b.e1a.tables"),
    ("the hoverer stretching its phases at the wrong distance", "en25b", "en25b.toml",
     r"long = wr\[0x02\] >= 11 and", 'long = wr[0x02] >= 16 and', "FAIL  en25b.e2f.tick_hover"),
    ("the ice block tossed at half its speed", "en25b", "en25b.toml",
     r"0xBB61: 0x0100, 0xBB66", '0xBB61: 0x0080, 0xBB66', "FAIL  en25b.e5e.toss"),
]


def run_kd(args, dbdir=None):
    env = dict(os.environ)
    if dbdir:
        env["KD_DB"] = dbdir
    r = subprocess.run([PY, KD] + args, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


def db_cases(log, only=None):
    ok = True
    for name, unit, fname, old, new, want in CASES:
        if only and unit not in only:
            continue
        tmp = tempfile.mkdtemp(prefix="kd-selftest-")
        try:
            for f in os.listdir(os.path.join(HERE, "db")):
                shutil.copy(os.path.join(HERE, "db", f), tmp)
            p = os.path.join(tmp, fname)
            s = open(p).read()
            s2, n = re.subn(old, new.replace("\\", "\\\\"), s, count=1)
            if n != 1:
                log(f"  ??      {name}: the text to change was not found (update selftest.py)")
                ok = False
                continue
            open(p, "w").write(s2)
            code, out = run_kd(["check", "--unit", unit, "--no-build", "--no-status", "-v"], tmp)
            caught = code != 0 and want in out
            line = next((ln.strip() for ln in out.splitlines() if want in ln), "")
            log(f"  {'caught' if caught else 'MISSED'}  {name}" + (f"   <- {line[:110]}" if caught else ""))
            ok = ok and caught
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return ok


def movie_case(log):
    """A corpus movie with one frame of input changed must not reproduce its recorded RAM hash."""
    sys.path.insert(0, HERE)
    import multiprocessing as mp
    import evidence as EVD
    rows = EVD.manifest()
    mid, frames, sha = min(rows, key=lambda r: r[1])[:3]
    src = open(EVD.movie_path(mid)).read()
    tid = "_selftest"
    # hold Right+A for the last 600 frames instead of what the movie did
    sys.path.insert(1, os.path.join(os.path.dirname(HERE), "tas"))
    import env as E
    masks = E.parse_spec(src)
    masks[-600:] = [E.LETTERS["R"] | E.LETTERS["A"]] * 600
    open(EVD.movie_path(tid), "w").write(E.rle(masks) + "\n")
    try:
        with mp.get_context("spawn").Pool(1) as pool:
            _, good, msg, _ = pool.apply(EVD._movie_job, ((tid, 4000, sha),))
    finally:
        os.remove(EVD.movie_path(tid))
        shutil.rmtree(os.path.join(EVD.EV, "snaps", tid), ignore_errors=True)
        p = os.path.join(EVD.EV, "movie", tid + ".npz")
        if os.path.exists(p):
            os.remove(p)
    caught = not good and "RAM hash" in msg
    log(f"  {'caught' if caught else 'MISSED'}  a corpus movie ({mid}) with its last 600 frames of input replaced"
        + (f"   <- {msg[:60]}" if caught else ""))
    return caught


def build_case(log):
    """One byte changed in a rendered source file must fail the rebuild."""
    sys.path.insert(0, HERE)
    import db as DBM
    import evidence as EVD
    import kd
    import render
    import rommodel as RM
    d = DBM.DB()
    m = RM.Model(EVD.Evidence(), db=d)
    lock = kd.locked("build")
    try:
        render.Renderer(m, d).write()
        p = os.path.join(render.OUT, "src", "bank3E.s")
        s = open(p).read()
        s2 = s.replace("    ldx #$0B", "    ldx #$0C", 1)          # random: 11 rounds -> 12
        assert s2 != s
        open(p, "w").write(s2)
        good, msg = render.build(m)
        render.Renderer(m, d).write()
        back, _ = render.build(m)
    finally:
        lock.close()
    caught = not good and "first difference" in msg and back
    log(f"  {'caught' if caught else 'MISSED'}  one operand changed in the rendered source   <- {msg[:70]}")
    return caught


def main(log=print, only=None):
    log("planted errors that the gates must catch:")
    ok = db_cases(log, only)
    if only:
        log(f"selftest (units {', '.join(only)} only): {'PASS, every planted error was caught' if ok else 'FAIL'}")
        return ok
    ok = movie_case(log) and ok
    ok = build_case(log) and ok
    log(f"selftest: {'PASS, every planted error was caught' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
