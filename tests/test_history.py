"""Tests for the history of this session and going back (spec.md section 16, R18).

The answers end with "q", not the menu's Quit number, so a new menu option doesn't
break them. "8" is the History option.
"""

import pytest

from grades import DROP_LOWEST, Item, parse_class
from storage import load_class, save_class
from test_cli import SPEC_EXAMPLE, run

HEADER = "HISTORY: changes made since the program was opened (lost when it is closed)"
EMPTY = "No changes yet since the program was opened, so there is nothing to go back to."

# Three changes: homework 20 -> 18, split homework into 3 parts, drop its lowest grade.
THREE_CHANGES = [
    "1", "1", "18",
    "6", "1", "3", "10", "10", "10", "8", "4", "9",
    "7", "1", "2",
]


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


# Checks R18, R17, R19.
def test_the_history_lists_the_changes_in_order(class_file, saved):
    _, printed, questions = opened(class_file, saved, THREE_CHANGES + ["8", "q"])
    assert (
        f"{HEADER}\n"
        "  1) Changed homework from 20 to 18\n"
        "  2) Split homework into 3 parts\n"
        "  3) homework now drops the lowest grade\n"
        "\n"
        "1) Go back to before a change\n"
        "2) Leave the history"
    ) in printed
    assert questions[-1] == "Choose 1 or 2: "


# Checks R18, R17.
def test_a_part_and_an_na_grade_are_named_as_on_the_screen(class_file, saved):
    answers = ["6", "1", "2", "15", "15", "10", "N/A", "1", "2", "12", "1", "5", "N/A", "8", "q"]
    _, printed, _ = opened(class_file, saved, answers)
    assert "  2) Changed homework 1.1 from N/A to 12\n  3) Changed attendance from 10 to N/A" in printed


# Checks R18, R17.
def test_joining_back_into_one_part_is_listed(class_file, saved):
    answers = ["6", "1", "2", "15", "15", "10", "N/A", "6", "1", "1", "25", "8", "q"]
    _, printed, _ = opened(class_file, saved, answers)
    assert "  1) Split homework into 2 parts\n  2) Joined homework back into one" in printed


# Checks R18.
def test_with_no_changes_there_is_nothing_to_go_back_to(class_file, saved):
    _, printed, questions = opened(class_file, saved, ["8", "q"])
    assert EMPTY in printed
    assert HEADER not in printed
    assert questions[-1].startswith("Choose 1 to")  # back to the menu


# Checks R18, R15.
def test_what_if_the_goal_and_renames_are_not_in_the_history(class_file, saved):
    answers = ["5", "1", "1", "30", "2", "2", "A", "3", "CSC 299 Fall", "8", "q"]
    _, printed, _ = opened(class_file, saved, answers)
    assert EMPTY in printed


# Checks R18.
def test_a_change_that_changes_nothing_is_not_added(class_file, saved):
    _, printed, _ = opened(class_file, saved, ["1", "1", "20", "7", "8", "q"])
    # homework already had 20; option 7 with nothing split changes nothing either
    assert EMPTY in printed


# Checks R18, R10, R17, R19.
def test_going_back_undoes_that_change_and_every_later_one(class_file, saved):
    answers = THREE_CHANGES + ["8", "1", "2", "Yes", "8", "q"]
    _, printed, questions = opened(class_file, saved, answers)
    assert ("Go back to before change 2? Changes 2 to 3 will be undone. "
            "Type Yes or No: ") in questions
    assert "Went back to before change 2.\nSaved." in printed
    # The split and the drop choice are gone; the first change stays.
    assert load_class(saved, "CSC 299") == parse_class(SPEC_EXAMPLE.replace("20 25", "18 25"))
    # Changes 2 and 3 left the history.
    last = printed.split(HEADER)[-1]
    assert "  1) Changed homework from 20 to 18\n\n" in last
    assert "2) Split" not in last


# Checks R18, R16.
def test_the_screen_after_going_back_shows_the_old_grades(class_file, saved):
    _, printed, _ = opened(class_file, saved, ["1", "1", "18", "8", "1", "1", "yes", "q"])
    after = printed.split("Went back to before change 1.")[1]
    assert "homework:       20 out of 30 = 67%" in after
    assert load_class(saved, "CSC 299") == parse_class(SPEC_EXAMPLE)


# Checks R18, R19.
def test_going_back_to_the_last_change_undoes_only_it(class_file, saved):
    answers = THREE_CHANGES + ["8", "1", "3", " YES ", "q"]
    _, _, questions = opened(class_file, saved, answers)
    assert "Go back to before change 3? Change 3 will be undone. Type Yes or No: " in questions
    items = load_class(saved, "CSC 299")
    assert items[:3] == [Item("homework", 10, 8), Item("homework", 10, 4), Item("homework", 10, 9)]
    assert DROP_LOWEST not in [item.rule for item in items]


# Checks R18.
def test_no_undoes_nothing_and_shows_the_history_again(class_file, saved):
    answers = ["1", "1", "18", "8", "1", "1", "maybe", "No", "2", "q"]
    _, printed, _ = opened(class_file, saved, answers)
    assert "Please type Yes or No." in printed
    assert "Nothing was undone." in printed.split(HEADER)[1]
    assert printed.count(HEADER) == 2
    assert load_class(saved, "CSC 299")[0] == Item("homework", 30, 18)


# Checks R18, R8.
def test_wrong_answers_in_the_history_are_asked_again(class_file, saved):
    answers = ["1", "1", "18", "8", "3", "1", "2", "1", "no", "2", "q"]
    _, printed, _ = opened(class_file, saved, answers)
    assert "Please type 1 or 2." in printed
    assert "Please type a number from 1 to 1." in printed


# Checks R18.
def test_leaving_the_history_goes_back_to_the_menu(class_file, saved):
    _, _, questions = opened(class_file, saved, ["1", "1", "18", "8", "2", "q"])
    assert questions[-1].startswith("Choose 1 to")
    assert questions[-2] == "Choose 1 or 2: "


# Checks R18.
def test_q_while_going_back_quits_and_undoes_nothing(class_file, saved):
    _, printed, _ = opened(class_file, saved, ["1", "1", "18", "8", "1", "1", "q"])
    assert "Went back" not in printed
    assert load_class(saved, "CSC 299")[0] == Item("homework", 30, 18)


# Checks R18, R13.
def test_renaming_keeps_the_history_and_going_back_saves_the_renamed_class(class_file, saved):
    answers = ["1", "1", "18", "3", "CSC 299 Fall", "8", "1", "1", "Yes", "q"]
    _, printed, _ = opened(class_file, saved, answers)
    assert "  1) Changed homework from 20 to 18" in printed
    assert load_class(saved, "CSC 299 Fall") == parse_class(SPEC_EXAMPLE)
    assert not (saved / "CSC 299.txt").exists()


# Checks R18, R10.
def test_every_time_the_program_is_opened_the_history_is_empty(class_file, saved):
    opened(class_file, saved, ["1", "1", "18", "q"])
    _, printed, _ = run([], ["1", "B", "8", "q"], saved)  # open the saved class again
    assert EMPTY in printed
    assert load_class(saved, "CSC 299")[0] == Item("homework", 30, 18)  # the change stays


# Checks R18, R12.
def test_after_deleting_the_class_the_next_one_starts_with_an_empty_history(class_file, saved):
    save_class(saved, "MATH 101", parse_class(SPEC_EXAMPLE))
    answers = ["1", "1", "18", "4", "Yes", "1", "B", "8", "q"]
    _, printed, _ = opened(class_file, saved, answers)
    assert EMPTY in printed.split('Deleted "CSC 299".')[1]
