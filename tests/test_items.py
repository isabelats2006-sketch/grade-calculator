"""Tests for each item's own percentage under the table (spec.md section 14, R16)."""

from fractions import Fraction

import pytest

from gradecalc import screen, item_lines
from grades import Item, item_percent, parse_class, parse_goal
from test_cli import run

R16_EXAMPLE = (
    "homework / midterm / final / attendance\n"
    "20 30 40 10\n"
    "15 20 N/A 10\n"
)


def lines_for(text):
    items = parse_class(text)
    return item_lines(items, [item.name for item in items])


# Checks R16.
def test_the_list_matches_the_r16_example():
    items = parse_class(R16_EXAMPLE)
    shown = "\n".join(screen(items, "CSC 299", parse_goal("B")))
    assert (
        "homework / midterm / final / attendance\n"
        "20         30        40      10          = total weight\n"
        "15         20        N/A     10          = 45 out of 60 = 75% = C (2.0)\n"
        "-------------------- === --------------------\n"
        "homework:       15 out of 20 = 75%\n"
        "midterm:        20 out of 30 = 67%\n"
        "final:          N/A\n"
        "attendance:     10 out of 10 = 100%\n"
        "TOTAL:          45 out of 60 = 75%\n"
        "\n"
        "You need at least "
    ) in shown


# Checks R16, R9.
@pytest.mark.parametrize("grade, weight, percent", [
    ("20", "30", 67),  # 66.67 rounds up
    ("10", "30", 33),  # 33.33 rounds down
    ("1", "8", 13),  # 12.5: .5 goes up (round() would give 12)
    ("5", "8", 63),  # 62.5: .5 goes up (round() would give 62)
    ("17.9", "20", 90),  # 89.5 exactly, not 89.4999... as with floats
    ("0", "10", 0),
    ("10", "10", 100),
])
def test_an_items_percent_is_rounded_like_the_grade(grade, weight, percent):
    assert item_percent(Item("hw", Fraction(weight), Fraction(grade))) == percent


# Checks R16, R5.
def test_an_item_not_out_yet_has_no_percent():
    assert item_percent(Item("final", Fraction(40), None)) is None


# Checks R16, R4.
def test_an_item_with_weight_0_says_not_in_this_class():
    lines = lines_for(
        "homework / midterm / final / attendance\n"
        "20 30 50 0\n"
        "20 20 N/A 0\n"
    )
    assert lines == [
        "homework:       20 out of 20 = 100%",
        "midterm:        20 out of 30 = 67%",
        "final:          N/A",
        "attendance:     not in this class",
        "TOTAL:          40 out of 50 = 80%",
    ]


# Checks R16, R5.
def test_total_says_no_grades_out_yet_when_nothing_is_out():
    lines = lines_for(
        "homework / midterm / final / attendance\n"
        "20 30 40 10\n"
        "N/A N/A N/A N/A\n"
    )
    assert lines[-1] == "TOTAL:          no grades out yet"


# Checks R16.
def test_the_equals_signs_line_up_when_numbers_have_different_lengths():
    lines = lines_for(
        "homework / midterm / final / attendance\n"
        "10 30 50 10\n"
        "8 20 N/A 10\n"
    )
    assert lines[0] == "homework:       8 out of 10  = 80%"
    assert lines[1] == "midterm:        20 out of 30 = 67%"
    assert len({line.index("=") for line in lines if "=" in line}) == 1


# Checks R16.
def test_a_long_name_makes_the_label_column_wider():
    lines = lines_for(
        "homework / midterm / final / attendance / group presentation\n"
        "20 30 30 10 10\n"
        "15 20 N/A 10 9\n"
    )
    assert lines[4] == "group presentation:   9 out of 10  = 90%"
    assert lines[0] == "homework:             15 out of 20 = 75%"
    assert lines[-1] == "TOTAL:                54 out of 70 = 77%"


# Checks R16, R15.
def test_what_if_shows_the_list_with_the_tried_grade(tmp_path):
    path = tmp_path / "csc299.txt"
    path.write_text(R16_EXAMPLE, encoding="utf-8")
    # what if final = 30 out of 40, then leave, then quit
    _, printed, _ = run([str(path)], ["CSC 299", "B", "5", "1", "3", "30", "2", "q"],
                        tmp_path / "saved")
    what_if_part = printed.split("WHAT IF: nothing here is saved")[-1]
    assert "final:          30 out of 40  = 75%\n" in what_if_part
    assert "TOTAL:          75 out of 100 = 75%\n" in what_if_part
    after_leaving = printed.split("Left what-if mode.")[-1]
    assert "final:          N/A\n" in after_leaving
