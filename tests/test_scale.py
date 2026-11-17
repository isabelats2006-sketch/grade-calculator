"""Tests for the grade scale (spec.md section 19, R21): the scale's lines and marks, the
line saying how far the grade is from the goal, the average of all classes, and the
grade scale menu (option 10).

The answers end with "q", not the menu's Quit number, so a new menu option doesn't
break them.
"""

import pytest

from grades import average_percent, distance_text, parse_class, parse_goal, scale_lines
from storage import load_class, save_class
from test_cli import SPEC_EXAMPLE, run

# The example in R21 (problem.md), copied from the program's output: 89% with goal A-.
R21_EXAMPLE = [
    "GRADE SCALE (nearest whole %, so 93.5% is 94% = A)",
    "A  = 4.0 = 94 to 100%",
    "A- = 3.7 = 90 to 93%   <- your goal",
    "B+ = 3.3 = 87 to 89%   <- you are here (89%)",
    "B  = 3.0 = 83 to 86%",
    "B- = 2.7 = 80 to 82%",
    "C+ = 2.3 = 77 to 79%",
    "C  = 2.0 = 73 to 76%",
    "C- = 1.7 = 70 to 72%",
    "D+ = 1.3 = 67 to 69%",
    "D  = 1.0 = 60 to 66%",
    "F  = 0.0 = 0 to 59%",
]
PLAIN = [line.split("   <- ")[0] for line in R21_EXAMPLE]


# Checks R21, R9.
def test_the_scale_matches_the_r21_example():
    assert scale_lines(89, parse_goal("A-")) == R21_EXAMPLE


# Checks R21.
def test_the_distance_line_matches_the_r21_example():
    assert distance_text(89, parse_goal("A-")) == "You are 1% from an A- (90%)."


# Checks R21, R9.
def test_with_no_grade_only_the_goal_is_marked():
    lines = scale_lines(None, parse_goal("B"))
    assert lines[4] == "B  = 3.0 = 83 to 86%   <- your goal"
    assert [line for line in lines if "<-" in line] == [lines[4]]
    assert distance_text(None, parse_goal("B")) == "No grade is out yet, so you are not on the scale yet."


# Checks R21, R9.
@pytest.mark.parametrize("here, line", [
    (100, 1), (94, 1), (93, 2), (90, 2), (89, 3), (87, 3), (86, 4), (83, 4), (82, 5),
    (80, 5), (79, 6), (77, 6), (76, 7), (73, 7), (72, 8), (70, 8), (69, 9), (67, 9),
    (66, 10), (60, 10), (59, 11), (0, 11),
])
def test_you_are_here_is_on_the_line_of_the_percent(here, line):
    lines = scale_lines(here, parse_goal("A"))
    marked = [number for number, text in enumerate(lines) if f"you are here ({here}%)" in text]
    assert marked == [line]
    assert lines[line].startswith(PLAIN[line] + "   <- ")


# Checks R21, R6.
def test_goal_and_here_on_the_same_line_share_one_mark():
    assert scale_lines(91, parse_goal("A-"))[2] == "A- = 3.7 = 90 to 93%   <- your goal, you are here (91%)"


# Checks R21, R6.
def test_a_goal_typed_as_a_gpa_is_marked_like_its_letter():
    assert scale_lines(None, parse_goal("3.7"))[2] == "A- = 3.7 = 90 to 93%   <- your goal"


# Checks R21, R6.
def test_a_goal_typed_as_a_percent_says_which_percent():
    lines = scale_lines(85, parse_goal("91%"))
    assert lines[2] == "A- = 3.7 = 90 to 93%   <- your goal (91%)"
    assert lines[4] == "B  = 3.0 = 83 to 86%   <- you are here (85%)"


# Checks R21, R6.
@pytest.mark.parametrize("here, goal, expected", [
    (89, "A-", "You are 1% from an A- (90%)."),
    (70, "B", "You are 13% from a B (83%)."),
    (90, "A-", "You reached your goal of A- (90%)."),
    (100, "B", "You reached your goal of B (83%)."),
    (89, "91%", "You are 2% from your goal of 91%."),
    (91, "91", "You reached your goal of 91%."),
    (90, "90.5%", "You are 1% from your goal of 90.5%."),  # 90.5% is reached at 91%
])
def test_the_distance_is_from_the_rounded_percent_to_the_goal(here, goal, expected):
    assert distance_text(here, parse_goal(goal)) == expected


# Checks R21, R14.
@pytest.mark.parametrize("percents, expected", [
    ([95, 85], 90),
    ([90, 91], 91),  # 90.5 goes up
    ([89, 90, 90], 90),  # 89.67
    ([77], 77),
    ([], None),
])
def test_average_percent(percents, expected):
    assert average_percent(percents) == expected


# --- The grade scale menu (option 10) ---

# The class of spec.md section 17: homework in 3 parts, its lowest grade dropped.
DROP_CLASS = (
    "homework / homework / homework / midterm / final / attendance\n"
    "10 10 10 30 30 10\n"
    "8 4 9 N/A N/A 10\n"
    "homework: drop lowest\n"
)
MENU_QUESTION = "Pick one by number, or press Enter to go back: "
HEADER = "GRADE SCALE: see where a grade is on the scale"
# Another saved class: 30 + 27 + 10 out of 70 = 95.7, so 96%.
MATH_101 = "homework / midterm / final / attendance\n30 30 30 10\n30 27 N/A 10\n"
NO_GRADES = "homework / midterm / final / attendance\n30 30 30 10\nN/A N/A N/A N/A\n"


def scale_run(tmp_path, text, answers, goal="A-"):
    """Open this class as "CSC 299" with this goal, then type the answers."""
    path = tmp_path / "csc299.txt"
    path.write_text(text, encoding="utf-8")
    return run([str(path)], ["CSC 299", goal] + answers, tmp_path / "saved")


# Checks R21, R17.
def test_the_menu_lists_each_part_then_the_class_then_all_classes(tmp_path):
    _, printed, questions = scale_run(tmp_path, DROP_CLASS, ["10", "q"])
    assert (
        f"{HEADER}\n"
        "  1) homework 1.0\n"
        "  2) homework 1.1\n"
        "  3) homework 1.2\n"
        "  4) midterm\n"
        "  5) final\n"
        "  6) attendance\n"
        "  7) The whole class (CSC 299)\n"
        "  8) All your classes together"
    ) in printed
    assert questions[-1] == MENU_QUESTION


# Checks R21, R9, R19.
def test_the_whole_class_matches_the_spec_example(tmp_path):
    _, printed, _ = scale_run(tmp_path, DROP_CLASS, ["10", "7", "q"])
    assert "\n".join(
        ["CSC 299: 35.5 out of 40 = 89% = B+ (3.3)", ""] + R21_EXAMPLE
        + ["", "You are 1% from an A- (90%).", "", HEADER]
    ) in printed


# Checks R21, R16, R19.
def test_a_dropped_part_shows_its_own_percent(tmp_path):
    _, printed, _ = scale_run(tmp_path, DROP_CLASS, ["10", "2", "q"])
    assert "homework 1.1: 4 out of 10 = 40%   (dropped)\n\nGRADE SCALE (" in printed
    assert "F  = 0.0 = 0 to 59%   <- you are here (40%)" in printed
    assert "You are 50% from an A- (90%)." in printed


# Checks R21, R16.
def test_a_part_at_the_goal_has_both_marks(tmp_path):
    _, printed, _ = scale_run(tmp_path, DROP_CLASS, ["10", "3", "q"])
    assert "homework 1.2: 9 out of 10 = 90%\n" in printed
    assert "A- = 3.7 = 90 to 93%   <- your goal, you are here (90%)" in printed
    assert "You reached your goal of A- (90%)." in printed


# Checks R21, R5.
def test_an_na_item_shows_only_the_goal(tmp_path):
    _, printed, _ = scale_run(tmp_path, DROP_CLASS, ["10", "4", "q"])
    assert "midterm: N/A\n\nGRADE SCALE (" in printed
    assert "you are here" not in printed
    assert "No grade is out yet, so you are not on the scale yet." in printed


# Checks R21, R4.
def test_an_item_with_weight_0_is_not_listed(tmp_path):
    text = "homework / midterm / final / attendance / project\n30 30 30 0 10\n20 20 N/A N/A 5\n"
    _, printed, _ = scale_run(tmp_path, text, ["10", "q"])
    assert (
        f"{HEADER}\n  1) homework\n  2) midterm\n  3) final\n  4) project\n"
        "  5) The whole class (CSC 299)\n  6) All your classes together"
    ) in printed


# Checks R21, R14, R10.
def test_all_classes_together_is_the_average_of_their_percents(tmp_path):
    saved = tmp_path / "saved"
    save_class(saved, "MATH 101", parse_class(MATH_101))
    save_class(saved, "WRD 101", parse_class(NO_GRADES))
    (saved / "Broken.txt").write_text("nonsense", encoding="utf-8")
    _, printed, _ = scale_run(tmp_path, SPEC_EXAMPLE, ["10", "7", "q"])
    assert (
        "All your classes together: 88%, the average of 2 classes\n"  # 79 and 96: 87.5 goes up
        "  Broken: can't be read, not counted\n"
        "  CSC 299: 79%\n"
        "  MATH 101: 96%\n"
        "  WRD 101: no grades out yet, not counted\n"
        "\n"
        "GRADE SCALE ("
    ) in printed
    # The open class's goal is used here too.
    assert "A- = 3.7 = 90 to 93%   <- your goal\nB+ = 3.3 = 87 to 89%   <- you are here (88%)" in printed
    assert "You are 2% from an A- (90%)." in printed


# Checks R21, R14.
def test_all_classes_together_with_only_one_class(tmp_path):
    _, printed, _ = scale_run(tmp_path, SPEC_EXAMPLE, ["10", "7", "q"], goal="C")
    assert "All your classes together: 79%, the average of 1 class\n  CSC 299: 79%\n" in printed
    assert "You reached your goal of C (73%)." in printed


# Checks R21, R14, R5.
def test_all_classes_together_with_no_grades_out(tmp_path):
    _, printed, _ = scale_run(tmp_path, NO_GRADES, ["10", "6", "q"])
    assert "All your classes together: no grades out yet\n  CSC 299: no grades out yet, not counted\n" in printed
    assert "No grade is out yet, so you are not on the scale yet." in printed


# Checks R21, R5.
def test_the_whole_class_with_no_grades_out(tmp_path):
    _, printed, _ = scale_run(tmp_path, NO_GRADES, ["10", "5", "q"])
    assert "CSC 299: no grades out yet\n\nGRADE SCALE (" in printed


# Checks R21, R7.
@pytest.mark.parametrize("typed", ["0", "9", "x", "1.0"])
def test_a_wrong_choice_is_explained_and_asked_again(tmp_path, typed):
    _, printed, questions = scale_run(tmp_path, DROP_CLASS, ["10", typed, "q"])
    assert "Please type a number from 1 to 8, or press Enter to go back." in printed
    assert questions[-2:] == [MENU_QUESTION, MENU_QUESTION]


# Checks R21.
def test_after_a_scale_the_menu_is_shown_again_and_enter_goes_back(tmp_path):
    _, printed, questions = scale_run(tmp_path, DROP_CLASS, ["10", "7", "1", "", "q"])
    assert printed.count(HEADER) == 3
    assert questions[-5:] == ["Choose 1 to 11: ", MENU_QUESTION, MENU_QUESTION, MENU_QUESTION, "Choose 1 to 11: "]
    # Back on the normal screen after Enter.
    assert printed.split(HEADER)[-1].count("GOAL = A- (3.7) // CURRENT GRADE = B+ (3.3), 89%") == 1


# Checks R21.
def test_q_quits_from_the_grade_scale_menu(tmp_path):
    _, printed, _ = scale_run(tmp_path, DROP_CLASS, ["10", "q"])
    assert printed.endswith("Bye!")


# Checks R21, R10.
def test_nothing_is_changed_or_saved(tmp_path):
    scale_run(tmp_path, DROP_CLASS, ["10", "1", "7", "8", "", "q"])
    assert load_class(tmp_path / "saved", "CSC 299") == parse_class(DROP_CLASS)
