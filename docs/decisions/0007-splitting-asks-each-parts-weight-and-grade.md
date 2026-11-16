# 0007: Splitting asks for each part's weight and grade, and splitting again redoes it

Round 4, R17 ("The user has to choose to do this, if they dont, the normal case is the one
presented preeviously." and "The user can divided this categories up to 10 times (from
1.0 to 1.9), any more then that, will not be allowed.").

In the context of the new menu option 6, Split a category (R17), where a category such as
homework already has one weight (20) and maybe a grade (15 out of 20), and the weights of
the whole class must add up to exactly 100 (R3),
facing the questions of where the parts' weights and grades come from, and how a split is
changed or undone later,
we decided to ask how many parts (1 to 10), then each part's weight (a number above 0, and
the parts must add up to the category's weight, or all the weights are asked again), then
each part's grade or N/A, and to let the new parts replace the category, so that splitting
an already split category redoes it and choosing 1 part joins it back into one,
and neglected splitting the weight evenly with every part starting as N/A, and also
neglected splitting the weight evenly and asking only the grades, and also neglected a
separate "join" menu option that adds the parts back up,
to achieve parts that match the real course (homework worth 5 + 5 + 10, not only even
shares, and no 6.666... weights), a total that always stays 100, so a split never makes the
file break a rule, and one option that splits, changes and undoes a split,
accepting that splitting takes more typing than an even split, that the old grade of the
category is not kept (each part's grade is typed again), and that to change one part's
weight the whole category is split again; a part's grade alone can still be changed with
Change a grade.

Decided by the student in the round 4 questions, from the options above. That a part's
weight must be above 0, and that a category with weight 0 can't be split, were chosen by
Claude.
