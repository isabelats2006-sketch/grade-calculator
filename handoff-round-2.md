# Handoff after round 2 (rename and delete)

For the fresh session that does round 3. Read `problem.md`, `spec.md`, `CLAUDE.md` and
`docs/decisions/` first; this file adds what they don't say. `handoff-round-1.md` covers the
round 1 build and is still accurate for everything round 2 didn't touch.

## Current state

Rounds 1 and 2 (R1-R13 in `problem.md`) are fully built, committed and pushed.

- **R12 (delete)** and **R13 (rename)** work from two places:
  - the open-class menu: 1) Change a grade, 2) Change the goal, 3) Rename this class,
    4) Delete this class, 5) Quit
  - the saved-class list (`python gradecalc.py` with no file): `r` or `d`, then the class's
    number
- `storage.py` has the new functions `rename_class` and `delete_class`.
- `gradecalc.py` has the new functions `ask_rename`, `ask_delete` and `_ask_number` (the
  shared "type a number from 1 to N" loop). `run_menu` now returns only when the open class
  was deleted, and `main` then goes back to the saved-class list.
- `spec.md` sections 9-11 describe rename, delete and the new list. Its decisions 8-14 are
  the round 2 ones.
- `docs/decisions/` has 0001 (class names stay file names) and 0002 (Quit moves to 5).
  The next record is **0003**.
- `tests/`: 221 tests, all passing, none skipped. That is 192 from round 1 plus 29 new ones in
  `test_storage.py` and `test_cli.py`. Every test has a `# Checks Rn.` comment.

## How to run

```
python gradecalc.py examples/example-class.txt    # first time with a file
python gradecalc.py                               # pick, rename or delete a saved class
python -m pytest                                  # run the tests
```

Windows 11, Git Bash, Python 3.13, pytest 9.2. Standard library only, no installs needed.

## Decisions made in round 2, and why

The student chose these when asked before any code was written:

- **Rename and delete are in both places** (menu and saved-class list), because R13 says
  "at any point".
- **"Special characters within reason" = everything Windows allows in a file name.** Only
  `\ / : * ? " < > |`, reserved names (CON, LPT1...) and a trailing dot are refused, using the
  same `check_name` as new classes. The class name stays the file name, so saved files keep
  the round 1 three-line layout (decision record 0001).
- **Deleting needs the class's name typed.** The question uses the student's R12 wording:
  `Are you sure you want to delete "CSC 299"? It will be lost. Type its name to delete it, or
  press Enter to keep it:`. The match is exact, capitals included, with only outer spaces
  ignored. Anything else keeps the class.
- **Renaming to another class's name is refused** (capitals ignored), so a rename can never
  wipe out a class. Changing only the capitals of the same class is allowed.

These I chose, and the student approved them in review:

- **Quit moved from 3 to 5** so it stays last (decision record 0002). The 13 round 1 tests
  that quit with `3` were changed to `5`, and the wrong-choice message is now
  "Please type 1, 2, 3, 4 or 5.". No other round 1 test changed.
- Enter at the rename question keeps the old name.
- After deleting the open class, it goes back to the list and asks the goal again for the next
  class. If no classes are left, it shows the round 1 "no saved classes yet" message and ends.
- If Windows refuses the rename or delete (for example, the file is open in another program),
  the program explains it and keeps the class (R8).

## Unresolved

- **A class named `q` can't be deleted from the confirmation question**, because `_ask` treats
  `q` as quit everywhere. It can still be deleted by hand from `saved_classes/`. The student
  knows and hasn't asked for a fix.
- **Old wording in `spec.md`, not fixed because nobody asked:**
  - Sections 1-7 still say "bullet N" instead of R-numbers.
  - Sections 6 and 7 cite "bullet 12" and "bullet 13", but those bullets don't exist.
    They probably mean R10 and R11.
  - Section 8 says "The screen layout is not tested", but `test_the_screen_matches_the_spec_example`
    does test it.
  - Ask the student before changing any of these.
- Nothing is known to be broken.

## Warnings for the next session

- **Old tests may need their menu answers changed** if the menu changes again. Many CLI tests
  quit by typing `5` as their last answer, so moving Quit breaks them all at once. Say so in the
  commit message if you change them, as round 2 did.
- **`main()` saves to the real `saved_classes/` by default.** Tests pass `folder=tmp_path`.
  For a real run, copy `gradecalc.py`, `grades.py`, `storage.py` and an example file into the
  scratchpad and run it there, piping the answers in with `printf '...\n' | python gradecalc.py`.
  Round 2 did this, and the student's real grades were never touched.
- `git commit` prints "LF will be replaced by CRLF" warnings. They are harmless on Windows;
  ignore them.
