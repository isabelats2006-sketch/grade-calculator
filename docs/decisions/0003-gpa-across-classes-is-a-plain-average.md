# 0003: The GPA across classes is a plain average of each class's GPA

Round 3, R14 ("If the user has more then one class, then it can see all the GPA across all
class together").

In the context of showing one GPA across all saved classes (R14), where a class file has
only names, weights and grades, and no credit hours,
facing the question of how to combine several classes into one number,
we decided to take the plain average of each class's current GPA (from the R9 scale), with
2 decimals and .5 going up, leaving out classes with no grades out yet, and to show it
automatically above the saved-class list whenever there are 2 or more classes,
and neglected a credit-weighted GPA (which would need a credits question for every class
and a new line in the saved files), and also neglected averaging the classes' percentages
and turning that into one letter,
to achieve a number that works with the saved files as they are (they keep the round 1
three-line layout and stay easy to edit by hand, R11), that matches the GPA each class
already shows, and that needs no extra typing,
accepting that a 1-credit lab counts as much as a 4-credit class, so the number can differ
from the official GPA, and that a class's GPA is its grade so far, which can still change.

Decided by the student in the round 3 questions, from the options above.
