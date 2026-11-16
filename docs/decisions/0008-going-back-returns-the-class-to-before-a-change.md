# 0008: Going back returns the class to how it was before a change, from snapshots in memory

Round 5, R18 ("There is a new, separate "menu" where you can see the history. You can see
the changes made in that session and go back. If you close the program, the history is
lost, so every time you open it, its a blank slate").

In the context of the new History option (menu option 8), where Change a grade, Split a
category and the R19 drop/keep choice each save the class to `saved_classes/` right away,
facing the questions of what "go back" means when several changes were made, and how the
program remembers what to go back to,
we decided that the history lists only those three kinds of change, and that going back
to before change N puts the class's grades, splits and drop/keep choices back exactly as
they were before N (undoing N and every later change, which then leave the history),
after a Yes/No question, by keeping a copy of the whole class from just before each change
in a list that lives only in memory while the class is open,
and neglected undoing only the change picked while keeping the later ones, and also
neglected an "undo the latest change" that is repeated step by step, and also neglected
saving the history to a file, and also neglected recording each change as an
"opposite change" to apply backwards,
to achieve a going back that can never leave the class in a state it was never in
(undoing an old grade change under a later split could point at a part that no longer
exists), a history that is a blank slate every time the program opens, as R18 says, and
real grades that are never touched by what-if tries,
accepting that changes after the one picked are lost when going back (there is no redo,
which is why it asks Yes or No first), that goal changes, renames and deletes can't be
gone back on, and that each change keeps a copy of the class in memory (a few lines of
text, so it doesn't matter).

What is listed, the meaning of going back and where the option is were decided by the
student in the round 5 questions, from the options above. The Yes/No question, keeping
copies (snapshots) instead of opposite changes, and not adding a change that changes
nothing were chosen by Claude.
