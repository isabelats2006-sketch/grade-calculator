"""Tests for the grade scale (spec.md section 19, R21): the scale's lines and marks, the
line saying how far the grade is from the goal, and the average of all classes.
"""

import pytest

from grades import average_percent, distance_text, parse_goal, scale_lines

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
