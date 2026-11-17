# Handoff after round 6 (clearing all grades, the grade scale)

For the fresh session that does the next round. Read `problem.md`, `spec.md`, `CLAUDE.md`
and `docs/decisions/` first; this file adds what they don't say. The handoffs for rounds 1
to 5 are still accurate for everything round 6 didn't touch.

## Current state

Rounds 1 to 6 (R1-R21 in `problem.md`) are built, committed and pushed. The last round 6
commit is `5bc6a88`; the working tree was clean after it (apart from this file and the
CLAUDE.md edit, which the student reads before committing).

- **R20, Clear all grades:** menu option 9. If no item with weight above 0 has a grade, it
  says `All the grades are already N/A, so there is nothing to clear.` and asks nothing.
  Otherwise it asks Yes/No (`_ask_yes_no`, shared with delete and going back). Yes sets every
  grade to N/A (`cleared` in `grades.py`: names, weights, splits and `rule` stay), saves,
  and adds `Cleared all grades` to the history (`remember` in `run_menu`). Going back to
  before it brings the grades back. Code: `has_grades`, `cleared` (`grades.py`),
  `ask_clear` (`gradecalc.py`). Spec section 18.
- **R21, the scale itself:** pure functions in `grades.py`: `scale_lines(here, goal)`
  (the title and 11 lines, with marks 3 spaces after the line), `distance_text(here,
  goal)`, `average_percent(percents)`, all built from `SCALE`. `here` is always a
  **rounded** whole % or None. `Goal` now has a 4th field, `letter` ("A-", or None for a
  goal typed as a %), set by `_letter_goal`; it defaults to None, so older code that builds
  a Goal still works.
- **R21, the menu:** option 10, `see_grade_scale` in `gradecalc.py`. It lists items with
  weight above 0 (labels from `labels()`, so parts are `homework 1.0`, ...), then
  `The whole class (<name>)`, then `All your classes together`. Enter goes back (record
  0011), and after each scale the menu is shown again. Helpers: `_item_on_scale`,
  `_class_on_scale` and `_all_classes_on_scale`. The last one reads every saved class
  from `folder` with `load_class`, as `gpa_across_classes` does. Nothing is saved.
- **All classes together** = the plain average of each class's `grade.rounded`, rounded .5
  up; classes with no grades or that can't be read are listed but not counted; shown even
  with 1 class (record 0012). It uses the open class's goal.
- **The open-class menu is now:** 1) Change a grade, 2) Change the goal, 3) Rename,
  4) Delete, 5) What if, 6) Split a category, 7) Drop the lowest or keep the highest grade,
  8) History, 9) Clear all grades, 10) See the grade scale, **11) Quit**.
  `Choose 1 to 11: `; a wrong choice says `Please type 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 or 11.`
- `spec.md`: new sections 18 and 19 (they come after 17, and before section 8, which is
  still near the end); section 7's menu and section 16's history list were updated.
  Decisions 56-71 are round 6's (56-61 the student's, 62-71 Claude's).
- `docs/decisions/`: 0011 and 0012 are new. The next record is **0013**.
- `tests/`: **424 tests**, all passing, none skipped (353 from rounds 1-5, 71 new):
  `tests/test_clear.py` (R20, 14) and `tests/test_scale.py` (R21, 57: 40 for the scale
  logic, 17 for the menu). Every test has a `# Checks Rn.` comment.
- README describes clearing all grades and the grade scale.

## How to run

```
python gradecalc.py examples/example-class.txt    # first time with a file
python gradecalc.py                               # pick, rename or delete a saved class
python -m pytest                                  # run the tests
```

Windows 11, Git Bash, Python 3.13. Standard library only, plus pytest. No installs needed.

## Decisions made in round 6, and why

The student chose these when asked before any code was written:

- **Clearing asks Yes or No first**, and only grades become N/A: splits *and* drop/keep
  choices stay (R20 says only "Splits also stay").
- **The last line of a scale compares with the goal** ("You are 1% from an A- (90%)." /
  "You reached your goal of A- (90%)."), not with the next letter up, and the goal mark is
  the open class's goal on every scale.
- **Each part of a split category is its own entry** in the grade scale menu, not the whole
  category.
- **All classes together is the average of the classes' %**, marked on the scale, not the
  GPA across classes (which isn't on a % scale).
- **The all-classes scale uses the open class's goal** too.
- **The grade scale is option 10, Clear all grades 9, Quit 11**; N/A items are listed and
  show the scale with only the goal mark and
  `No grade is out yet, so you are not on the scale yet.`

These Claude chose, and they were listed for the student at the end of round 6 (spec
decisions 62-71, plus a few from building it):

- Nothing to clear means no question and no history entry.
- Weight-0 items are not in the grade scale menu.
- Leaving with Enter, so the last two options are the ones R21 names (record 0011).
- The menu is shown again after each scale.
- Mark wording: `<- your goal, you are here (91%)` on one line; `<- your goal (91%)` for a %
  goal.
- The distance uses rounded %s.
- The average uses each class's rounded %, with the same not-counted rules as the GPA
  across classes (record 0012).
- A dropped part keeps its own % and shows `(dropped)` in its first line.
- Neither new option is in what-if mode.
- `Goal.letter`, the two new test files, two decision records, and the wording of every
  new message.

## Unresolved

- **Bug: with drop lowest, a higher grade can lower the class grade.** This is a real bug,
  not just an assumption. Example: homework split into weights 9 / 1 / 9 with
  `homework: drop lowest`, grades 4.5 / 0.55 / 9 (the rest N/A). The 4.5 (50%) is dropped,
  the kept parts are 9.55 out of 10, and the class is 95.5% = 96% (A). Raising the first
  part to 5.04 (56%) makes the 0.55 (55%) the lowest instead. The kept parts are then 14.04
  out of 18, and the class is 78% (C+). (Checked with `parse_class` and `current_grade` in
  round 6.) The cause is in `current_grade` (`grades.py`): the parts out count as the kept
  parts' %, so which part is dropped changes how much weight the kept parts stand for
  (record 0009). Because of this, **the "You need..." % can be wrong in such classes**.
  `needed_for` gives every N/A item the same whole %, from 0 up, and reports the first one
  that reaches the goal (record 0010), which is only right if the grade never goes down
  when that % goes up. Here it can, so "You need at least X%" can be false for some %s
  above X, "You already have ... even if you get 0" can be wrong, and "not reachable" can
  be said when a lower % would reach the goal. Not fixed; the student asked only to record
  it. Ask the student before changing the counting or the "You need..." search.
- **A dropped part's scale compares its own % with the class goal**, even though that part
  doesn't count. That's what "its own %" means, but a student could read
  "You are 50% from an A-" on a dropped homework as a problem.
- **The all-classes % and the GPA across classes can disagree** (the average of GPAs is not
  the GPA of the average %). Record 0012 accepts this; nobody has asked about it yet.
- **The all-classes average reads the saved files**, not the items in memory. The open
  class is saved after every change, so they agree, unless a save failed. Saving errors
  aren't caught in `run_menu` (as before round 6).
- **Clearing a weight-0 item:** `cleared` sets its grade to N/A too (0 becomes N/A), but
  `has_grades` ignores weight-0 items, so a class whose only grade is a 0 on a weight-0 item
  counts as "nothing to clear". Both show `not in this class`, so nothing visible changes.
- **The spec section 19 "all classes together" example (95% / 85%) is not one real run.**
  Its layout matches the program's output (a test with 79% / 96% checks the real format),
  but the numbers are made up. The section 19 menu and whole-class examples were checked
  against a real run and match line for line.
- **problem.md's R21 example has trailing spaces after `B  = 3.0 = 83 to 86%`**; the program
  prints none. The test copies the program's output, not the trailing spaces.
- Still from rounds 4-5: the numbers row can be off by a space for a 1-character name in
  category 10+; `spec.md` sections 1-7 still say "bullet N", sections 6 and 7 cite
  "bullet 12"/"bullet 13", and section 8 comes after section 19 in the file; there is no
  test for weight-0 parts inside a drop/keep category. Ask the student before changing these.

## Warnings for the next session

- **Old CLI tests in `tests/test_cli.py` now quit by typing `11`** (24 answer lists end
  with `"11"`, the wrong-choice test types `"12"`, and two tests expect `Choose 1 to 11: `,
  one in `test_cli.py` and one in `test_split.py`, plus the menu-list test). They were moved
  twice this round (9 -> 10 -> 11), each time with a script that replaced exact texts and
  stopped if a count was wrong. Watch out: after the first move, `"10"` meant Quit, and the
  next move had to change the wrong-choice answer first (`"11", "10"]` -> `"12", "11"]`)
  before the plain `"10"]` endings. Do the most specific replacement first.
- **Option numbers inside the grade scale menu depend on the class.** With
  `SPEC_EXAMPLE` (5 items) the whole class is 6 and all classes 7; with the section 17
  class (homework in 3 parts, 6 items) they are 7 and 8. One round 6 check used the wrong
  number. Print the menu before writing answer numbers.
- **Test files import from each other:** `test_clear.py` and `test_scale.py` import `run`
  and `SPEC_EXAMPLE` from `test_cli.py` (as `test_drop.py` and `test_history.py` do).
- **`gpa_across_classes` and `_all_classes_on_scale` loop over the saved classes in the
  same way** but are separate functions. A change to how unreadable classes are handled
  must go in both.
- **A break script must restore in `finally`** (now in CLAUDE.md). In round 6 the script
  crashed on a pytest option that isn't installed and left `gradecalc.py` broken; it was
  restored from the copy taken before the break and checked with `cmp`.
- **Line endings:** CRLF: `gradecalc.py`, `grades.py`, `spec.md`, `problem.md`,
  `tests/test_cli.py`, `test_goal.py`, `test_grade.py`, `test_parse.py`,
  `test_show_number.py`, `test_storage.py`. LF: `storage.py`, `tests/test_items.py`,
  `test_split.py`, `test_drop.py`, `test_history.py`, `test_clear.py`, `test_scale.py`,
  `README.md`, `CLAUDE.md`, the decision records and handoffs. The Edit tool kept CRLF
  files CRLF in round 6 (checked by counting).
- **The scratchpad scripts are gone** with the scratchpad. Round 6 used two: one that
  applies a list of exact replacements from a JSON file (`[file, old, new, expected
  count]`, stopping with nothing written if a count is wrong) and one that does breaks from a
  JSON file (`[file, old, broken]`), each one replaced exactly once, then runs pytest,
  restores the file and compares sha256. JSON makes `\r\n` in a break easy to write, which
  a CRLF file needs for any break that spans two lines.
- **`main()` saves to the real `saved_classes/` by default.** Tests pass `folder=tmp_path`.
  For a real run, copy `gradecalc.py`, `grades.py`, `storage.py` and a class file into the
  scratchpad and run it there with `printf '...\n' | python gradecalc.py file.txt`.
- `git commit` prints "LF will be replaced by CRLF" warnings. They are harmless; ignore them.
