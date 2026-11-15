"""Tests for reading and checking the class file (spec.md sections 1 and 2)."""

from fractions import Fraction

import pytest

from grades import FileProblems, Item, parse_class


def problems_for(text):
    """Return the list of problems parse_class reports for this text."""
    with pytest.raises(FileProblems) as caught:
        parse_class(text)
    return caught.value.problems


# --- Files that should be accepted ---

# Checks R1, R3.
def test_first_example_from_problem_md():
    text = (
        "homework / midterm / final / attendance\n"
        "30         30        30      10         = total weight\n"
        "20         20        20      10         = 70 out of 100\n"
    )
    assert parse_class(text) == [
        Item("homework", 30, 20),
        Item("midterm", 30, 20),
        Item("final", 30, 20),
        Item("attendance", 10, 10),
    ]


# Checks R4, R5.
def test_second_example_with_na_and_zero_weight():
    text = (
        "homework / midterm / final / attendance\n"
        "20         30        50      0\n"
        "20         20        N/A     0\n"
    )
    items = parse_class(text)
    assert items[2] == Item("final", 50, None)
    assert items[3] == Item("attendance", 0, 0)


# Checks R1, R2.
def test_extra_items_after_attendance_are_allowed():
    text = (
        "homework / midterm / final / attendance / project / quizzes\n"
        "20 20 20 10 20 10\n"
        "15 18 N/A 10 N/A 9\n"
    )
    items = parse_class(text)
    assert [item.name for item in items][4:] == ["project", "quizzes"]


@pytest.mark.parametrize("first_name", ["homework", "hw", "assignments", "HW", "Homework"])
# Checks R1, R2.
def test_homework_can_be_called_hw_or_assignments_in_any_capitals(first_name):
    text = f"{first_name} / MIDTERM / Final / attendance\n30 30 30 10\n20 20 20 10\n"
    assert len(parse_class(text)) == 4


# Checks R3.
def test_decimal_numbers_are_exact_fractions():
    text = "hw / midterm / final / attendance\n27.5 32.5 30 10\n20.25 30 N/A 10\n"
    items = parse_class(text)
    assert items[0].weight == Fraction(55, 2)
    assert items[0].grade == Fraction(81, 4)


# Checks R1, R7.
def test_blank_lines_and_note_only_lines_are_ignored():
    text = "\nhw / midterm / final / attendance\n\n= my notes\n30 30 30 10\n20 20 20 10\n\n"
    assert len(parse_class(text)) == 4


# Checks R5.
def test_na_is_accepted_in_any_capitals():
    text = "hw / midterm / final / attendance\n30 30 30 10\nn/a N/a N/A 10\n"
    assert [item.grade for item in parse_class(text)] == [None, None, None, 10]


# --- Files that should be rejected, with a clear explanation ---

# Checks R1, R8.
def test_wrong_number_of_lines():
    assert problems_for("hw / midterm / final / attendance\n30 30 30 10\n") == [
        "The file should have 3 lines (names, weights, grades), but it has 2."
    ]


# Checks R1, R2, R8.
def test_names_in_wrong_order_are_explained():
    text = "midterm / hw / final / attendance\n30 30 30 10\n20 20 20 10\n"
    assert problems_for(text) == [
        'Line 1: name 1 should be "homework" (or "hw" or "assignments"), but it is "midterm".',
        'Line 1: name 2 should be "midterm", but it is "hw".',
    ]


# Checks R2, R8.
def test_misspelled_name_is_explained():
    text = "hw / midtrem / final / attendance\n30 30 30 10\n20 20 20 10\n"
    assert problems_for(text) == ['Line 1: name 2 should be "midterm", but it is "midtrem".']


# Checks R2, R8.
def test_missing_attendance():
    text = "hw / midterm / final\n40 30 30\n20 20 20\n"
    assert problems_for(text) == [
        "Line 1: it needs at least homework / midterm / final / attendance, but it has only 3 name(s)."
    ]


@pytest.mark.parametrize("weights, total", [("30 30 30 0", "90"), ("30 30 30 20", "110")])
# Checks R3, R8.
def test_weights_must_add_up_to_exactly_100(weights, total):
    text = f"hw / midterm / final / attendance\n{weights}\n20 20 20 0\n"
    assert problems_for(text) == [
        f"Line 2: the weights add up to {total}, but they must add up to exactly 100."
    ]


# Checks R3, R5.
def test_weights_with_na_grades_still_must_add_up_to_100():
    text = "hw / midterm / final / attendance\n20 30 40 0\n20 20 N/A 0\n"
    assert problems_for(text) == [
        "Line 2: the weights add up to 90, but they must add up to exactly 100."
    ]


# Checks R3, R8.
def test_grade_above_its_weight():
    text = "hw / midterm / final / attendance\n30 30 30 10\n20 35 20 10\n"
    assert problems_for(text) == [
        "Line 3: grade 2 is 35, but it can't be more than its weight (30)."
    ]


# Checks R4, R8.
def test_zero_weight_item_must_have_zero_or_na():
    text = "hw / midterm / final / attendance\n40 30 30 0\n20 20 20 5\n"
    assert problems_for(text) == [
        "Line 3: grade 4 is 5, but its weight is 0, so the grade must be 0 or N/A."
    ]


@pytest.mark.parametrize("bad", ["-5", "abc", "1/2", "20%"])
# Checks R3, R8.
def test_grade_that_is_not_a_plain_number(bad):
    text = f"hw / midterm / final / attendance\n30 30 30 10\n{bad} 20 20 10\n"
    assert problems_for(text) == [
        f'Line 3: grade 1 is "{bad}", but a grade must be a number of 0 or more, or N/A.'
    ]


# Checks R3, R8.
def test_weight_that_is_not_a_number():
    text = "hw / midterm / final / attendance\n30 thirty 30 10\n20 20 20 10\n"
    assert problems_for(text) == [
        'Line 2: weight 2 is "thirty", but a weight must be a number of 0 or more.'
    ]


# Checks R1, R8.
def test_count_of_weights_and_grades_must_match_names():
    text = "hw / midterm / final / attendance\n30 30 40\n20 20 20 10 5\n"
    problems = problems_for(text)
    assert "Line 2: there are 4 names but 3 weights." in problems
    assert "Line 3: there are 4 names but 5 grades." in problems


# Checks R8.
def test_line_numbers_count_blank_lines():
    text = "\n\nhw / midterm / final / attendance\n30 30 30 10\n20 99 20 10\n"
    assert problems_for(text) == [
        "Line 5: grade 2 is 99, but it can't be more than its weight (30)."
    ]


# Checks R8.
def test_every_problem_is_listed_not_just_the_first():
    text = "hw / midtrem / final / attendance\n30 30 30 0\n20 20 40 0\n"
    assert len(problems_for(text)) == 3
