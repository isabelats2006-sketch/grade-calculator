# Grade calculator

A command-line app that reads a class's grading weights and your grades so far, then
shows your current letter grade and GPA. It also shows the % you need on everything not
graded yet (N/A) to reach your goal. Classes are saved by name, so you can come back and
update a grade when it comes out.

Python 3.13 or newer, standard library only. Tests use pytest.

## Run it

The first time, give it a class file:

```
python gradecalc.py examples/example-class.txt
```

It asks what to call the class and what your goal is (`A-`, `3.7` or `90%`), then shows:

```
GOAL = B (3.0) // CURRENT GRADE = C+ (2.3), 79%

homework / midterm / final / attendance / project
30         30        20      10           10       = total weight
20         25        N/A     10           N/A      = 55 out of 70 = 79% = C+ (2.3)
-------------------- === --------------------
homework:       20 out of 30 = 67%
midterm:        25 out of 30 = 83%
final:          N/A
attendance:     10 out of 10 = 100%
project:        N/A
TOTAL:          55 out of 70 = 79%

You need at least 92% on final and project to get a B.
```

Under the table, each item shows its own percentage, so you can see how you are doing in
each category.

From the menu you can change a grade (it is saved), change the goal, rename the class,
delete it, try grades in what-if mode, split a category into parts, drop the lowest grade
of a split category (or keep only its highest), see the history of your changes, clear
all grades, see the grade scale, or quit.

**Splitting a category.** Any category except midterm and final can be split into 2 to
10 parts, for example the 2 homeworks given so far out of 4. It asks how many parts, each
part's weight (they must add up to the category's weight) and each part's grade. The
parts are numbered 1.0 to 1.9 for homework, 4.0 to 4.9 for attendance, and so on, and
each shows its own percentage. Each part can be changed or tried in what-if mode on its
own. Splitting again redoes it, and 1 part joins it back into one.

**Dropping the lowest grade.** If your professor drops the lowest homework (or counts
only the best one), choose that for the split category in the menu. The part not counted
shows `(dropped)`, and the category keeps its whole weight: with 8, 4 and 9 out of 10
and the 4 dropped, homework counts as 85%. Only grades already out can be dropped, and
the "You need..." % takes the drop into account. By default every part counts.

**History.** The History option lists the changes you made since you opened the
program (grades, splits, drop choices). You can go back to before any of them, which
undoes that change and every later one, and saves the class. The history is kept only
while the program is open, so it starts empty each time.

**Clear all grades.** Makes every grade of the open class N/A again, after you type Yes.
The splits and drop choices stay. If it was a mistake, go back to before it in the
history, which is the only way to get the grades back.

**The grade scale.** Pick any item of the class (each part of a split category is its
own item), the whole class, or all your saved classes together (the average of their %).
It shows the full grade scale with `<- your goal` and `<- you are here (89%)`, and how far
you are from your goal, like `You are 1% from an A- (90%).` Press Enter to go back.

**What if.** In what-if mode you can try any grade
("what if I get 18 on the final?") and see your grade and what you still need. Nothing
there is saved, and when you leave the mode your real grades are back.

After that, run it with no file to pick one of your saved classes:

```
python gradecalc.py
```

In that list you can also type `r` to rename a class or `d` to delete one. Names can use
any character except `\ / : * ? " < > |` (Windows doesn't allow those in file names).
Before deleting, it asks you to type Yes or No, so nothing is deleted by accident.

With 2 or more saved classes, the list starts with your GPA across all of them: each
class's current GPA and their plain average. Classes with no grades out yet are not counted.

## Run the tests

```
python -m pytest
```

(Install pytest first if you don't have it: `python -m pip install pytest`.)

## The class file

Three lines: names, weights, grades (plus any drop lines, below). See
`examples/example-class.txt`.

- The names start with `homework` (or `hw` or `assignments`), `midterm`, `final`,
  `attendance`, in that order. Others can follow. Capitals don't matter.
- The weights add up to exactly 100. Use 0 for something the class doesn't have.
- The grades are points out of each weight, or `N/A` if not out yet.
- A split category is its name repeated side by side, one per part, like
  `homework / homework / midterm / ...`, each with its own weight and grade.
- After the three lines, a split category can have a line `homework: drop lowest` or
  `homework: keep highest`. The menu writes it for you.
- Anything after `=` on a line is a note and is ignored.

If the file breaks a rule, the program lists every problem with its line number.

Saved classes go in `saved_classes/`, which is never put on GitHub. The full rules are
in `spec.md`.
