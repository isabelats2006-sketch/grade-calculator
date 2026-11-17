# 0011: The grade scale menu is left by pressing Enter, so its last two options are the class and all classes

Round 6, R21 ("There is a new option called see the grade scale that takes you to another
menu where you can click on any of the current attributes in a class (such as hw, midterm,
final, etc) and once inside you see the full grade scale and can get a better
understanding of how well (or not) your doing. The last two options in the menu are to see
the grade in one class and the grades of all classes put together.").

In the context of the new grade scale menu (option 10 of the open-class menu), which lists
every item of the class and then needs some way back to the normal menu,
facing the problem that every other menu in the program (what-if, the history) ends with a
"Leave" option, but R21 says the last two options are the whole class and all classes put
together, so a "Leave" at the end would break R21's wording,
we decided that the menu lists the items, then "The whole class (CSC 299)" and "All your
classes together" as the last two numbers, and that pressing Enter (typing nothing) goes
back, with the question saying so: "Pick one by number, or press Enter to go back: ",
and neglected a numbered "Leave the grade scale" after the two (as in the other menus),
and also neglected a "0) Leave" option before the items, and also neglected showing the
scale once and going straight back to the normal menu after it,
to achieve a menu whose last two options are exactly what R21 asks for, that can still be
left in one keystroke, and that can be used to look at several scales in a row (the menu is
shown again after each scale),
accepting that this is the only menu in the program left with Enter instead of a number
(the question says how, and `q` still quits as everywhere), and that pressing Enter by
mistake leaves the menu (nothing is changed there, so it loses nothing).

Chosen by Claude. The student chose where the option is (option 10, with Clear all grades
9 and Quit 11), that each part of a split category is its own item, and that N/A items
are listed.
