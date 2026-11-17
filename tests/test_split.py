"""Tests for categories split into parts (spec.md section 15, R17)."""

from fractions import Fraction

import pytest

from gradecalc import screen
from grades import (
    Item, SplitProblem, describe_needed, is_split, labels, needed_for, numbers, parse_class,
    parse_goal, parse_part_weight, split_category, splittable,
)
from storage import load_class, save_class
from test_cli import run
from test_parse import problems_for

R17_EXAMPLE = (
    "homework / homework / midterm / final / attendance\n"
    "10 10 30 40 10\n"
    "8 N/A 20 N/A 10\n"
)


def file_with(names, weights, grades):
    return f"{names}\n{weights}\n{grades}\n"


# --- Reading a split category from the file ---

# Checks R17.
def test_a_repeated_name_is_one_category_in_parts():
    items = parse_class(R17_EXAMPLE)
    assert items[:2] == [Item("homework", 10, 8), Item("homework", 10, None)]
    assert numbers(items) == ["1.0", "1.1", "2.0", "3.0", "4.0"]
    assert labels(items) == ["homework 1.0", "homework 1.1", "midterm", "final", "attendance"]
    assert is_split(items)


# Checks R17, R16.
def test_nothing_split_means_every_item_is_x_0_and_shown_by_its_name():
    items = parse_class(file_with("hw / midterm / final / attendance / project",
                                  "20 30 30 10 10", "15 20 N/A 10 N/A"))
    assert numbers(items) == ["1.0", "2.0", "3.0", "4.0", "5.0"]
    assert labels(items) == ["hw", "midterm", "final", "attendance", "project"]
    assert not is_split(items)


# Checks R17.
def test_attendance_and_categories_after_it_can_be_split_too():
    items = parse_class(file_with(
        "hw / midterm / final / attendance / attendance / attendance / project / project",
        "20 30 30 2 2 6 5 5", "15 20 N/A 2 0 N/A 5 N/A"))
    assert numbers(items) == ["1.0", "2.0", "3.0", "4.0", "4.1", "4.2", "5.0", "5.1"]
    assert labels(items)[3:] == [
        "attendance 4.0", "attendance 4.1", "attendance 4.2", "project 5.0", "project 5.1",
    ]


# Checks R17.
def test_capitals_dont_matter_but_spellings_do():
    items = parse_class(file_with("Homework / homework / midterm / final / attendance",
                                  "10 10 30 40 10", "8 N/A 20 N/A 10"))
    assert numbers(items)[:2] == ["1.0", "1.1"]
    # hw and homework are different names: the second one is where midterm should be.
    assert 'Line 1: name 2 should be "midterm", but it is "hw".' in problems_for(
        file_with("homework / hw / midterm / final / attendance",
                  "10 10 30 40 10", "8 N/A 20 N/A 10"))


# Checks R17.
def test_up_to_10_parts_are_allowed():
    items = parse_class(file_with(
        " / ".join(["hw"] * 10) + " / midterm / final / attendance",
        " ".join(["2"] * 10) + " 30 40 10", " ".join(["N/A"] * 10) + " 20 N/A 10"))
    assert numbers(items)[:10] == [f"1.{part}" for part in range(10)]
    assert numbers(items)[10] == "2.0"


# Checks R17, R8.
def test_11_parts_are_refused_and_explained():
    problems = problems_for(file_with(
        "hw / midterm / final / attendance / " + " / ".join(["quiz"] * 11),
        "20 30 30 9 " + " ".join(["1"] * 11), "N/A 20 N/A 9 " + " ".join(["1"] * 11)))
    assert problems == [
        'Line 1: "quiz" is split into 11 parts, but a category can have at most 10 (5.0 to 5.9).'
    ]


# Checks R17, R8.
@pytest.mark.parametrize("names, repeated", [
    ("hw / midterm / midterm / final / attendance", "midterm"),
    ("hw / midterm / final / Final / attendance", "final"),
])
def test_midterm_and_final_cant_be_split(names, repeated):
    problems = problems_for(file_with(names, "20 20 20 30 10", "N/A N/A N/A N/A 10"))
    assert problems == [
        f'Line 1: "{repeated}" is there 2 times, but midterm and final can\'t be split into parts.'
    ]


# Checks R17, R8.
def test_a_name_in_two_places_is_explained_once():
    problems = problems_for(file_with(
        "hw / midterm / final / attendance / project / quiz / project / project",
        "20 30 30 10 2 4 2 2", "N/A 20 N/A 10 1 4 2 2"))
    assert problems == [
        'Line 1: "project" is in more than one place. '
        "The parts of a split category must be side by side."
    ]


# Checks R2, R17, R8.
def test_the_name_order_is_checked_on_categories():
    problems = problems_for(file_with("hw / hw / midtrem / final / attendance",
                                      "10 10 30 40 10", "8 N/A 20 N/A 10"))
    assert problems == ['Line 1: name 3 should be "midterm", but it is "midtrem".']


# Checks R3, R17, R8.
def test_the_parts_weights_still_must_add_up_to_100():
    problems = problems_for(file_with("hw / hw / midterm / final / attendance",
                                      "10 5 30 40 10", "8 N/A 20 N/A 10"))
    assert problems == ["Line 2: the weights add up to 95, but they must add up to exactly 100."]


# Checks R3, R17, R8.
def test_each_part_follows_the_grade_rules():
    problems = problems_for(file_with("hw / hw / midterm / final / attendance",
                                      "10 10 30 40 10", "8 12 20 N/A 10"))
    assert problems == ["Line 3: grade 2 is 12, but it can't be more than its weight (10)."]


# Checks R10, R11, R17.
def test_a_split_class_is_saved_as_repeated_names_and_loads_back(tmp_path):
    items = parse_class(R17_EXAMPLE)
    save_class(tmp_path, "CSC 299", items)
    text = (tmp_path / "CSC 299.txt").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "homework / homework / midterm / final / attendance"
    assert len(text.splitlines()) == 3  # the numbers are not in the file
    assert load_class(tmp_path, "CSC 299") == items


# --- On the screen ---

# Checks R16, R17, R9.
def test_the_screen_matches_the_r17_example():
    shown = screen(parse_class(R17_EXAMPLE), "CSC 299", parse_goal("B"))
    assert "\n".join(shown[3:]) == (
        "1.0        1.1        2.0       3.0     4.0\n"
        "homework / homework / midterm / final / attendance\n"
        "10         10         30        40      10          = total weight\n"
        "8          N/A        20        N/A     10          = 38 out of 50 = 76% = C (2.0)\n"
        "-------------------- === --------------------\n"
        "homework 1.0:   8 out of 10  = 80%\n"
        "homework 1.1:   N/A\n"
        "midterm:        20 out of 30 = 67%\n"
        "final:          N/A\n"
        "attendance:     10 out of 10 = 100%\n"
        "TOTAL:          38 out of 50 = 76%\n"
        "\n"
        "You need at least 89% on homework 1.1 and final to get a B."
    )


# Checks R17, R16.
def test_no_numbers_row_when_nothing_is_split():
    shown = screen(parse_class(file_with("homework / midterm / final / attendance",
                                         "20 30 40 10", "15 20 N/A 10")),
                   "CSC 299", parse_goal("B"))
    assert shown[3] == "homework / midterm / final / attendance"
    assert not any(line.startswith("1.0") for line in shown)


# Checks R6, R17.
def test_the_needed_sentence_names_the_parts():
    items = parse_class(R17_EXAMPLE)
    goal = parse_goal("B")
    needed = needed_for(items, goal)
    assert needed.remaining == ["homework 1.1", "final"]
    # (82.5 - 38) / 50 = 89%: following it on both N/A items reaches 82.5% = B.
    assert describe_needed(needed, goal) == (
        "You need at least 89% on homework 1.1 and final to get a B."
    )


# Checks R11, R17.
def test_change_a_grade_lists_the_parts_and_saves_the_one_picked(tmp_path):
    path = tmp_path / "csc299.txt"
    path.write_text(R17_EXAMPLE, encoding="utf-8")
    saved = tmp_path / "saved"
    _, printed, questions = run([str(path)], ["CSC 299", "B", "1", "2", "9", "q"], saved)
    assert "  1) homework 1.0: 8 out of 10\n  2) homework 1.1: N/A out of 10\n" in printed
    assert "New grade for homework 1.1 (out of 10, or N/A): " in questions
    assert load_class(saved, "CSC 299")[1] == Item("homework", 10, 9)
    assert "homework 1.1:   9 out of 10  = 90%" in printed


# Checks R15, R17.
def test_what_if_can_try_a_grade_on_one_part_without_saving(tmp_path):
    path = tmp_path / "csc299.txt"
    path.write_text(R17_EXAMPLE, encoding="utf-8")
    saved = tmp_path / "saved"
    _, printed, _ = run([str(path)], ["CSC 299", "B", "5", "1", "2", "10", "2", "q"], saved)
    tried = printed.split("WHAT IF: nothing here is saved")[-1].split("Left what-if mode.")[0]
    assert "homework 1.1:   10 out of 10 = 100%" in tried
    assert load_class(saved, "CSC 299") == parse_class(R17_EXAMPLE)


# --- Split a category (menu option 6) ---

UNSPLIT = (
    "homework / midterm / final / attendance / project\n"
    "20 30 30 10 10\n"
    "15 20 N/A 10 N/A\n"
)


def split_run(tmp_path, text, answers):
    """Open this class file, goal B, then type these answers. Returns (printed, questions, saved)."""
    path = tmp_path / "csc299.txt"
    path.write_text(text, encoding="utf-8")
    saved = tmp_path / "saved"
    _, printed, questions = run([str(path)], ["CSC 299", "B"] + answers, saved)
    return printed, questions, saved


# Checks R17.
def test_split_lists_every_category_but_midterm_and_final(tmp_path):
    printed, questions, _ = split_run(tmp_path, UNSPLIT, ["6", "q"])
    assert (
        "Which category? (midterm and final can't be split)\n"
        "  1) homework (1), weight 20\n"
        "  2) attendance (4), weight 10\n"
        "  3) project (5), weight 10\n"
    ) in printed
    assert questions[-1] == "Which one? (number): "


# Checks R17, R10.
def test_splitting_homework_into_2_parts_saves_them_and_shows_the_numbers(tmp_path):
    answers = ["6", "1", "2", "10", "10", "8", "N/A", "q"]
    printed, questions, saved = split_run(tmp_path, UNSPLIT, answers)
    assert questions[-7:-1] == [
        "Which one? (number): ",
        "How many parts? (2 to 10, or 1 to join it back into one): ",
        "Weight of homework 1.0 (the 2 parts must add up to 20): ",
        "Weight of homework 1.1 (the 2 parts must add up to 20): ",
        "Grade for homework 1.0 (out of 10, or N/A): ",
        "Grade for homework 1.1 (out of 10, or N/A): ",
    ]
    assert load_class(saved, "CSC 299") == parse_class(
        "homework / homework / midterm / final / attendance / project\n"
        "10 10 30 30 10 10\n"
        "8 N/A 20 N/A 10 N/A\n"
    )
    after = printed.split("Saved.")[-1]
    assert "1.0        1.1        2.0       3.0     4.0          5.0\n" in after
    assert "homework 1.0:   8 out of 10  = 80%\nhomework 1.1:   N/A\n" in after


# Checks R17, R3, R7.
def test_parts_that_dont_add_up_are_explained_and_asked_again(tmp_path):
    answers = ["6", "1", "2", "10", "5", "12", "8", "N/A", "N/A", "q"]
    printed, _, saved = split_run(tmp_path, UNSPLIT, answers)
    assert (
        "The parts add up to 15, but they must add up to 20, the weight of homework. "
        "Please type them again."
    ) in printed
    items = load_class(saved, "CSC 299")
    assert [item.weight for item in items[:2]] == [12, 8]
    assert sum(item.weight for item in items) == 100


# Checks R17, R7.
@pytest.mark.parametrize("typed, message", [
    ("0", "A part's weight must be above 0."),
    ("ten", 'I didn\'t understand "ten". Type a number above 0, like 10.'),
    ("-5", 'I didn\'t understand "-5". Type a number above 0, like 10.'),
])
def test_a_bad_part_weight_is_explained_and_asked_again(tmp_path, typed, message):
    answers = ["6", "1", "2", typed, "10", "10", "N/A", "N/A", "q"]
    printed, questions, saved = split_run(tmp_path, UNSPLIT, answers)
    assert message in printed
    assert questions.count("Weight of homework 1.0 (the 2 parts must add up to 20): ") == 2
    assert [item.weight for item in load_class(saved, "CSC 299")[:2]] == [10, 10]


# Checks R17, R7.
@pytest.mark.parametrize("typed", ["0", "11", "x", ""])
def test_more_than_10_parts_or_not_a_number_is_asked_again(tmp_path, typed):
    printed, questions, _ = split_run(tmp_path, UNSPLIT, ["6", "1", typed, "q"])
    assert "Please type a number from 1 to 10." in printed
    assert questions.count("How many parts? (2 to 10, or 1 to join it back into one): ") == 2


# Checks R17, R7.
def test_a_bad_grade_for_a_part_is_explained_and_asked_again(tmp_path):
    answers = ["6", "1", "2", "10", "10", "12", "8", "N/A", "q"]
    printed, _, saved = split_run(tmp_path, UNSPLIT, answers)
    assert "The grade can't be more than its weight (10)." in printed
    assert load_class(saved, "CSC 299")[0] == Item("homework", 10, 8)


# Checks R17.
def test_1_part_joins_a_split_category_back_into_one(tmp_path):
    printed, questions, saved = split_run(tmp_path, R17_EXAMPLE, ["6", "1", "1", "18", "q"])
    assert "Grade for homework (out of 20, or N/A): " in questions
    assert not any(question.startswith("Weight of") for question in questions)
    assert load_class(saved, "CSC 299")[0] == Item("homework", 20, 18)
    after = printed.split("Saved.")[-1]
    assert "1.0" not in after  # nothing is split any more: no numbers row
    assert "homework:       18 out of 20 = 90%" in after


# Checks R17.
def test_splitting_a_split_category_again_redoes_it(tmp_path):
    answers = ["6", "1", "3", "5", "5", "10", "5", "N/A", "N/A", "q"]
    printed, _, saved = split_run(tmp_path, R17_EXAMPLE, answers)
    assert "  1) homework (1), weight 20, in 2 parts\n" in printed
    assert [(item.name, item.weight, item.grade) for item in load_class(saved, "CSC 299")[:4]] == [
        ("homework", 5, 5), ("homework", 5, None), ("homework", 10, None), ("midterm", 30, 20),
    ]


# Checks R17, R4.
def test_a_category_with_weight_0_cant_be_split(tmp_path):
    text = "homework / midterm / final / attendance\n30 30 40 0\n20 20 N/A 0\n"
    printed, questions, saved = split_run(tmp_path, text, ["6", "2", "q"])
    assert "attendance is not in this class (weight 0), so it can't be split." in printed
    assert questions[-1] == "Choose 1 to 11: "  # back to the menu
    assert load_class(saved, "CSC 299") == parse_class(text)


# Checks R17, R7.
def test_q_in_the_middle_of_a_split_quits_and_changes_nothing(tmp_path):
    printed, _, saved = split_run(tmp_path, UNSPLIT, ["6", "1", "2", "10", "q"])
    assert printed.endswith("Bye!")
    assert load_class(saved, "CSC 299") == parse_class(UNSPLIT)


# Checks R17.
def test_split_category_keeps_the_weights_at_100_and_refuses_what_breaks_the_rules():
    items = parse_class(UNSPLIT)
    assert [(number, group) for number, group in splittable(items)] == [(1, [0]), (4, [3]), (5, [4])]
    split = split_category(items, [4], [Item("project", 4, 4), Item("project", 6, None)])
    assert numbers(split) == ["1.0", "2.0", "3.0", "4.0", "5.0", "5.1"]
    assert sum(item.weight for item in split) == 100
    with pytest.raises(SplitProblem, match="can't be split"):
        split_category(items, [1], [Item("midterm", 15, None), Item("midterm", 15, None)])
    with pytest.raises(SplitProblem, match="add up to 9, but they must add up to 10"):
        split_category(items, [4], [Item("project", 4, None), Item("project", 5, None)])
    with pytest.raises(SplitProblem, match="1 to 10 parts"):
        split_category(items, [0], [Item("hw", 2, None)] * 10 + [Item("hw", 0, None)])


# Checks R17.
@pytest.mark.parametrize("typed, weight", [("10", 10), (" 2.5 ", Fraction(5, 2))])
def test_a_part_weight_is_a_number_above_0(typed, weight):
    assert parse_part_weight(typed) == weight
