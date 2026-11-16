# Handoff after round 3 (Yes/No delete, GPA across classes, what if)

For the fresh session that does the next round. Read `problem.md`, `spec.md`, `CLAUDE.md`
and `docs/decisions/` first; this file adds what they don't say. `handoff-round-1.md` and
`handoff-round-2.md` are still accurate for everything round 3 didn't touch.

## Current state

Rounds 1 to 3 (R1-R15 in `problem.md`) are built, committed and pushed.

- **R12 (changed):** deleting asks
  `Are you sure you want to delete "CSC 299"? It will be lost. Type Yes to delete it or No to keep it: `
  `Yes`/`No` in any capitals, with spaces around ignored. Anything else says
  `Please type Yes or No.` and asks again; `q` quits and keeps the class. Code:
  `ask_delete` in `gradecalc.py`.
- **R14:** with 2 or more saved classes, the saved-class list starts with
  `GPA across all your classes: 3.15 (average of 2 classes)`, then one line per class.
  Code: `average_gpa` in `grades.py` (the math), `gpa_across_classes` in `gradecalc.py`
  (the lines), called from `pick_saved_class`.
- **R15:** menu option 5 is what-if mode (`what_if` in `gradecalc.py`). It has its own
  menu: 1) Try a grade, 2) Leave what-if mode. Quit is now **6**.
- The open-class menu is: 1) Change a grade, 2) Change the goal, 3) Rename this class,
  4) Delete this class, 5) What if (try grades without saving), 6) Quit.
- `spec.md`: section 10 has the new delete question, 12 is what if, 13 is the GPA across
  classes. Decisions 15-22 are round 3's. Round 2 decision 10 is marked as replaced.
- `docs/decisions/`: 0003 (plain-average GPA, R14), 0004 (what-if works on a copy in
  memory, R15) and 0005 (Yes/No delete, R12). The next record is **0006**.
- `tests/`: 243 tests, all passing, none skipped (221 from rounds 1-2, 22 new). Every test
  has a `# Checks Rn.` comment.
- README describes what if, the Yes/No question and the GPA across classes.

## How to run

```
python gradecalc.py examples/example-class.txt    # first time with a file
python gradecalc.py                               # pick, rename or delete a saved class
python -m pytest                                  # run the tests
```

Windows 11, Git Bash, Python 3.13. Standard library only, plus pytest. No installs needed.

## Decisions made in round 3, and why

The student chose these when asked before any code was written:

- **Yes/No, any capitals, anything else asks again** (not also `y`/`n`, and not "anything
  but Yes keeps it"): no class is deleted or kept by a typo. Decision record 0005.
- **The GPA across classes is the plain average of each class's current GPA**, because the
  class files have no credits and adding them would change the saved file layout.
  Classes with no grades out yet are not counted. Decision record 0003.
- **It is shown automatically above the saved-class list** when there are 2 or more
  classes, not behind a letter or menu option.
- **What-if can change any item**, N/A or already out (for example a regrade).

These Claude chose, and the student approved them in review:

- What if is option 5 and Quit moves to 6, so Quit stays last (like decision record 0002).
  21 earlier tests had their last answer changed from `5` to `6`.
- What-if works on a copy of the grades in memory and never writes to `saved_classes/`,
  so `q` or closing the program in the middle can't change real grades (decision record
  0004). Leaving says `Left what-if mode. Your real grades are back.`
- What-if mode has no "change the goal"; the goal from outside is used.
- The GPA across classes has 2 decimals, .5 going up (Fractions, not `round()`), and no
  letter, since an average like 3.5 isn't on the scale.
- A saved class that breaks a file rule is listed as `can't be read, not counted` in the
  GPA block instead of stopping the program.

## Unresolved

- The round 2 problem "a class named `q` can't be deleted" is fixed by the R12 change.
- **Old wording in `spec.md`, still not fixed because nobody asked:** sections 1-7 say
  "bullet N" instead of R-numbers, sections 6 and 7 cite "bullet 12" and "bullet 13"
  (probably R10 and R11), and section 8 says the screen layout is not tested, though
  `test_the_screen_matches_the_spec_example` tests it. Section 8 also comes after
  section 11 in the file. Ask the student before changing any of these.
- Nothing is known to be broken.

## Warnings for the next session

- **Old CLI tests quit by typing `6`** as their last answer. If the menu changes again,
  they all break at once; say so in the commit message, as rounds 2 and 3 did.
- **The delete tests answer `yes`/`No`.** Any test that deletes needs a Yes answer.
- **The GPA block is printed before "Your saved classes:"** whenever there are 2 or more
  classes, so a test that checks `printed.startswith("Your saved classes:")` only works with
  0 or 1 class.
- **`main()` saves to the real `saved_classes/` by default.** Tests pass `folder=tmp_path`.
  For a real run, copy `gradecalc.py`, `grades.py`, `storage.py` and an example file into
  the scratchpad and run it there with `printf '...\n' | python gradecalc.py`.
- `git commit` prints "LF will be replaced by CRLF" warnings. They are harmless; ignore them.
