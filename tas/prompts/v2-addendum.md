# Recipe v2 addendum (2026-11-10): search without scores. Where it conflicts with the older recipe below, this wins.

The `search` tool has a third mode, `explore`, and there is a `go` tool. Use them first; fall back to beams and
hand-written scores only to squeeze frames or when an explore search fails twice.

**`search` with `mode: "explore"`** needs no score. It keeps one state per *cell*, expands rarely-visited cells
with random macro-actions until `goal` holds, then spends `refine` seconds shortening the path.
- `goal`: the predicate you want, or a stepping stone. "Somewhere new" is valid: `room not in (43, 44)`.
- `cell`: a tuple expression saying what counts as a different situation. Default `(room, x//16, y//16)`.
  **Put the mechanic's state in the cell**: an object being present, a boss HP variable, an ability, a camera
  position. Define a variable for it with `ram define` and add it to the tuple. When nothing moves (the goal
  game, cutscenes, timing presses) put time in it: `(room, frame//20)`.
- `avoid`: everything that must survive (`hp < 31`, `hp > 47` while dying, `ability != 23`, a wrong room).
- `actions`: omit them for the walking alphabet (it has no long B hold: add `B*24`, `RB*16`, `D*6` to inhale and
  swallow; add `L*2`, `R*2` when a few pixels matter).
- `time_limit` (default 75 s) and `refine` (default 8 s). `apply: true` plays the result.
- No map dump, door coordinates or score are needed to leave a room: goal `room not in (<this>, <previous>)`.

**`go`** chains explore searches: each step reaches a value of `var` (default `room`) not seen yet in this call,
until `until` holds. One call can carry Kirby through a whole stage: `go(until="room == 42")`, then one explore
search with a time cell through the goal game to the hub. It goes to *any* unseen room, so in hubs and rooms with
optional doors use `search` with the room you want in the goal and the wrong ones in `avoid`.

**Fights** work the same way: define the boss HP variable (mark → one hit → diff; `ram objects` now lists every
live object with its script id, including Warp Stars and pickups), then explore with goal `bhp < <current>` and
cell `(x//16, y//16, bhp, mouth)`, actions with `B*24` holds; repeat per hit, or goal `bhp == 0` in one call
with a longer `time_limit`.

**Contact is not completion**: a Warp Star needs Kirby standing on it ~20 frames and then ~100 frames of ride; a
Star Rod piece and the hub return take hundreds of frames. Search for the contact, then `play .*N` and read events.

Measured on 2026-11-10 with these tools: an invisible door found in 16 s from the goal "a room that is not one of
the known ones"; three rooms as UFO in one `go` call (66 s); the HAL-room trick (an object unloading) in 4 s once
the object count was in the cell.
