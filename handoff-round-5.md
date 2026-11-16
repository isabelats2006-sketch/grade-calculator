# Handoff after round 5 (history of the session, dropping the lowest grade)

For the fresh session that does the next round. Read `problem.md`, `spec.md`, `CLAUDE.md`
and `docs/decisions/` first; this file adds what they don't say. The handoffs for rounds 1
to 4 are still accurate for everything round 5 didn't touch.

## Current state

Rounds 1 to 5 (R1-R19 in `problem.md`) are built, committed and pushed. The last round 5
commit is `f44ff2c`; the working tree was clean after it (apart from this file and the
CLAUDE.md edits, which the student reads before committing).

- **R19, the counting:** a category split into 2 or more parts can count all parts (the
  standard, no line in the file), `drop lowest` or `keep highest`. Only parts that are out
  (grade, weight > 0) can be dropped, and only when 2 or more are out. Lowest/highest is by
  each part's own %, a tie picks the first part. The category keeps its whole weight: the
  parts out count as the kept parts' % (8, 4, 9 out of 10, 4 dropped: 85% of 30 = 25.5 out
  of 30). Code: `Item.rule`, `DROP_LOWEST`, `KEEP_HIGHEST`, `dropped`, `current_grade`,
  `with_rule` in `grades.py`. Spec section 17, records 0009 and 0010.
- **R19, the file:** after the three lines, optional lines `<name>: drop lowest` /
  `<name>: keep highest` (capitals and spaces ignored). Read by `_read_rules` in
  `parse_class`; written by `class_to_text` in `storage.py`. A file with fewer than 3 lines
  gets the old message; any other extra line is a file problem (4 new messages, spec
  section 17).
- **R19, the screen:** a dropped part has `   (dropped)` after its %, and a line under TOTAL
  says `homework drops its lowest grade.` / `keeps only its highest grade.` (`item_lines`
  and `RULE_TEXT` in `gradecalc.py`). Works in what-if too.
- **R19, the menu:** option 7, Drop the lowest or keep the highest grade (`ask_rule`,
  `RULE_CHOICE`, `RULE_MENU`). Lists only split categories.
- **"You need..."**: `needed_for` now tries each whole % from 0 to 100 on every N/A item and
  reports the first that reaches the goal (record 0010). Without drops it gives exactly
  the old formula's answer; every earlier test passed unchanged.
- **`show_number`**: a number that doesn't end in decimals (35/3) is shown with 2
  decimals, .5 up. Numbers that end are shown exactly, as before.
- **R18, history:** option 8 (`ask_history`, `grade_change_text`, `HISTORY_MENU`). The
  history is a local list in `run_menu`: `(text, items before the change)`, oldest first.
  It records Change a grade, Split a category and option 7, never what-if, goal, rename or
  delete, and not a change that changes nothing. Going back to before change N asks Yes/No
  (`_ask_yes_no`, shared with delete), restores that copy, deletes entries N and later,
  saves. Record 0008. Spec section 16.
- **The open-class menu is now:** 1) Change a grade, 2) Change the goal, 3) Rename,
  4) Delete, 5) What if, 6) Split a category, 7) Drop the lowest or keep the highest grade,
  8) History, **9) Quit**.
- `ask_split` and `ask_rule` now return `(new items, history line)`, or None.
- `spec.md`: new sections 16 and 17; sections 1, 3, 4, 7, 8 and 15 point to them.
  Decisions 38-55 are round 5's. The section 17 screen example was checked against the
  real output and matches line for line (it is also a test).
- `docs/decisions/`: 0008, 0009, 0010 are new. The next record is **0011**.
- `tests/`: **353 tests**, all passing, none skipped (293 from rounds 1-4, 60 new):
  `tests/test_drop.py` (R19, 44) and `tests/test_history.py` (R18, 16). Every test has a
  `# Checks Rn.` comment.
- README describes dropping a grade, the history and the drop line in the file.

## How to run

```
python gradecalc.py examples/example-class.txt    # first time with a file
python gradecalc.py                               # pick, rename or delete a saved class
python -m pytest                                  # run the tests
```

Windows 11, Git Bash, Python 3.13. Standard library only, plus pytest. No installs needed.

## Decisions made in round 5, and why

The student chose these when asked before any code was written:

- **The history lists grade changes, splits and drop/keep choices**, the changes that are
  saved to the class; not what-if tries, the goal, renames or deletes.
- **Going back to a change undoes it and every later one** (like undoing several times),
  and those leave the history, so the class can never end up in a state it was never in.
- **History is opened from the open-class menu** only, not the saved-class list.
- **Drop the 1 lowest or keep the 1 highest**, not N, since R19 says "the lowest grade"
  and "the highest grade".
- **The category keeps its whole weight**, so the total stays 100 (R3) and every earlier
  rule still holds.
- **Lowest/highest by %**, not points.
- **Only grades already out can be dropped** (and only with 2 or more out); the
  "You need..." % takes the drop into account.
- **A menu option sets the choice, stored as a line after the three lines**, so old
  3-line files still load and the file can be edited by hand (R11).

These Claude chose, and they were listed for the student at the end of round 5 (spec
decisions 46-55, plus a few from building it):

- Drop/keep is option 7, History 8, Quit moved to 9 so it stays last.
- Going back asks Yes or No first, since there is no redo.
- A change that changes nothing is not added to the history.
- The history belongs to the open class: renaming keeps it, and it starts empty after the
  class is deleted and another one picked.
- Going back keeps a copy of the whole class from before each change, not an "opposite
  change" per change (record 0008).
- Only split categories can drop/keep; a drop line for a 1-part category is a file problem.
- On a tie, the first part is dropped or kept.
- Splitting again into 2+ parts keeps the choice; joining into 1 part removes it.
- A line under TOTAL names each category's choice, so it shows before anything is dropped.
- Points that don't end are shown with 2 decimals.
- `(dropped)` has 3 spaces before it, copied from the R19 example.
- "You need..." is found by trying each whole % for every class (record 0010).
- The wording of the new messages and the 4 new file problems.

The student also asked for one change to the commit messages before the last commits:
decision-record commits must also have a body saying why (now a rule in CLAUDE.md).

## Unresolved

- **"You need..." with drops assumes the grade never goes down when the N/A items get a
  higher %.** It reports the *first* whole % that reaches the goal. With "lowest by %" this
  holds in every case worked out by hand and in the tests, but it was not proved for every
  possible class. If a student ever reports a "You need..." % that seems too high or too
  low with a drop, check this first.
- **Weight-0 parts inside a drop/keep category** are left out of dropping (they are never
  "out"), but no test checks this case. Splitting from the menu can't make one (part
  weights must be above 0); only a hand-edited file can.
- **`Item.rule` is stored on every part of a category**, but the code reads it from the
  first part (`items[group[0]].rule`). `parse_class`, `with_rule` and `split_category` keep
  all parts the same. Code that builds Items by hand with different rules on the parts of
  one category would be read by the first part only.
- **A delete can't be gone back on**, and neither can a rename or a goal change (the
  student's choice). Going back has no redo.
- **What-if can't change the drop/keep choice**, only grades (like splitting, it is done
  outside what-if and saved). Nobody asked for it.
- **The spec section 16 example** (`Changed homework from 15 to 18`, ...) is written to the
  same format the tests check, but it is not a copy of one real run.
- Still from round 4: the numbers row can be off by a space for a 1-character name in
  category 10+; `spec.md` sections 1-7 still say "bullet N", sections 6 and 7 cite
  "bullet 12"/"bullet 13", and section 8 comes after section 15 in the file. Ask the
  student before changing these.
- Nothing is known to be broken.

## Warnings for the next session

- **Old CLI tests in `tests/test_cli.py` quit by typing `9`** (24 answer lists end with
  `"9"`, the wrong-choice test types `"10"`, and two menu tests expect `Choose 1 to 9: `,
  one in `test_cli.py` and one in `test_split.py`). This round they were moved twice
  (7 -> 8 -> 9), once per menu option added, with a small script that replaced only those
  exact texts and stopped if a count was wrong. Newer tests (`test_items.py`,
  `test_split.py`, `test_drop.py`, `test_history.py`) end with `q` instead.
- **Test files import from each other:** `test_drop.py` and `test_history.py` import `run`
  and `SPEC_EXAMPLE` from `test_cli.py`; `test_drop.py` imports `problems_for` from
  `test_parse.py`. Renaming those breaks them.
- **Item numbers shift after a split.** In a test that splits homework into 2 parts and
  then uses Change a grade, attendance is item 5, not 4. One round 5 test got this wrong
  (it picked final, already N/A, and the change was rightly not recorded). Print the real
  item list before writing the answer numbers.
- **The `=` signs in the per-item list line up with the widest "out of"**, which is often
  TOTAL's (`35.5 out of 40`), so other lines get extra spaces. One expected line in round 5
  had too few. Copy expected lines from printed output (see CLAUDE.md).
- **`show_number` rounds a number that doesn't end.** That's fine for the screen, but it
  means `show_number` must never be used to *save* a worked-out number (like a category's
  25.5 after a drop). Saving only writes numbers the user typed, which always end.
- **Line endings in the working copy:** CRLF: `gradecalc.py`, `grades.py`, `spec.md`,
  `problem.md`, `tests/test_cli.py`, `test_goal.py`, `test_grade.py`, `test_parse.py`,
  `test_show_number.py`, `test_storage.py`. LF: `storage.py`, `tests/test_items.py`,
  `test_split.py`, `test_drop.py`, `test_history.py`, `README.md`, `CLAUDE.md`, the
  decision records and handoffs. The Edit tool kept CRLF files CRLF in round 5 (checked
  by counting `\r\n` against `\n` after every edit).
- **The scratchpad scripts are gone** with the scratchpad. The break checks used a script
  that, for each break, copied the file, replaced one exact text (stopping unless it was
  found exactly once), ran pytest, restored the copy and compared sha256. Its breaks
  file had one break per line, separated by `|||`, so a break can't contain a line ending.
  Python's `splitlines()` also splits on a lone `\r`, so writing `\r` into the breaks
  file broke it. Match a line's text without its ending.
- **`main()` saves to the real `saved_classes/` by default.** Tests pass `folder=tmp_path`.
  For a real run, copy `gradecalc.py`, `grades.py`, `storage.py` and a class file into the
  scratchpad and run it there with `printf '...\n' | python gradecalc.py file.txt`.
- `git commit` prints "LF will be replaced by CRLF" warnings. They are harmless; ignore them.
