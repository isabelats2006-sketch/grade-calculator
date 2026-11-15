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
