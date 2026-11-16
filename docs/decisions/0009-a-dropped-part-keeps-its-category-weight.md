# 0009: A dropped part's weight is covered by the kept parts, and the choice is a line in the file

Round 5, R19 ("they choose to drop the lowest grade or get only the highest grade out of
all of them. All of these options are allowed now, but the user has to specify that they
want it. The standard version is that all the categories are taken into consideration for
the grade.").

In the context of a category split into parts (R17), such as homework 8, 4 and 9 out of
10 each, weight 30, where the weights of the whole class must add up to exactly 100 (R3),
facing the questions of what happens to a dropped part's weight, which part is "the
lowest", what to do with parts that are still N/A, and how the choice is kept for next
time,
we decided that the category keeps its whole weight and the parts that are out count as
the kept parts' % (homework is 17 out of 20 = 85% of 30, so 25.5 out of 30), that the
lowest and highest are by each part's own %, that only parts with a grade can be dropped
and only when at least 2 are out, and that the choice is made with a new menu option and
stored as an optional line after the three lines, like `homework: drop lowest`,
and neglected removing the dropped part's weight from the class (17 out of 20, with the
class then out of 90), and also neglected choosing by points instead of %, and also
neglected waiting until every part is out before dropping, and also neglected marking the
choice on the name in line 1 (`homework (drop lowest) / homework / ...`), and also
neglected asking it at the end of Split a category,
to achieve the way professors usually drop a grade, a total that stays 100 so every
earlier rule and the "You need..." math still hold, a drop that is visible as soon as two
grades are out, and old 3-line class files and saved classes that load exactly as before,
accepting that the points shown can have decimals (25.5, or 11.67 for a total that
doesn't end), that TOTAL no longer equals the sum of the parts' lines (the dropped one is
marked `(dropped)` and a line under TOTAL says how the category counts), and that a file
can now have more than 3 lines, so a stray 4th line is reported as a line that isn't
understood.

Decided by the student in the round 5 questions, from the options above. Dropping only 1
(not N) was also the student's choice. That a tie picks the first part, and that the
choice stays when splitting again into 2 or more parts, were chosen by Claude.
