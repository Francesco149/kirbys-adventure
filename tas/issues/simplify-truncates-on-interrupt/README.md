# `kt simplify` leaves movie.txt truncated when it is interrupted (even with `--dry`)

Staged 2026-11-14 from the nix-lab dsh-bench (research/dsh-bench, task kirby-hal) for a look by whoever works on
this workbench: is it a real problem to solve, or was the caller using the tool wrong?

## What happened

A local model (Qwen3.8-Flash-Next IQ3_KS in DSH, the bench's "daily driver") solved `tasks/secret-hal.md`: at 88.6
minutes its own `kt check` printed PASS (6,867 frames) and `kt verify` MATCH, and it saved checkpoint `room48`. Its
next call, in the last minute of a 90-minute cap, was a dry run of the tail clean-up:

    kt simplify secret-hal --from 3583 --task tasks/secret-hal.md --mode frames --time-limit 180 --dry

The cap killed the process tree mid-search. `movie.txt` was left at 3,583 frames (only step 1 of 4 passes); the
passing movie survived only in `checkpoints/room48.movie` (= `movie.txt` here).

## Repro (about 1 minute, nothing outside a temp dir is touched)

    ./repro.sh            # interrupts simplify after 25 s
    before: 6867 frames   task secret-hal: PASS ...
    after:  3583 frames   task secret-hal: FAIL ...

## Why (drive.py / env.py as of 2026-11-14)

`cmd_simplify` does `run.truncate(a.start)` before searching and puts the tail back only at the end
(`run.play_masks(masks if not a.dry else tail)`). `Run.truncate` -> `persist()` writes the cut movie to disk at once.
Anything that ends the process in between (shell timeout, Ctrl-C, SIGTERM, an agent's time cap, an OOM kill) leaves
the run truncated; the `finally: run.close()` does not restore it. The help says "dry run, movie unchanged", and
DRIVER.md's advice to give a shell call a timeout above the search's makes the cut more likely when a caller
underestimates `--time-limit` + check time.

The caller did nothing the card forbids; arguably they should have checkpointed (they had) and `ck load` after.
Possible fixes, for whoever decides: keep the truncation in memory until the result is applied (or never for
`--dry`); or write the full movie back in a signal handler / `finally`; or print the checkpoint to load if
interrupted.

## Resolution (2026-11-14)

A real problem, not misuse: the help promises an unchanged movie for `--dry`, and any interrupted search lost the tail.
`cmd_simplify` now cuts the movie in memory only (`E.Env.truncate`, not `Run.truncate`, which persists), so
`movie.txt` keeps the whole movie until the result is applied by `play_masks` (an atomic write at the end), and with
`--dry` it is never shortened. `./repro.sh` now prints 6867 frames and PASS after the interrupt; an uninterrupted
`simplify --from 6000 --time-limit 30` on the same movie still applies (807 -> 795 frames, task PASS).
`drive.Run.truncate()` in scripts still writes to disk at once, by design (`kt rewind` relies on it).
