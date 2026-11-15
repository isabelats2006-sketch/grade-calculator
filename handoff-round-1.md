# Handoff after round 1 (the first build)

For the fresh session that does round 2. Read `problem.md`, `spec.md` and `CLAUDE.md` first;
this file adds what they don't say.

## Current state

Round 1 (the initial requirements, R1-R11 in `problem.md`) is fully built and pushed.

- `grades.py`: all the logic. It reads and checks a class file (`parse_class`), works out the
  current grade (`current_grade`, `round_percent`, `letter_for`), reads a goal (`parse_goal`),
  finds the % needed on N/A items (`needed_for`, `describe_needed`), checks one typed grade
  (`parse_grade`), and shows numbers exactly (`show_number`).
- `storage.py`: saving classes by name in `saved_classes/<name>.txt` (save, list, find, load,
  `check_name`).
- `gradecalc.py`: the program the user runs. It asks the questions, shows the screen and the
  menu, and gets `ask`/`say` passed in so tests can type answers.
- `tests/`: 192 tests, all passing, none skipped. Every test has a `# Checks Rn.` comment
  naming the requirement(s) it checks. Every one of R1-R11 is named.
- `examples/example-class.txt`: a made-up class file to try.

## How to run

```
python gradecalc.py examples/example-class.txt    # first time with a file
python gradecalc.py                               # pick a saved class
python -m pytest                                  # run the tests
```

Windows 11, Git Bash, Python 3.13, pytest 9.2. Standard library only, no installs needed.

## Decisions made in round 1, and why

- **Exact math with `fractions.Fraction`, never floats.** With floats, 17.9/20 came out as
  89.4999…% and rounded to a B+ instead of an A-. There is a test for that exact case.
- **Rounding: nearest whole %, .5 goes up**, with `math.floor(x + 1/2)`. Python's `round()`
  sends .5 to the even number (`round(92.5) == 92`), so it is not used.
- **The needed % is rounded UP**, and a final of goal - 0.5% counts, because of the rounding
  above. `test_every_answer_is_checked_by_filling_in_the_na_items` checks that the needed %
  reaches the goal and that 1% less does not.
- **File layout is three lines** (names with `/`, weights, grades). Anything after `=` is a
  note. The names and order are strict (R2); `hw`/`assignments` count as homework.
- **The goal is asked after the program starts** (not an argument): letter, GPA (number ≤ 4)
  or percent (number > 4 or with %).
- **Saved classes live in `saved_classes/`**, which is in `.gitignore` because it holds real
  grades. Names Windows can't use are refused; capitals don't create duplicates.
- **Weights and names are changed by editing the saved file by hand.** The menu only changes
  grades and the goal (spec decision 7).
- The full list of small decisions is at the end of `spec.md`.

## Unresolved

- Nothing is known to be broken.
- `problem.md` still has the student's own typos (her wording is kept on purpose; don't fix it).

## Warnings for the next session

- **Never edit `problem.md` except to add what the assignment calls for**, and tell the student
  first. She writes every "Round N requirements" section herself.
- **Show every commit message and wait for her OK before committing.** Never undo or amend a
  commit.
- **New and changed requirements get new tests named with their ID**, using the same
  `# Checks Rn.` comment. A changed requirement keeps its number; a removed one stays in
  `problem.md`, marked removed. New requirements get new numbers (R12, R13, …), never reused.
- **Each round needs at least one Y-statement decision record** in `docs/decisions/`
  (0001, 0002, …). None exist yet; round 2 makes the first.
- When breaking the code on purpose to check that a test fails, check that the break really
  happened. Once a `sed` command silently changed nothing.
- Lines in `saved_classes/` and `examples/` are lined up with spaces; `class_to_text` always
  leaves at least one space after each value (a long value once ran into the next one).
