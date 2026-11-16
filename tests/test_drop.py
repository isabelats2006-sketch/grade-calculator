"""Tests for dropping the lowest grade or keeping only the highest (spec.md section 17, R19)."""

from fractions import Fraction

import pytest

from gradecalc import gpa_across_classes, screen
from grades import (
    DROP_LOWEST, KEEP_HIGHEST, Item, SplitProblem, current_grade, describe_needed, dropped,
    needed_for, parse_class, parse_goal, show_number, split_category, with_rule,
)
from storage import class_to_text, load_class, save_class
from test_cli import run
from test_parse import problems_for

R19_TABLE = (
    "homework / homework / homework / midterm / final / attendance\n"
    "10 10 10 30 30 10\n"
    "8 4 9 N/A N/A 10\n"
)
R19_EXAMPLE = R19_TABLE + "homework: drop lowest\n"


def with_grades(homework, rule="homework: drop lowest"):
    """The R19 example with these three homework grades (like "8 4 N/A") and this line."""
    return R19_TABLE.replace("8 4 9", homework) + rule + "\n"


# --- Reading the choice from the file ---

# Checks R19.
def test_a_drop_lowest_line_is_read_for_every_part_of_the_category():
    items = parse_class(R19_EXAMPLE)
    assert [item.rule for item in items] == [DROP_LOWEST] * 3 + [None] * 3


# Checks R19.
def test_the_standard_is_to_count_every_part():
    items = parse_class(R19_TABLE)
    assert [item.rule for item in items] == [None] * 6
    assert dropped(items) == set()
    assert current_grade(items).earned == 31  # 8 + 4 + 9 + 10: nothing dropped


# Checks R19.
def test_keep_highest_is_read_with_capitals_and_spaces_ignored():
    items = parse_class(with_grades("8 4 9", "Homework :  Keep   Highest"))
    assert [item.rule for item in items[:3]] == [KEEP_HIGHEST] * 3


# Checks R19, R8.
@pytest.mark.parametrize("line, problem", [
    ("projet: drop lowest", 'Line 4: there is no category called "projet" in line 1.'),
    ("midterm: drop lowest",
     'Line 4: "midterm" is not split into parts, so no grade can be dropped. '
     "Split it first or remove this line."),
    ("homework: drop highest",
     'Line 4: "homework: drop highest" isn\'t understood. '
     'Write it like "homework: drop lowest" or "homework: keep highest".'),
    ("drop lowest",
     'Line 4: "drop lowest" isn\'t understood. '
     'Write it like "homework: drop lowest" or "homework: keep highest".'),
])
def test_a_wrong_line_after_the_three_is_explained(line, problem):
    assert problems_for(R19_TABLE + line + "\n") == [problem]


# Checks R19, R8.
def test_a_category_with_two_lines_is_a_file_problem():
    text = R19_EXAMPLE + "homework: keep highest\n"
    assert problems_for(text) == [
        'Line 5: "homework" already has a line saying how to count it (line 4).'
    ]


# Checks R19, R10.
def test_the_choice_is_saved_and_loaded_with_the_class(tmp_path):
    items = parse_class(R19_EXAMPLE)
    assert class_to_text(items).splitlines()[3] == "homework: drop lowest"
    save_class(tmp_path, "CSC 299", items)
    assert load_class(tmp_path, "CSC 299") == items


# Checks R19, R10.
def test_a_class_without_a_choice_is_still_saved_as_three_lines():
    assert len(class_to_text(parse_class(R19_TABLE)).splitlines()) == 3


# --- Counting ---

# Checks R19, R3.
def test_drop_lowest_keeps_the_category_weight_as_in_the_spec_example():
    items = parse_class(R19_EXAMPLE)
    assert dropped(items) == {1}  # homework 1.1, 4 out of 10
    grade = current_grade(items)
    # homework: 17 out of 20 = 85% of 30 = 25.5, plus attendance 10 out of 10
    assert (grade.earned, grade.out_of, grade.rounded, grade.letter) == (
        Fraction("35.5"), 40, 89, "B+")


# Checks R19.
def test_keep_highest_counts_only_the_best_part():
    items = parse_class(with_grades("8 4 9", "homework: keep highest"))
    assert dropped(items) == {0, 1}
    grade = current_grade(items)
    assert (grade.earned, grade.out_of, grade.rounded) == (37, 40, 93)  # 90% of 30 + 10


# Checks R19.
def test_the_lowest_is_by_percent_not_by_points():
    items = parse_class(
        "homework / homework / midterm / final / attendance\n"
        "5 10 35 40 10\n"
        "4 6 N/A N/A N/A\n"
        "homework: drop lowest\n"
    )
    assert dropped(items) == {1}  # 6 out of 10 = 60% is lower than 4 out of 5 = 80%
    assert current_grade(items).earned == 12  # 80% of 15


# Checks R19.
def test_a_part_not_out_yet_is_never_dropped():
    items = parse_class(with_grades("8 4 N/A"))
    assert dropped(items) == {1}
    grade = current_grade(items)
    assert (grade.earned, grade.out_of) == (26, 30)  # homework 80% of 20 = 16, plus 10


# Checks R19.
def test_nothing_is_dropped_until_two_parts_are_out():
    items = parse_class(with_grades("4 N/A N/A"))
    assert dropped(items) == set()
    assert current_grade(items).earned == 14


# Checks R19.
@pytest.mark.parametrize("rule, homework, expected", [
    ("homework: drop lowest", "5 5 9", {0}),
    ("homework: keep highest", "9 9 4", {1, 2}),
])
def test_on_a_tie_the_first_part_is_the_one_dropped_or_kept(rule, homework, expected):
    assert dropped(parse_class(with_grades(homework, rule))) == expected


# Checks R19, R6.
def test_you_need_takes_the_drop_into_account():
    goal = parse_goal("B")
    needed = needed_for(parse_class(R19_EXAMPLE), goal)
    assert describe_needed(needed, goal) == "You need at least 79% on midterm and final to get a B."


# Checks R19, R6.
def test_you_need_works_out_the_drop_again_for_an_na_part():
    # With X% on homework 1.2, midterm and final, 4 out of 10 is dropped:
    # 30 x (8 + X/10) / 20 + 10 + 60 x X/100 >= 82.5 gives X >= 80.67, so 81%.
    # Counting all parts it would be 87%.
    goal = parse_goal("B")
    assert needed_for(parse_class(with_grades("8 4 N/A")), goal).percent == 81
    assert needed_for(parse_class(with_grades("8 4 N/A", "")), goal).percent == 87


# Checks R19, R6.
def test_the_best_grade_still_possible_counts_the_drop():
    items = parse_class(
        "homework / homework / midterm / final / attendance\n"
        "10 10 30 40 10\n"
        "0 10 0 N/A 0\n"
        "homework: drop lowest\n"
    )
    needed = needed_for(items, parse_goal("A"))
    assert (needed.kind, needed.best_rounded) == ("unreachable", 60)  # 20 + 40 out of 100


# --- Changing the choice and splitting ---

# Checks R19.
def test_with_rule_changes_every_part_and_back_to_count_all():
    items = parse_class(R19_TABLE)
    changed = with_rule(items, [0, 1, 2], KEEP_HIGHEST)
    assert [item.rule for item in changed] == [KEEP_HIGHEST] * 3 + [None] * 3
    assert [item.rule for item in with_rule(changed, [0, 1, 2], None)] == [None] * 6
    assert items == parse_class(R19_TABLE)  # a new list; the old one is unchanged


# Checks R19.
def test_a_category_that_is_not_split_cant_drop_a_grade():
    with pytest.raises(SplitProblem, match="not split into parts"):
        with_rule(parse_class(R19_TABLE), [5], DROP_LOWEST)


# Checks R19, R17.
def test_splitting_again_keeps_the_choice_and_joining_removes_it():
    items = parse_class(R19_EXAMPLE)
    parts = [Item("homework", 15, None), Item("homework", 15, 10)]
    assert [i.rule for i in split_category(items, [0, 1, 2], parts)[:2]] == [DROP_LOWEST] * 2
    joined = split_category(items, [0, 1, 2], [Item("homework", 30, 20)])
    assert joined[0].rule is None


# Checks R19.
@pytest.mark.parametrize("number, shown", [
    (Fraction(35, 3), "11.67"),
    (Fraction(2, 3), "0.67"),
    (Fraction(1, 6), "0.17"),  # 0.1666...: rounds up
    (Fraction(1, 8), "0.125"),  # ends, so it is shown exactly, as before
    (Fraction(91, 3), "30.33"),
])
def test_points_that_dont_end_are_shown_with_2_decimals(number, shown):
    assert show_number(number) == shown


# --- The screen ---

# Checks R19, R16, R17.
def test_the_screen_matches_the_spec_example():
    assert screen(parse_class(R19_EXAMPLE), "CSC 299", parse_goal("B")) == [
        "CSC 299",
        "GOAL = B (3.0) // CURRENT GRADE = B+ (3.3), 89%",
        "",
        "1.0        1.1        1.2        2.0       3.0     4.0",
        "homework / homework / homework / midterm / final / attendance",
        "10         10         10         30        30      10          = total weight",
        "8          4          9          N/A       N/A     10          "
        "= 35.5 out of 40 = 89% = B+ (3.3)",
        "-------------------- === --------------------",
        "homework 1.0:   8 out of 10    = 80%",
        "homework 1.1:   4 out of 10    = 40%   (dropped)",
        "homework 1.2:   9 out of 10    = 90%",
        "midterm:        N/A",
        "final:          N/A",
        "attendance:     10 out of 10   = 100%",
        "TOTAL:          35.5 out of 40 = 89%",
        "homework drops its lowest grade.",
        "",
        "You need at least 79% on midterm and final to get a B.",
    ]


# Checks R19, R16.
def test_keep_highest_marks_every_other_part_as_dropped():
    lines = screen(parse_class(with_grades("8 4 9", "homework: keep highest")), "C", parse_goal("B"))
    assert [line for line in lines if "(dropped)" in line] == [
        "homework 1.0:   8 out of 10  = 80%   (dropped)",
        "homework 1.1:   4 out of 10  = 40%   (dropped)",
    ]
    assert "homework keeps only its highest grade." in lines


# Checks R19.
def test_the_choice_is_shown_before_any_part_is_dropped():
    lines = screen(parse_class(with_grades("N/A N/A N/A")), "C", parse_goal("B"))
    assert not any("(dropped)" in line for line in lines)
    assert "homework drops its lowest grade." in lines


# Checks R19, R16.
def test_without_a_choice_nothing_is_marked_and_no_line_is_added():
    lines = screen(parse_class(R19_TABLE), "C", parse_goal("B"))
    assert not any("(dropped)" in line or "grade." in line for line in lines)


# Checks R19, R15.
def test_what_if_works_out_the_drop_with_the_tried_grades(tmp_path):
    path = tmp_path / "csc299.txt"
    path.write_text(R19_EXAMPLE, encoding="utf-8")
    # What if, try homework 1.1 = 10: now 8 out of 10 (homework 1.0) is the lowest.
    _, printed, _ = run([str(path)], ["CSC 299", "B", "5", "1", "2", "10", "q"], tmp_path / "saved")
    tried = printed.split("WHAT IF: nothing here is saved")[2]
    assert "homework 1.0:   8 out of 10    = 80%   (dropped)" in tried
    assert "homework 1.1:   10 out of 10   = 100%" in tried
    assert load_class(tmp_path / "saved", "CSC 299") == parse_class(R19_EXAMPLE)  # not saved


# Checks R19, R17.
def test_changing_a_grade_keeps_the_choice(tmp_path):
    path = tmp_path / "csc299.txt"
    path.write_text(R19_EXAMPLE, encoding="utf-8")
    # homework 1.0, the first part: the saved line is written from it.
    run([str(path)], ["CSC 299", "B", "1", "1", "7", "q"], tmp_path / "saved")
    items = load_class(tmp_path / "saved", "CSC 299")
    assert items[0] == Item("homework", 10, 7, DROP_LOWEST)
    assert [item.rule for item in items[:3]] == [DROP_LOWEST] * 3


# Checks R19, R14.
def test_the_gpa_across_classes_counts_the_drop(tmp_path):
    save_class(tmp_path, "CSC 299", parse_class(R19_EXAMPLE))
    save_class(tmp_path, "MATH 101", parse_class(R19_TABLE))
    assert gpa_across_classes(tmp_path, ["CSC 299", "MATH 101"]) == [
        "GPA across all your classes: 2.80 (average of 2 classes)",
        "  CSC 299: B+ (3.3), 89%",
        "  MATH 101: C+ (2.3), 78%",
    ]
