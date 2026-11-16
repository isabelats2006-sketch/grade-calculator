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

You need at least 92% on final and project to get a B.
```

From the menu you can change a grade (it is saved), change the goal, rename the class,
delete it, try grades in what-if mode, or quit. In what-if mode you can try any grade
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

Three lines: names, weights, grades. See `examples/example-class.txt`.

- The names start with `homework` (or `hw` or `assignments`), `midterm`, `final`,
  `attendance`, in that order. Others can follow. Capitals don't matter.
- The weights add up to exactly 100. Use 0 for something the class doesn't have.
- The grades are points out of each weight, or `N/A` if not out yet.
- Anything after `=` on a line is a note and is ignored.

If the file breaks a rule, the program lists every problem with its line number.

Saved classes go in `saved_classes/`, which is never put on GitHub. The full rules are
in `spec.md`.
