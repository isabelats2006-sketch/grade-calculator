"""Logic for the grade calculator: reading a class file and working out the grade.

Kept apart from input/output (gradecalc.py) so it can be tested without typing.
All numbers are Fractions, not floats, so grade edges like 89.5% are exact.
"""

import math
import re
from dataclasses import dataclass
from fractions import Fraction

# The first four names, in order. The first spelling is the one shown in error messages.
REQUIRED_NAMES = [
    ("homework", "hw", "assignments"),
    ("midterm",),
    ("final",),
    ("attendance",),
]

_NUMBER = re.compile(r"\d+(\.\d+)?")


@dataclass
class Item:
    """One grading item, such as homework: its weight and points earned (None = N/A)."""

    name: str
    weight: Fraction
    grade: Fraction | None


class FileProblems(Exception):
    """The class file broke one or more rules. `problems` lists every one found."""

    def __init__(self, problems):
        super().__init__("\n".join(problems))
        self.problems = problems


def _without_note(line):
    """Drop anything after '=' (notes like '= total weight') and surrounding spaces."""
    return line.split("=", 1)[0].strip()


def _parse_number(text):
    """Return text as a Fraction if it is a plain number like 20 or 27.5, else None."""
    if _NUMBER.fullmatch(text):
        return Fraction(text)
    return None


def _quoted_names(allowed):
    """'"homework" (or "hw" or "assignments")' for error messages."""
    first = f'"{allowed[0]}"'
    if len(allowed) == 1:
        return first
    others = " or ".join(f'"{name}"' for name in allowed[1:])
    return f"{first} (or {others})"


def parse_class(text):
    """Read the text of a class file and return its list of Items.

    Raises FileProblems listing every problem found, each with its line number.
    """
    lines = [
        (number, _without_note(line))
        for number, line in enumerate(text.splitlines(), start=1)
        if _without_note(line)
    ]
    if len(lines) != 3:
        raise FileProblems([
            f"The file should have 3 lines (names, weights, grades), but it has {len(lines)}."
        ])

    problems = []
    (names_line, names_text), (weights_line, weights_text), (grades_line, grades_text) = lines

    # Line 1: names
    names = [name.strip() for name in names_text.split("/")]
    if any(name == "" for name in names):
        problems.append(f"Line {names_line}: there is an empty name (two / with nothing between them).")
    if len(names) < len(REQUIRED_NAMES):
        problems.append(
            f"Line {names_line}: it needs at least homework / midterm / final / attendance, "
            f"but it has only {len(names)} name(s)."
        )
    for position, allowed in enumerate(REQUIRED_NAMES):
        if position < len(names) and names[position].lower() not in allowed:
            problems.append(
                f"Line {names_line}: name {position + 1} should be {_quoted_names(allowed)}, "
                f'but it is "{names[position]}".'
            )

    # Lines 2 and 3 must have one value per name
    weight_texts = weights_text.split()
    grade_texts = grades_text.split()
    for line_number, what, values in (
        (weights_line, "weights", weight_texts),
        (grades_line, "grades", grade_texts),
    ):
        if len(values) != len(names):
            problems.append(
                f"Line {line_number}: there are {len(names)} names but {len(values)} {what}."
            )

    # Line 2: weights
    weights = []
    for position, text_value in enumerate(weight_texts, start=1):
        weight = _parse_number(text_value)
        if weight is None:
            problems.append(
                f'Line {weights_line}: weight {position} is "{text_value}", '
                "but a weight must be a number of 0 or more."
            )
        weights.append(weight)
    if weights and None not in weights and sum(weights) != 100:
        problems.append(
            f"Line {weights_line}: the weights add up to {_show(sum(weights))}, "
            "but they must add up to exactly 100."
        )

    # Line 3: grades
    grades = []
    for position, text_value in enumerate(grade_texts, start=1):
        if text_value.lower() == "n/a":
            grades.append(None)
            continue
        grade = _parse_number(text_value)
        grades.append(grade)
        if grade is None:
            problems.append(
                f'Line {grades_line}: grade {position} is "{text_value}", '
                "but a grade must be a number of 0 or more, or N/A."
            )
            continue
        if position <= len(weights) and weights[position - 1] is not None:
            weight = weights[position - 1]
            if weight == 0 and grade != 0:
                problems.append(
                    f"Line {grades_line}: grade {position} is {_show(grade)}, but its weight is 0, "
                    "so the grade must be 0 or N/A."
                )
            elif grade > weight:
                problems.append(
                    f"Line {grades_line}: grade {position} is {_show(grade)}, "
                    f"but it can't be more than its weight ({_show(weight)})."
                )

    if problems:
        raise FileProblems(problems)
    return [Item(name, weight, grade) for name, weight, grade in zip(names, weights, grades)]


def _show(number):
    """Show a Fraction the way a person would write it: 20, 27.5."""
    if number.denominator == 1:
        return str(number.numerator)
    return f"{float(number):g}"


# --- The current grade (spec.md section 3) ---

# (letter, GPA, lowest rounded %), from best to worst, exactly as in problem.md.
SCALE = [
    ("A", "4.0", 94),
    ("A-", "3.7", 90),
    ("B+", "3.3", 87),
    ("B", "3.0", 83),
    ("B-", "2.7", 80),
    ("C+", "2.3", 77),
    ("C", "2.0", 73),
    ("C-", "1.7", 70),
    ("D+", "1.3", 67),
    ("D", "1.0", 60),
    ("F", "0.0", 0),
]


@dataclass
class Grade:
    """A grade so far: points earned out of the counted weight, as % and letter."""

    earned: Fraction
    out_of: Fraction
    percent: Fraction  # exact, before rounding
    rounded: int  # nearest whole %, .5 goes up
    letter: str
    gpa: str


def round_percent(percent):
    """Round to the nearest whole %, with .5 going up (92.5 -> 93).

    Python's round() is not used: it sends .5 to the even number (round(92.5) == 92).
    """
    return math.floor(percent + Fraction(1, 2))


def letter_for(rounded):
    """The (letter, GPA) for a rounded % from 0 to 100."""
    for letter, gpa, lowest in SCALE:
        if rounded >= lowest:
            return letter, gpa
    raise ValueError(f"{rounded}% is below 0")


def current_grade(items):
    """The grade from the items that count so far, or None if no grades are out yet.

    An item counts if its weight is above 0 and its grade is not N/A.
    The weight > 0 check is only a safety net: parse_class already makes a weight-0
    item's grade 0 or N/A, so it would add 0 out of 0 anyway.
    """
    counted = [item for item in items if item.weight > 0 and item.grade is not None]
    out_of = sum((item.weight for item in counted), Fraction(0))
    if out_of == 0:
        return None
    earned = sum((item.grade for item in counted), Fraction(0))
    percent = earned / out_of * 100
    rounded = round_percent(percent)
    letter, gpa = letter_for(rounded)
    return Grade(earned, out_of, percent, rounded, letter, gpa)
