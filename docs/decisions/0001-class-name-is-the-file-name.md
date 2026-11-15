# 0001: A class's name stays its file name, so rename keeps the Windows rule

Round 2, R13 ("rename any class at any point, special characters are allowed within reason").

In the context of renaming a saved class (R13), where each class is saved as
`saved_classes/<name>.txt`,
facing the question of which special characters "within reason" allows, when Windows refuses
`\ / : * ? " < > |` in file names,
we decided to keep the class name as the file name and allow every character Windows allows
(`&`, `#`, `'`, `( )`, `!`, accents, emoji, ...), refusing only those 9 and Windows'
reserved names with an explanation,
and neglected storing the name inside the file (a fourth line, or a separate index file) so
that any character could be used, and also neglected allowing only letters, numbers, spaces,
`-` and `_`,
to achieve a simple rename (one file rename, nothing else to keep in step), saved files that
keep the round 1 three-line layout and stay easy to edit by hand (R11), and the same name rule
for new classes and renamed ones,
accepting that a name like `CSC 299 / Lab` can't be used and must be written another way,
like `CSC 299 - Lab`.

Decided by the student in the round 2 questions, from the options above.
