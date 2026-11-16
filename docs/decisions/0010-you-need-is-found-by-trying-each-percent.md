# 0010: The "You need..." % is found by trying each whole % from 0 to 100

Round 5, R19 (dropping the lowest grade or keeping only the highest) together with R6
("the program should say what I need on the N/A ones to reach my goal ... If there is
more than one N/A, it says the same % needed on all of them").

In the context of the "You need at least X% on ..." sentence, which until round 5 used
one formula, (goal % - 0.5 - points earned) / (weight of the N/A items) x 100 rounded up,
facing the problem that with a drop, which part is dropped depends on the grades the N/A
items get (a homework still N/A may be the one dropped if it is low, or push another one
out if it is high), so the formula is wrong for those classes,
we decided to give every N/A item the same whole %, from 0 up to 100, work out the final
grade with the drops for each, and report the first % that reaches the goal, for every
class, with or without drops,
and neglected keeping the formula for classes without drops and adding a special case
for each kind of drop, and also neglected solving it exactly with a formula for each
possible dropped part and picking the right one,
to achieve one way of working out what is needed that is right for every class, can't
miss a case, and reuses the same grade math as the screen, so the % shown and the grade
it leads to always agree; without drops it gives exactly the formula's answer, so all
earlier tests pass unchanged,
accepting that the grade is worked out up to 101 times instead of once (instant for a
class file of a few lines), and that the answer is always a whole %, as it already was.

Chosen by Claude; the student chose that the "You need..." % takes the drop into account.
