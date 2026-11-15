"""Tests for the current grade, rounding and the letter/GPA scale (spec.md section 3)."""

from fractions import Fraction

import pytest

from grades import Item, current_grade, letter_for, parse_class, round_percent


# --- Rounding: nearest whole %, .5 goes up ---

@pytest.mark.parametrize(
    "percent, expected",
    [("93.5", 94), ("89.6", 90), ("89.4", 89), ("92.5", 93), ("80", 80), ("0", 0), ("100", 100)],
)
# Checks R9.
def test_round_percent_goes_to_nearest_with_half_up(percent, expected):
    assert round_percent(Fraction(percent)) == expected


# Checks R9.
def test_half_rounds_up_unlike_pythons_round():
    # Python's round(92.5) is 92; the spec says .5 goes up.
    assert round_percent(Fraction("92.5")) == 93


# --- The letter and GPA scale from problem.md ---

@pytest.mark.parametrize(
    "rounded, letter, gpa",
    [
        (100, "A", "4.0"), (94, "A", "4.0"),
        (93, "A-", "3.7"), (90, "A-", "3.7"),
        (89, "B+", "3.3"), (87, "B+", "3.3"),
        (86, "B", "3.0"), (83, "B", "3.0"),
        (82, "B-", "2.7"), (80, "B-", "2.7"),
        (79, "C+", "2.3"), (77, "C+", "2.3"),
        (76, "C", "2.0"), (73, "C", "2.0"),
        (72, "C-", "1.7"), (70, "C-", "1.7"),
        (69, "D+", "1.3"), (67, "D+", "1.3"),
        (66, "D", "1.0"), (60, "D", "1.0"),
        (59, "F", "0.0"), (0, "F", "0.0"),
    ],
)
# Checks R9.
def test_every_edge_of_the_scale(rounded, letter, gpa):
    assert letter_for(rounded) == (letter, gpa)


# --- The current grade ---

# Checks R3, R9.
def test_first_example_from_problem_md_is_70_out_of_100():
    items = parse_class("hw / midterm / final / attendance\n30 30 30 10\n20 20 20 10\n")
    grade = current_grade(items)
    assert (grade.earned, grade.out_of, grade.rounded) == (70, 100, 70)
    assert (grade.letter, grade.gpa) == ("C-", "1.7")


# Checks R4, R5.
def test_second_example_counts_only_graded_items_40_out_of_50():
    items = parse_class("hw / midterm / final / attendance\n20 30 50 0\n20 20 N/A 0\n")
    grade = current_grade(items)
    assert (grade.earned, grade.out_of, grade.rounded) == (40, 50, 80)
    assert (grade.letter, grade.gpa) == ("B-", "2.7")


# Checks R9.
def test_exact_89_point_5_is_an_a_minus_where_floats_would_say_b_plus():
    # In floats, 17.9 / 20 * 100 is 89.49999999999999, which would round to 89 (B+).
    items = [Item("hw", Fraction(20), Fraction("17.9")), Item("final", Fraction(80), None)]
    grade = current_grade(items)
    assert grade.percent == Fraction("89.5")
    assert (grade.rounded, grade.letter) == (90, "A-")


# Checks R4.
def test_zero_weight_items_are_left_out():
    items = [Item("hw", Fraction(50), Fraction(45)), Item("attendance", Fraction(0), Fraction(0))]
    assert current_grade(items).out_of == 50


# Checks R5.
def test_no_grades_out_yet_gives_none():
    items = parse_class("hw / midterm / final / attendance\n30 30 30 10\nN/A N/A N/A N/A\n")
    assert current_grade(items) is None


# Checks R3, R9.
def test_all_zero_scores_is_an_f_not_none():
    items = parse_class("hw / midterm / final / attendance\n30 30 30 10\n0 N/A N/A N/A\n")
    grade = current_grade(items)
    assert (grade.rounded, grade.letter, grade.gpa) == (0, "F", "0.0")
