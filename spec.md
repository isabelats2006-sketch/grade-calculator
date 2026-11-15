# Grade calculator: spec

What the program does, exactly. The requirements are in `problem.md`; this file turns them
into behaviour that can be built and tested. "Bullet N" means the Nth bullet under
*Initial requirements* in `problem.md`.

## How to run

```
python gradecalc.py csc299.txt     # open a class file (first time)
python gradecalc.py                # pick one of your saved classes
```

## 1. The class file (bullets 1-5)

A plain text file with three lines, laid out like the example in `problem.md`:

```
homework / midterm / final / attendance / project
30         30        20      10           10
20         25        N/A     10           N/A
```

- **Line 1, names**, separated by `/`. Capitals don't matter.
  - The first four must be, in this order: `homework` (or `hw` or `assignments`), `midterm`,
    `final`, `attendance`.
  - Any number of other names may follow (`project`, `quizzes`, ...).
- **Line 2, weights**: one number per name, separated by spaces. Each is 0 or more, and
  together they must add up to exactly 100.
- **Line 3, grades**: one per name, separated by spaces. Each is points earned out of that
  item's weight (20 under 30 means 20 out of 30), or `N/A` if it is not out yet.
  - A grade can't be below 0 or above its weight.
- An item with weight 0 doesn't exist in this class. Its grade must be 0 or N/A, and it is
  left out of every calculation.
- Anything after `=` on a line is ignored, so notes like `= total weight` are allowed.
  Blank lines are ignored.

## 2. Checking the file (bullets 2, 8, 9)

The program is strict about the file but never crashes. If the file is wrong it lists
**every** problem it found, each with its line number and what to fix. For example:

```
There are problems with csc299.txt:
  - Line 1: name 2 should be "midterm", but it is "midtrem".
  - Line 2: the weights add up to 90, but they must add up to exactly 100.
Please fix the file or use a different one.
```

Then it asks for another file path, or `q` to quit. A file that doesn't exist or can't be
read gets the same treatment.

## 3. The current grade (bullets 3-4, 10)

- **Counted** items have a weight above 0 and a grade (not N/A).
- **Current grade** = points earned on counted items ÷ their weights × 100.
  This is the "40 out of 50" in `problem.md`: 40 ÷ 50 = 80%.
- The % is rounded to the nearest whole number, with .5 rounding up (93.5 → 94, 89.4 → 89).
  Then it is looked up in the scale:

| Letter | GPA | Rounded % |
|---|---|---|
| A | 4.0 | 94-100 |
| A- | 3.7 | 90-93 |
| B+ | 3.3 | 87-89 |
| B | 3.0 | 83-86 |
| B- | 2.7 | 80-82 |
| C+ | 2.3 | 77-79 |
| C | 2.0 | 73-76 |
| C- | 1.7 | 70-72 |
| D+ | 1.3 | 67-69 |
| D | 1.0 | 60-66 |
| F | 0.0 | 0-59 |

- If nothing is counted yet (all N/A), it says "No grades are out yet" instead of a grade.

## 4. The goal (bullet 6)

After the file is loaded, the program asks `What is your goal?`. You can type:

- **a letter**: `A-`, `b+` (capitals don't matter)
- **a GPA**: `3.7`. It must be one of the GPAs in the scale.
- **a percent**: `90%`, or a number above 4 such as `90`

If the answer can't be understood, it explains why and asks again. The goal is not stored
in the file.

**What you need to reach it.** The goal's lowest % is the bottom of its range (A- is 90).
Because of rounding, a final grade of 89.5% already counts as 90%.

- Let *needed* be the % to score on **every** N/A item (the same % on all of them) so that
  the final grade, out of 100, reaches the goal.
- needed = (goal % − 0.5 − points earned so far) ÷ (total weight of N/A items) × 100,
  rounded **up** to a whole %.
- How it is reported:
  - between 0 and 100: "You need at least 85% on final and project to get an A-."
  - 0 or less: "You already have an A- even if you get 0 on the rest."
  - above 100: "An A- is not reachable anymore, even with 100% on the rest. The best you can
    get is B+ (88%)."
  - no N/A items left: "Your final grade is B+. You reached / did not reach your goal of A-."

## 5. What the screen shows

```
CSC 299
GOAL = B (3.0) // CURRENT GRADE = C+ (2.3), 79%

homework / midterm / final / attendance / project
30         30        20      10           10       = total weight
20         25        N/A     10           N/A      = 55 out of 70 = 79% = C+ (2.3)

You need at least 92% on final and project to get a B.
```

## 6. Saving classes by name (bullet 12)

- The first time you open a file, the program asks `What should this class be called?`,
  suggesting the file's name. It saves a copy in the `saved_classes/` folder as
  `<name>.txt`, using the same layout as the class file.
  - A name can't contain `\ / : * ? " < > |`, since Windows doesn't allow them in file names.
  - If the name is already used, it asks before replacing it.
- `python gradecalc.py` with no file lists the saved classes, numbered, and you pick one.
  If there are none, it tells you how to start with a file.
- `saved_classes/` is not put on GitHub (it is in `.gitignore`), because it holds your
  real grades.

## 7. Changing things (bullet 13)

After the result, a menu:

```
1) Change a grade
2) Change the goal
3) Rename this class
4) Delete this class
5) Quit
```

- **Change a grade**: pick the item by number, then type the new grade (a number or
  `N/A`). It is checked by the same rules as the file. The saved class is updated and the
  result is shown again.
- **Change the goal**: asks the goal question again.
- **Rename this class** and **Delete this class**: see sections 9 and 10.
- Weights and names are changed by editing the saved file in `saved_classes/` by hand.
- `q` at any question still quits.

## 9. Renaming a class (R13)

A saved class can be renamed from two places: the menu of an open class (option 3), and
the saved-class list (type `r`, then the class's number).

- It asks `New name for "CSC 299" (press Enter to keep it): `. Enter keeps the old name.
- The new name follows the same rules as a new class name (section 6): any characters are
  allowed except `\ / : * ? " < > |`, which Windows doesn't allow in file names. So
  `CSC 299 (Fall) & Lab #2`, `Français 101` and `MATH-101!` are fine. A name can't be
  empty, end with a dot, or be a name Windows reserves (`CON`, `LPT1`, ...).
- If another saved class already has that name (capitals ignored), it says so and asks
  again, so renaming never replaces another class. Changing only the capitals of the same
  class (`csc 299` to `CSC 299`) is allowed.
- A refused name is explained and the question is asked again.
- The saved file is renamed (`saved_classes/<new name>.txt`) and its grades are unchanged.
  It says `Renamed "CSC 299" to "CSC 299 (Fall)".`, and the screen shows the new name.

## 10. Deleting a class (R12)

A saved class can be deleted from two places: the menu of an open class (option 4), and
the saved-class list (type `d`, then the class's number).

- It always asks first:
  `Are you sure you want to delete "CSC 299"? It will be lost. Type its name to delete it, or press Enter to keep it: `
- Only typing the class's name exactly (spaces around it are ignored, capitals are not)
  deletes it. Anything else keeps it and says `Kept "CSC 299".`
- When deleted, it says `Deleted "CSC 299".` and the file in `saved_classes/` is removed.
- From the menu of an open class, the program then goes back to the saved-class list. If
  no classes are left, it says so (as in section 6) and ends.

## 11. The saved-class list, with rename and delete (R10, R12, R13)

```
Your saved classes:
  1) CSC 299
  2) MATH 101
Pick a class by number, r to rename, d to delete, or q to quit:
```

- A number opens that class, as before.
- `r` or `d` asks `Which class? (number): `, then renames or deletes it as in sections 9
  and 10, then shows the list again.
- Anything else says `Please type a number from 1 to 2.` (with `r`, `d` and `q` in the
  question) and asks again.

## 8. Tests

`python -m pytest`. Tests cover the logic: reading and checking the file, the grade and
rounding, the goal input, the "needed" math, and saving/loading, renaming and deleting. The screen layout is
not tested.

## Decisions I made that problem.md doesn't say (please check)

1. An item with weight 0 must have grade 0 or N/A.
2. A grade above its weight is an error.
3. 89.5% counts as reaching 90%, because of the nearest-% rounding. The *needed* % is rounded
   up, so following it really reaches the goal.
4. A goal number of 4 or below is a GPA; above 4 it is a percent.
5. When the goal can't be reached, it also shows the best grade still possible.
6. Saved classes live in `saved_classes/`, one file per class, and are kept off GitHub.
7. Weights and names are edited by hand, not through the menu.

### Round 2 (R12, R13)

8. Rename and delete are in both the open-class menu and the saved-class list.
9. "Special characters within reason" means every character Windows allows in a file name.
10. Deleting needs the class's name typed exactly; anything else keeps it.
11. Renaming to a name another class already has is refused, never a replacement.
12. Quit moves from 3 to 5 in the menu so it stays last; `q` still quits anywhere.
13. Pressing Enter at the rename question keeps the old name.
14. After deleting the open class, the program goes back to the saved-class list.
