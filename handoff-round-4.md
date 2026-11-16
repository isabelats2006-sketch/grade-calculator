# Handoff after round 4 (each item's percentage, splitting a category)

For the fresh session that does the next round. Read `problem.md`, `spec.md`, `CLAUDE.md`
and `docs/decisions/` first; this file adds what they don't say. The handoffs for rounds 1
to 3 are still accurate for everything round 4 didn't touch.

## Current state

Rounds 1 to 4 (R1-R17 in `problem.md`) are built, committed and pushed. The working tree
was clean after the last round 4 commit (`e6dade2`).

- **R16:** under the table, after the line `-------------------- === --------------------`,
  each item has its own line (`homework:       15 out of 20 = 75%`, `final:          N/A`,
  `attendance:     not in this class` for weight 0), then `TOTAL:` (the current grade, or
  `no grades out yet`). Then a blank line and the "You need..." sentence. It is on the normal
  screen and in what-if. Code: `item_lines` and `SEPARATOR` in `gradecalc.py`,
  `item_percent` in `grades.py`. Spec section 14.
- **R17, in the file:** a split category is its name repeated side by side, one per part
  (`homework / homework / midterm / ...`), capitals ignored. The file is still 3 lines and
  the numbers (1.0, 1.1, 2.0, 3.0, 4.0, 5.0...) are not stored; they are worked out from the
  order. New file problems: midterm or final repeated, more than 10 parts, a name in two
  places. The name-order rule (R2) is checked on categories. Code: `_group_positions`,
  `categories`, `is_split`, `numbers`, `labels` and the name checks in `parse_class`, all in
  `grades.py`. Spec section 15. Decision record 0006.
- **R17, on the screen:** when at least one category is split, a numbers row is shown above
  the names (`storage.aligned_row`). Parts are labelled `homework 1.0` in the per-item list,
  the "You need..." sentence (`needed_for` uses `labels`), and the Change a grade / Try a
  grade lists. Unsplit items show just their name.
- **R17, the menu:** option 6, Split a category (`ask_split` in `gradecalc.py`,
  `splittable`, `split_category`, `parse_part_weight` and `SplitProblem` in `grades.py`).
  The open-class menu is now: 1) Change a grade, 2) Change the goal, 3) Rename this class,
  4) Delete this class, 5) What if (try grades without saving), 6) Split a category,
  **7) Quit**. Decision record 0007.
- `spec.md`: new sections 14 and 15; sections 1, 5, 7 and 12 point to them. Decisions 23-37
  are round 4's.
- `docs/decisions/`: 0006 and 0007 are new. The next record is **0008**.
- `tests/`: 293 tests, all passing, none skipped (243 from rounds 1-3, 50 new). The new ones
  are in `tests/test_items.py` (R16, 14 tests) and `tests/test_split.py` (R17, 36 tests).
  Every test has a `# Checks Rn.` comment.
- README describes the per-item list and splitting.

## How to run

```
python gradecalc.py examples/example-class.txt    # first time with a file
python gradecalc.py                               # pick, rename or delete a saved class
python -m pytest                                  # run the tests
```

Windows 11, Git Bash, Python 3.13. Standard library only, plus pytest. No installs needed.

## Decisions made in round 4, and why

The student chose these when asked before any code was written:

- **Splitting is done with a menu option, and can also be written in the file by hand**,
  because R17 says "The user has to choose to do this" and R11 asks for easy editing.
- **In the file, a split category repeats its name side by side**, not a 4th line of
  numbers or numbers inside the names, so files stay 3 lines and old saved classes still
  load (record 0006).
- **Splitting asks how many parts, then each part's weight and grade.** The weights must
  add up to the category's weight, so the total stays 100. This was chosen over even
  shares (record 0007).
- **Splitting again redoes it, and 1 part joins it back into one**, with no separate join
  option (record 0007).
- **The numbers row is shown only when something is split**, so an unsplit class looks
  exactly like the R16 example.
- **A weight-0 item shows `not in this class`** in the list.
- **A split category has no combined line** in the list, only its parts (as in the R17
  example).
- **What-if tries grades on parts.** Splitting itself happens outside what-if and is saved.

These Claude chose, and they were listed for the student at the end of round 4 (spec
decisions 31-37):

- Split a category is option 6 and Quit moved to 7, so Quit stays last (like records 0002
  and 0004). 25 old tests in `tests/test_cli.py` now quit with `7`, and the wrong-choice
  test types `8`.
- An item's % is rounded like the grade (nearest whole %, .5 up). TOTAL says
  `no grades out yet` when nothing is out. Labels are padded to at least 16 characters and
  the `=` signs line up, as in the R16/R17 examples.
- Categories after attendance are numbered 5, 6, ... and can be split too.
- A name in two places that aren't side by side is a file problem.
- A part's weight typed in the menu must be above 0, and a weight-0 category can't be split.
- If the parts' weights don't add up, all of them are asked again. Weights are checked
  before any grade is asked. With 1 part, only the grade is asked. The category's old
  grade is not kept.

The student also asked for one change to the spec before the first commit: section 8
no longer says "The screen layout is not tested", because R16 and R17 are about the screen,
and the tests check the per-item list and the numbers row exactly.

## Unresolved

- **Old saved classes can read differently now.** Before round 4, a file like
  `... / project / project` meant two separate items. Now it is one category in 2 parts,
  and `project / quiz / project` is refused as a file problem (in the GPA list it shows as
  `can't be read, not counted`). Nobody has reported such a file; the student knows from
  record 0006.
- **The numbers row can be off by a space** for a name of 1 character in category 10 or
  higher (`10.0` is wider than the column). `aligned_row` still leaves at least one space,
  so nothing runs together. Not fixed, since it is very unlikely.
- **Old wording in `spec.md`, still not fixed because nobody asked:** sections 1-7 say
  "bullet N" instead of R-numbers, sections 6 and 7 cite "bullet 12" and "bullet 13"
  (probably R10 and R11), and section 8 comes after section 13 in the file. Ask the
  student before changing any of these.
- Nothing is known to be broken.

## Warnings for the next session

- **Old CLI tests quit by typing `7`** as their last answer. If the menu changes again they
  all break at once; say so in the commit message, as rounds 2, 3 and 4 did. New tests in
  `test_items.py` and `test_split.py` end with `q` instead, so they don't depend on the
  menu numbers.
- **`tests/test_items.py` and `tests/test_split.py` import `run` from `test_cli.py`**, and
  `test_split.py` imports `problems_for` from `test_parse.py`. Renaming those breaks them.
- **The screen tests compare exact spacing.** The table rows are padded to the longest row
  + 2, as since round 1. Twice in round 4 an expected line typed by hand had one space too
  many. Print the real output (see CLAUDE.md) instead of counting spaces.
- **Line endings differ by file:** `gradecalc.py`, `grades.py`, `spec.md` and most tests
  are CRLF in the working copy; `storage.py`, `test_items.py`, `test_split.py` and
  `CLAUDE.md` are LF. A multi-line search pattern written with `\n` doesn't match a CRLF
  file (this happened in round 4; see CLAUDE.md).
- **`main()` saves to the real `saved_classes/` by default.** Tests pass `folder=tmp_path`.
  For a real run, copy `gradecalc.py`, `grades.py`, `storage.py` and an example file into
  the scratchpad and run it there with `printf '...\n' | python gradecalc.py file.txt`.
- `git commit` prints "LF will be replaced by CRLF" warnings. They are harmless; ignore them.
