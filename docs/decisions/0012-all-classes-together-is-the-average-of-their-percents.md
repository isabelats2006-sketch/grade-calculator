# 0012: All classes together on the grade scale is the average of each class's rounded %

Round 6, R21 ("The last two options in the menu are to see the grade in one class and the
grades of all classes put together.") together with R14 ("If the user has more then one
class, then it can see all the GPA across all class together").

In the context of the "All your classes together" choice of the grade scale menu, which
has to put one "you are here" mark on a scale written in % (94 to 100% = A, ...),
facing the problem that the GPA across classes of R14 (like 3.57) is not on the scale, since
the scale's GPAs are only 4.0, 3.7, 3.3, ..., so the existing number can't be marked on it,
we decided to take each saved class's current %, rounded as it is shown everywhere else
(79% for CSC 299), average those with each class counting the same, round to the nearest
whole % with .5 going up, and mark that, listing every class under it, with the ones that
have no grades yet or can't be read listed but not counted, as in the GPA across classes,
and neglected marking the GPA across classes on the line with the closest GPA below it,
and also neglected one mark per class on the same scale, and also neglected averaging the
classes' exact %s before any rounding, and also neglected adding up all classes' points as
if they were one big class,
to achieve a mark that is a % like every other scale's, worked out from the same numbers
the student sees for each class, so it can be checked by hand (79% and 96% give 88%), and
where every class counts the same, as in the GPA across classes (record 0003),
accepting that rounding each class first can differ by 1% from averaging the exact %s, that
it can differ from the GPA across classes' letter (the average of the GPAs is not the GPA
of the average %), and that it is shown even with only 1 saved class, where it is just that
class's %.

The student chose that it is the average of the classes' %, placed on the scale, and that it
uses the open class's goal. Using each class's rounded % (not the exact one), how classes
with no grades are treated and showing it with 1 class were chosen by Claude.
