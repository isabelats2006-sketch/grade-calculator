# CLAUDE.md: grade calculator

A command-line app for my CSC 299 final project. Read `problem.md` (what it must do) and
`spec.md` (exactly how) before changing anything.

## Ground rules: the assignment's rules, never broken unless I say otherwise

- **problem.md is mine.** I write the requirements and any "Round N requirements" myself.
  Don't reword or add to it unless I ask, and keep my text.
- **Requirements come first.** In a round, my requirements are committed and pushed before
  any spec, test or code change.
- **Tests for everything.** Every new or changed behaviour gets a pytest test, and
  `python -m pytest` must pass with 0 failed and 0 skipped. A skipped test has not passed.
  A test must fail if the code it checks were wrong. When requirements have IDs (R1, R2...),
  each test names the ID it checks.
- **Commits:** one change per commit. The message says what changed and why. Never
  "update", "fix", "wip" or similar. Never undo or amend a commit.
- **Push at least once on every day of work.**
- **Never in the repo:** `.jsonl` transcripts, `.venv`, `node_modules`, API keys or
  passwords, `saved_classes/` (real grades), or any personal info. The repo is public.
- **README.md** always says what the program does, the command to run it, and the command
  to run the tests.
- **Runs with one command** on my computer. No API key, login or paid service.
- **Ask before installing anything.**

## How to run

```
python gradecalc.py csc299.txt     # open a class file
python gradecalc.py                # pick a saved class
python -m pytest                   # run the tests
```

## Code notes

- Python 3.13 on Windows, using Git Bash. Only the standard library, plus pytest for tests.
- Logic (reading files, grade math, goal math, saving) is kept apart from input/output, so
  it can be tested without typing.
- Grade math uses `fractions.Fraction`, not floats, so edge cases like 89.5% round
  correctly (with floats, 115 came out as 114.99999999999999).
- Rounding: nearest whole %, .5 goes up (Python's `round()` rounds .5 to even, so don't
  use it).
