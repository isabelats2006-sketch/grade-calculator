"""Tests for clearing all grades (spec.md section 18, R20).

The answers end with "q", not the menu's Quit number, so a new menu option doesn't
break them. "9" is the Clear all grades option and "8" the History option.
"""

from fractions import Fraction

import pytest

from grades import DROP_LOWEST, Item, cleared, has_grades, parse_class
from storage import load_class, save_class
from test_cli import SPEC_EXAMPLE, run

QUESTION = (
    'Are you sure you want to clear all the grades of "CSC 299"? They will all be N/A. '
    "You can go back with the history (option 8). Type Yes or No: "
)
CLEARED = 'Cleared all the grades of "CSC 299". They are all N/A now.'
NOTHING_TO_CLEAR = "All the grades are already N/A, so there is nothing to clear."
# Split homework into 3 parts (10, 10, 10; grades 8, 4, 9), then drop its lowest grade.
SPLIT_AND_DROP = ["6", "1", "3", "10", "10", "10", "8", "4", "9", "7", "1", "2"]


@pytest.fixture
def class_file(tmp_path):
    path = tmp_path / "csc299.txt"
    path.write_text(SPEC_EXAMPLE, encoding="utf-8")
    return path


@pytest.fixture
def saved(tmp_path):
    return tmp_path / "saved_classes"


def opened(class_file, saved, answers):
    """Open the class file as "CSC 299" with goal B, then type these answers."""
    return run([str(class_file)], ["CSC 299", "B"] + answers, saved)


# Checks R20.
def test_yes_makes_every_grade_na_and_saves_it(class_file, saved):
    _, printed, questions = opened(class_file, saved, ["9", "Yes", "q"])
    assert QUESTION in questions
    assert f"{CLEARED}\nSaved." in printed
    assert load_class(saved, "CSC 299") == [
        Item(item.name, item.weight, None) for item in parse_class(SPEC_EXAMPLE)
    ]


# Checks R20, R5.
def test_the_screen_after_clearing_has_no_grades(class_file, saved):
    _, printed, _ = opened(class_file, saved, ["9", "yes", "q"])
    after = printed.split(CLEARED)[1]
    assert "GOAL = B (3.0) // CURRENT GRADE = no grades out yet" in after
    assert "N/A        N/A       N/A     N/A          N/A      = no grades out yet" in after
    assert "TOTAL:          no grades out yet" in after


# Checks R20, R17, R19.
def test_splits_and_the_drop_choice_stay(class_file, saved):
    opened(class_file, saved, SPLIT_AND_DROP + ["9", "Yes", "q"])
    items = load_class(saved, "CSC 299")
    assert [item.name for item in items] == [
        "homework", "homework", "homework", "midterm", "final", "attendance", "project",
    ]
    assert [item.weight for item in items] == [10, 10, 10, 30, 20, 10, 10]
    assert all(item.grade is None for item in items)
    assert [item.rule for item in items[:3]] == [DROP_LOWEST] * 3


# Checks R20, R12.
def test_no_keeps_every_grade(class_file, saved):
    _, printed, _ = opened(class_file, saved, ["9", " No ", "q"])
    assert "Nothing was cleared." in printed
    assert CLEARED not in printed
    assert load_class(saved, "CSC 299") == parse_class(SPEC_EXAMPLE)


# Checks R20, R7.
def test_another_answer_asks_again(class_file, saved):
    _, printed, questions = opened(class_file, saved, ["9", "", "maybe", "YES", "q"])
    assert printed.count("Please type Yes or No.") == 2
    assert questions.count(QUESTION) == 3
    assert CLEARED in printed


# Checks R20, R18.
def test_clearing_is_in_the_history_and_going_back_brings_the_grades_back(class_file, saved):
    answers = ["9", "Yes", "8", "1", "1", "Yes", "q"]
    _, printed, _ = opened(class_file, saved, answers)
    assert "  1) Cleared all grades" in printed
    assert "Went back to before change 1." in printed
    assert load_class(saved, "CSC 299") == parse_class(SPEC_EXAMPLE)


# Checks R20, R18, R17, R19.
def test_going_back_keeps_the_splits_and_brings_back_each_part(class_file, saved):
    opened(class_file, saved, SPLIT_AND_DROP + ["9", "Yes", "8", "1", "3", "Yes", "q"])
    items = load_class(saved, "CSC 299")
    assert [item.grade for item in items[:3]] == [8, 4, 9]
    assert items[0].rule == DROP_LOWEST


# Checks R20, R18.
def test_with_every_grade_already_na_nothing_is_asked_or_added(tmp_path, saved):
    path = tmp_path / "new.txt"
    path.write_text("hw / midterm / final / attendance\n30 30 30 10\nN/A N/A N/A N/A\n", encoding="utf-8")
    _, printed, questions = run([str(path)], ["CSC 299", "B", "9", "8", "q"], saved)
    assert NOTHING_TO_CLEAR in printed
    assert not any(question.startswith("Are you sure") for question in questions)
    assert "No changes yet since the program was opened" in printed


# Checks R20, R10.
def test_only_the_open_class_is_cleared(class_file, saved):
    other = parse_class(SPEC_EXAMPLE)
    save_class(saved, "MATH 101", other)
    opened(class_file, saved, ["9", "Yes", "q"])
    assert load_class(saved, "MATH 101") == other
    assert not has_grades(load_class(saved, "CSC 299"))


# Checks R20.
def test_q_at_the_question_quits_and_clears_nothing(class_file, saved):
    _, printed, _ = opened(class_file, saved, ["9", "q"])
    assert printed.endswith("Bye!")
    assert load_class(saved, "CSC 299") == parse_class(SPEC_EXAMPLE)


# Checks R20, R17, R19, R4.
def test_cleared_keeps_names_weights_and_choices():
    items = [
        Item("homework", Fraction(10), Fraction(8), DROP_LOWEST),
        Item("homework", Fraction(10), Fraction(4), DROP_LOWEST),
        Item("midterm", Fraction(40), None),
        Item("final", Fraction(40), Fraction(30)),
        Item("attendance", Fraction(0), Fraction(0)),
    ]
    assert cleared(items) == [
        Item("homework", Fraction(10), None, DROP_LOWEST),
        Item("homework", Fraction(10), None, DROP_LOWEST),
        Item("midterm", Fraction(40), None),
        Item("final", Fraction(40), None),
        Item("attendance", Fraction(0), None),
    ]
    assert items[0].grade == 8  # the class given is not changed


# Checks R20, R4.
@pytest.mark.parametrize("grades, expected", [
    ([None, None, None, None], False),
    ([None, None, None, Fraction(0)], False),  # attendance has weight 0: not in this class
    ([None, Fraction(0), None, None], True),  # a 0 is still a grade
])
def test_has_grades(grades, expected):
    weights = [Fraction(30), Fraction(30), Fraction(40), Fraction(0)]
    names = ["homework", "midterm", "final", "attendance"]
    items = [Item(n, w, g) for n, w, g in zip(names, weights, grades)]
    assert has_grades(items) is expected
