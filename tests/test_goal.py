"""Tests for reading the goal and the % needed to reach it (spec.md section 4)."""

from fractions import Fraction

import pytest

from grades import (
    GoalProblem, Item, current_grade, describe_needed, needed_for, parse_class, parse_goal,
)

# The example on screen in spec.md section 5: 55 out of 70 so far, final and project N/A.
SPEC_EXAMPLE = (
    "homework / midterm / final / attendance / project\n"
    "30 30 20 10 10\n"
    "20 25 N/A 10 N/A\n"
)


# --- Reading the goal ---

@pytest.mark.parametrize(
    "typed, lowest, label",
    [
        ("A-", 90, "A- (3.7)"), ("a-", 90, "A- (3.7)"), ("  b+ ", 87, "B+ (3.3)"),
        ("A", 94, "A (4.0)"), ("F", 0, "F (0.0)"),
        ("3.7", 90, "A- (3.7)"), ("4", 94, "A (4.0)"), ("3.70", 90, "A- (3.7)"),
        ("0", 0, "F (0.0)"),
        ("90%", 90, "90%"), ("90", 90, "90%"), ("90.5%", 91, "90.5%"), ("4%", 4, "4%"),
        ("100%", 100, "100%"),
    ],
)
def test_goal_can_be_a_letter_a_gpa_or_a_percent(typed, lowest, label):
    goal = parse_goal(typed)
    assert (goal.lowest, goal.label) == (lowest, label)


@pytest.mark.parametrize(
    "typed, message",
    [
        ("", "Please type a goal, like A-, 3.7 or 90%."),
        ("pass", 'I didn\'t understand "pass". Type a letter (A-), a GPA (3.7) or a percent (90%).'),
        ("A+", 'I didn\'t understand "A+". Type a letter (A-), a GPA (3.7) or a percent (90%).'),
        ("-5", 'I didn\'t understand "-5". Type a letter (A-), a GPA (3.7) or a percent (90%).'),
        ("3.5", "3.5 isn't a GPA on the scale. The GPAs are: "
                "4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.7, 1.3, 1.0, 0.0."),
        ("150%", "A goal can't be more than 100%."),
    ],
)
def test_a_goal_that_cant_be_understood_is_explained(typed, message):
    with pytest.raises(GoalProblem) as caught:
        parse_goal(typed)
    assert str(caught.value) == message


# --- What is needed: the examples from spec.md ---

def test_spec_example_needs_92_percent_for_a_b():
    items = parse_class(SPEC_EXAMPLE)
    goal = parse_goal("B")
    needed = needed_for(items, goal)
    assert (needed.kind, needed.percent) == ("need", 92)
    assert describe_needed(needed, goal) == "You need at least 92% on final and project to get a B."


def test_spec_example_a_minus_is_not_reachable_and_shows_best_possible():
    items = parse_class(SPEC_EXAMPLE)
    goal = parse_goal("A-")
    needed = needed_for(items, goal)
    assert (needed.kind, needed.best_rounded) == ("unreachable", 85)
    assert describe_needed(needed, goal) == (
        "An A- is not reachable anymore, even with 100% on the rest. "
        "The best you can get is B (85%)."
    )


def test_goal_already_reached_even_with_zero_on_the_rest():
    items = parse_class("hw / midterm / final / attendance\n30 30 30 10\n30 30 N/A 10\n")
    goal = parse_goal("C-")  # 70 out of 100 already, final N/A
    needed = needed_for(items, goal)
    assert needed.kind == "already"
    assert describe_needed(needed, goal) == "You already have a C- even if you get 0 on the rest."


def test_one_na_item_is_named_alone():
    items = parse_class("hw / midterm / final / attendance\n30 30 30 10\n30 30 N/A 10\n")
    goal = parse_goal("A")
    # 70 so far + 79% of 30 = 93.7%, which rounds to 94% (A). 78% gives 93.4% -> 93% (A-).
    assert describe_needed(needed_for(items, goal), goal) == (
        "You need at least 79% on final to get an A."
    )


def test_three_na_items_are_listed_with_commas():
    text = "hw / midterm / final / attendance / project\n20 20 20 20 20\n20 N/A N/A 20 N/A\n"
    goal = parse_goal("B")
    assert describe_needed(needed_for(parse_class(text), goal), goal) == (
        "You need at least 71% on midterm, final and project to get a B."
    )


def test_percent_goal_reads_without_article():
    items = parse_class(SPEC_EXAMPLE)
    goal = parse_goal("80%")
    assert describe_needed(needed_for(items, goal), goal) == (
        "You need at least 82% on final and project to get 80%."
    )


@pytest.mark.parametrize("goal_text, reached", [("C-", "reached"), ("B", "did not reach")])
def test_nothing_left_says_final_grade_and_if_the_goal_was_reached(goal_text, reached):
    items = parse_class("hw / midterm / final / attendance\n30 30 30 10\n20 20 20 10\n")
    goal = parse_goal(goal_text)
    needed = needed_for(items, goal)
    assert needed.kind == "done"
    assert describe_needed(needed, goal) == (
        f"Your final grade is C-. You {reached} your goal of {goal.label}."
    )


def test_zero_weight_na_item_is_not_counted_as_remaining():
    items = parse_class("hw / midterm / final / attendance\n40 30 30 0\n30 25 N/A N/A\n")
    assert needed_for(items, parse_goal("B")).remaining == ["final"]


# --- The answer is really right, checked by filling in the N/A items ---

def final_if_everyone_scores(items, percent):
    """The final rounded % if every N/A item gets this % of its weight."""
    filled = [
        Item(i.name, i.weight, i.weight * Fraction(percent, 100) if i.grade is None else i.grade)
        for i in items
    ]
    return current_grade(filled).rounded


@pytest.mark.parametrize("goal_text", ["A", "A-", "B+", "B", "B-", "C+", "C", "D", "F", "88%", "90.5%"])
@pytest.mark.parametrize(
    "text",
    [
        SPEC_EXAMPLE,
        "hw / midterm / final / attendance\n30 30 30 10\n24.5 N/A N/A 7\n",
        "hw / midterm / final / attendance\n25 25 40 10\n17.9 21 N/A 10\n",
        "hw / midterm / final / attendance\n30 30 30 10\n30 30 N/A 10\n",
    ],
)
def test_every_answer_is_checked_by_filling_in_the_na_items(text, goal_text):
    items = parse_class(text)
    goal = parse_goal(goal_text)
    needed = needed_for(items, goal)
    if needed.kind == "need":
        # The needed % reaches the goal, and 1% less does not: it is the smallest.
        assert final_if_everyone_scores(items, needed.percent) >= goal.lowest
        assert final_if_everyone_scores(items, needed.percent - 1) < goal.lowest
    elif needed.kind == "already":
        assert final_if_everyone_scores(items, 0) >= goal.lowest
    else:
        assert needed.kind == "unreachable"
        assert final_if_everyone_scores(items, 100) < goal.lowest
        assert needed.best_rounded == final_if_everyone_scores(items, 100)
