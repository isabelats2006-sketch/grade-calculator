# Problem

I have a lot on my plate right now and it would be much easier if I didnt have to make calculations or constantly recheck how far away I am from the grade I want or what/how does my score look at this point in the quarter. While I could write this down somewhere or be more organized and keep a good track of my current grade and desired grade, it would be much easier if I could have that information already and could just focus on studying. It would also allow me a better idea on how hard I need to study for a final/class, how far away I am form my goal and what is at stake.

# Initial requirements

- R1: It will read a file that contains, necessarily in this order: homework(assignments may also pass) / midterm / final / attendance / *any other grading type.
- R2: It must have hw, midterm, final, attendance and it will recognize other names, but after attendance, nothing else is mandatory. Capitals are fine, but the names and the order have to be exactly these, if not, it explains what went wrong. For the first one, homework, hw and assignments all work.
- R3: Together with the names it should under have the weights + current grades (0s are allowed as long as the total of everything is 100), the grades are points out of the weight (20 under 30 means 20 out of 30). The weights have to add up to exactly 100 or it doesnt accept the file, N/A ones still count in the 100, they just dont count in the current grade until they are out. It should look somewhat like this (the GOAL // CURRENT GRADE line is what the program shows at the top, its not in the file):
  ```
  GOAL = X grade // CURRENT GRADE = Y grade (the grade should be a letter grade and the GPA)
  homework / midterm / final / attendance 
  30         30        30      10         = total weight
  20         20        20      10         = 70 out of 100 = X GPA and X letter grade (it should do the calculation automatically)
  ```
- R4: Alternatively, if one of them does not exist in the class, it just has a 0 and is not counted for.
- R5: If one of the tested or the grade is not out yet it should be N/A in the lower part and the total weight should only count what has values:
  ```
  homework / midterm / final / attendance 
  20         30        50      0         = total weight
  20         20        N/A     0         = 40 out of 50 = X GPA and X letter grade 
  (no attendance and final not done yet)
  ```
- R6: The goal is typed in by the user, not in the file, and the program should say what I need on the N/A ones to reach my goal. You start it with just the file name (like python gradecalc.py csc299.txt) and then it asks you what your goal is, it should be as user friendly as possible. If there is more than one N/A, it says the same % needed on all of them.
- R7: Anything that does not fit inside does rules, doesnt mean the program doesnt run.
- R8: If any error is encountered, the program should run and explain the error to the user and if the problem is the file, ask the user to use a different file or update it.
- R9: This is the GPA and letter grading system to be used (decimals round to the nearest whole %, so 93.5% is 94% = A):
  ```
  A = 4.0 = 94 to 100%
  A- = 3.7 = 90 to 93%
  B+ = 3.3 = 87 to 89%
  B = 3.0 = 83 to 86%
  B- = 2.7 = 80 to 82%
  C+ = 2.3 = 77 to 79%
  C = 2.0 = 73 to 76%
  C- = 1.7 = 70 to 72%
  D+ = 1.3 = 67 to 69%
  D = 1.0 = 60 to 66%
  F = 0.0 = 0 to 59%
  ```
- R10: It can be used for multiple classes (so if ure having MATH 101 and WRD 101, for example, you can have a calc for both), so every session should have a name and be saved for future use.
- R11: It should also be easy to be modify.

# Round 2 requirements

- R12: It can delete a saved class and it double checks if the user wants to actually delete the class by asking: are you sure you want to delete it? it will be lost
- R13: It can rename any class at any point, special characters are allowed within reason

# Round 3 requirements

- R12 (CHANGED): It can delete a saved class and it double checks if the user wants to actually delete the class by asking: are you sure you want to delete it? it will be lost. Instead of typing the class name, you should type "Yes" or "No" to confirm the deletion
- R14: If the user has more then one class, then it can see all the GPA across all class together
- R15: The user can run an what if. It should be a separate option where he chooses the grades he will have and it will no be saved, once he is quits that mode, the grades should go back to what they were

# Round 4 requirements

- R16: Each item has their own percentage under them, so that the user can see how well (or bad) their doing in that specific category. It should look like this: 
```
  homework / midterm / final / attendance 
  20         30        40      10         = total weight
  15         20        N/A     10         = 45 out of 60 = X GPA and X letter grade 
  -------------------- === --------------------
  homework:       15 out of 20 = 75%
  midterm:        20 out of 30 = 67%
  final:          N/A
  attendance:     10 out of 10 = 100%
  TOTAL:          45 out of 60 = 75%
  ```

- R17: Any category, aside form Midterm and Final (that should ALWAYS BE 2.0 and 3.0), can be broken into smaller categories. The user has to choose to do this, if they dont, the normal case is the one presented preeviously. The idea behind it is that if the user has only been given 2 out of the 4 hw in the quarter they can see how well theyve done in those specific 2. It also adds more detail into the whatif category because they can look into possibilities of their future projects. The same works for attendance, it there is only been held 5 out of 20 classes (for example) the user can see how well they done in those classes. The user can divided this categories up to 10 times (from 1.0 to 1.9), any more then that, will not be allowed. Any separtion should always be done like the example (X.0 - X.9). It should look like this:
```
  1.0        1.1        2.0       3.0     4.0
  homework / homework / midterm / final / attendance 
  10         10         30        40      10         = total weight
  8          N/A        20        N/A     10         = 38 out of 50 = X GPA and X letter grade   
  (the numbers here are always shown to the user)     
  -------------------- === --------------------
  homework 1.0:   8 out of 10  = 80%
  homework 1.1:   N/A
  midterm:        20 out of 30 = 67%
  final:          N/A
  attendance:     10 out of 10 = 100%
  TOTAL:          38 out of 50 = 76%
  (here the numbers are only shown if needed)
  ```


# Round 5 requirements

- R18: There is a new, separate "menu" where you can see the history. You can see the changes made in that session and go back. If you close the program, the history is lost, so every time you open it, its a blank slate
- R19: In some classes, professors have many hw, or papers, etc and they choose to drop the lowest grade or get only the highest grade out of all of them. All of these options are allowed now, but the user has to specify that they want it. The standard version is that all the categories are taken into consideration for the grade. It should look like this:
```
  homework 1.0:   8 out of 10  = 80%
  homework 1.1:   4 out of 10  = 40%   (dropped)
  homework 1.2:   9 out of 10  = 90%
  ```

# Round 6 requirements

- R20: There is a new options called clear all grades, where the user can delete all the current grades. They go bak to being N/A and the history allows to go back in case it was a mistake. It clears the current class, the only way to go back is through the history. Splits also stay.
- R21: There is a new option called see the grade scale that takes you to another menu where you can click on any of the current attributes in a class (such as hw, midterm, final, etc) and once inside you see the full grade scale and can get a better understanding of how well (or not) your doing. The last two options in the menu are to see the grade in one class and the grades of all classes put together. It should look like this:
```
  GRADE SCALE (nearest whole %, so 93.5% is 94% = A)
  A  = 4.0 = 94 to 100%
  A- = 3.7 = 90 to 93%   <- your goal
  B+ = 3.3 = 87 to 89%   <- you are here (89%)
  B  = 3.0 = 83 to 86%   
  B- = 2.7 = 80 to 82%
  C+ = 2.3 = 77 to 79%
  C  = 2.0 = 73 to 76%
  C- = 1.7 = 70 to 72%
  D+ = 1.3 = 67 to 69%
  D  = 1.0 = 60 to 66%
  F  = 0.0 = 0 to 59%

  You are 1% from an A- (90%).
  ```
