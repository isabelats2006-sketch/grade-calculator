"""Logic for the grade calculator: reading a class file and working out the grade.

Kept apart from input/output (gradecalc.py) so it can be tested without typing.
All numbers are Fractions, not floats, so grade edges like 89.5% are exact.
"""

import math
import re
from collections import Counter
from dataclasses import dataclass, replace
from decimal import Decimal
from fractions import Fraction

# The first four names, in order. The first spelling is the one shown in error messages.
REQUIRED_NAMES = [
    ("homework", "hw", "assignments"),
    ("midterm",),
    ("final",),
    ("attendance",),
]

_NUMBER = re.compile(r"\d+(\.\d+)?")

# R17: these are always 2.0 and 3.0; every other category can have up to 10 parts (X.0-X.9).
UNSPLITTABLE = ("midterm", "final")
MAX_PARTS = 10

# R19: how a split category counts its parts. None (no line in the file) counts them all.
DROP_LOWEST = "drop lowest"
KEEP_HIGHEST = "keep highest"
RULES = (DROP_LOWEST, KEEP_HIGHEST)


@dataclass
class Item:
    """One grading item, such as homework: its weight and points earned (None = N/A).

    rule is DROP_LOWEST, KEEP_HIGHEST or None (count all parts, the standard). It belongs
    to the whole category, so every part of a split category has the same one (R19).
    """

    name: str
    weight: Fraction
    grade: Fraction | None
    rule: str | None = None


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


def _group_positions(names):
    """Positions of the names, grouped into categories: a name repeated side by side
    (capitals ignored) is one category in parts. ["hw", "HW", "midterm"] -> [[0, 1], [2]].
    """
    groups = []
    for position, name in enumerate(names):
        if groups and names[groups[-1][0]].lower() == name.lower():
            groups[-1].append(position)
        else:
            groups.append([position])
    return groups


# --- Categories and their numbers (spec.md section 15, R17) ---

def categories(items):
    """The items' positions grouped into categories, as in the file: [[0, 1], [2], ...]."""
    return _group_positions([item.name for item in items])


def is_split(items):
    """True if at least one category has 2 or more parts."""
    return any(len(group) > 1 for group in categories(items))


def _numbered(items):
    """(number, parts in its category) for each item: ("1.0", 2), ("1.1", 2), ("2.0", 1)."""
    found = []
    for number, group in enumerate(categories(items), start=1):
        found += [(f"{number}.{part}", len(group)) for part in range(len(group))]
    return found


def numbers(items):
    """Each item's number: "1.0", "1.1", "2.0", ... (category number . part)."""
    return [number for number, _ in _numbered(items)]


def labels(items):
    """How each item is named to the user: "homework 1.0" if it is a part, else "midterm"."""
    return [
        f"{item.name} {number}" if parts > 1 else item.name
        for item, (number, parts) in zip(items, _numbered(items))
    ]


class SplitProblem(Exception):
    """A split typed in the menu breaks a rule (spec.md section 15). The message says why."""


def splittable(items):
    """The categories that can be split: (category number, positions), midterm and final
    left out. [(1, [0]), (4, [3]), (5, [4, 5])] for hw, midterm, final, attendance, 2 projects.
    """
    return [
        (number, group)
        for number, group in enumerate(categories(items), start=1)
        if items[group[0]].name.lower() not in UNSPLITTABLE
    ]


def parse_part_weight(text):
    """Read one part's weight typed in the menu: a number above 0. Raises SplitProblem."""
    typed = text.strip()
    weight = _parse_number(typed)
    if weight is None:
        raise SplitProblem(f'I didn\'t understand "{typed}". Type a number above 0, like 10.')
    if weight == 0:
        raise SplitProblem("A part's weight must be above 0.")
    return weight


def split_category(items, group, parts):
    """Replace the category at these positions with these parts (Items). Returns new items.

    The parts must be 1 to 10, keep the category's name, and their weights must add up to
    the category's weight, so the weights still add up to 100. Raises SplitProblem.
    """
    name = items[group[0]].name
    if name.lower() in UNSPLITTABLE:
        raise SplitProblem(f"{name} can't be split into parts.")
    weight = sum((items[position].weight for position in group), Fraction(0))
    if weight == 0:
        raise SplitProblem(f"{name} is not in this class (weight 0), so it can't be split.")
    if not 1 <= len(parts) <= MAX_PARTS:
        raise SplitProblem(f"A category can have 1 to {MAX_PARTS} parts.")
    total = sum((part.weight for part in parts), Fraction(0))
    if total != weight:
        raise SplitProblem(
            f"The parts add up to {show_number(total)}, but they must add up to "
            f"{show_number(weight)}, the weight of {name}. Please type them again."
        )
    # The drop/keep choice (R19) stays with 2 or more parts; 1 part has nothing to drop.
    rule = items[group[0]].rule if len(parts) > 1 else None
    new_parts = [Item(name, p.weight, p.grade, rule) for p in parts]
    return items[:group[0]] + new_parts + items[group[-1] + 1:]


def with_rule(items, group, rule):
    """The items with this category counting its parts by rule (R19, spec.md section 17):
    DROP_LOWEST, KEEP_HIGHEST or None (count all). Raises SplitProblem if it isn't split.
    """
    if len(group) < 2:
        raise SplitProblem(f"{items[group[0]].name} is not split into parts, so no grade can be dropped.")
    changed = list(items)
    for position in group:
        changed[position] = replace(items[position], rule=rule)
    return changed


# --- Clearing all grades (spec.md section 18, R20) ---

def has_grades(items):
    """True if at least one item in the class has a grade (weight above 0, not N/A)."""
    return any(_is_out(item) for item in items)


def cleared(items):
    """The items with every grade N/A. Names, weights, splits and drop/keep choices stay."""
    return [replace(item, grade=None) for item in items]


def _read_rules(rule_lines, names, groups):
    """Read the lines after the 3 lines, like "homework: drop lowest" (R19).

    Returns ({category name in lowercase: rule}, [problems]).
    """
    rules, said_on, problems = {}, {}, []
    for line_number, text in rule_lines:
        name, colon, how = text.rpartition(":")
        name, how = name.strip(), " ".join(how.lower().split())
        if not colon or not name or how not in RULES:
            problems.append(
                f'Line {line_number}: "{text}" isn\'t understood. Write it like '
                '"homework: drop lowest" or "homework: keep highest".'
            )
            continue
        group = next((g for g in groups if names[g[0]].lower() == name.lower()), None)
        if group is None:
            problems.append(f'Line {line_number}: there is no category called "{name}" in line 1.')
        elif len(group) < 2:
            problems.append(
                f'Line {line_number}: "{names[group[0]]}" is not split into parts, so no grade '
                "can be dropped. Split it first or remove this line."
            )
        elif name.lower() in said_on:
            problems.append(
                f'Line {line_number}: "{names[group[0]]}" already has a line saying how to '
                f"count it (line {said_on[name.lower()]})."
            )
        else:
            said_on[name.lower()] = line_number
            rules[name.lower()] = how
    return rules, problems


def parse_class(text):
    """Read the text of a class file and return its list of Items.

    Raises FileProblems listing every problem found, each with its line number.
    """
    lines = [
        (number, _without_note(line))
        for number, line in enumerate(text.splitlines(), start=1)
        if _without_note(line)
    ]
    if len(lines) < 3:
        raise FileProblems([
            f"The file should have 3 lines (names, weights, grades), but it has {len(lines)}."
        ])

    problems = []
    (names_line, names_text), (weights_line, weights_text), (grades_line, grades_text) = lines[:3]

    # Line 1: names. A name repeated side by side is one category split into parts (R17),
    # so the name rules are checked on categories (spec.md section 15).
    names = [name.strip() for name in names_text.split("/")]
    if any(name == "" for name in names):
        problems.append(f"Line {names_line}: there is an empty name (two / with nothing between them).")
    groups = _group_positions(names)
    if len(groups) < len(REQUIRED_NAMES):
        problems.append(
            f"Line {names_line}: it needs at least homework / midterm / final / attendance, "
            f"but it has only {len(groups)} name(s)."
        )
    for position, allowed in enumerate(REQUIRED_NAMES):
        if position < len(groups) and names[groups[position][0]].lower() not in allowed:
            first = groups[position][0]
            problems.append(
                f"Line {names_line}: name {first + 1} should be {_quoted_names(allowed)}, "
                f'but it is "{names[first]}".'
            )
    places = Counter(names[group[0]].lower() for group in groups if names[group[0]])
    reported = set()
    for number, group in enumerate(groups, start=1):
        name = names[group[0]]
        if name.lower() in UNSPLITTABLE and len(group) > 1:
            problems.append(
                f'Line {names_line}: "{name}" is there {len(group)} times, '
                "but midterm and final can't be split into parts."
            )
        elif len(group) > MAX_PARTS:
            problems.append(
                f'Line {names_line}: "{name}" is split into {len(group)} parts, '
                f"but a category can have at most {MAX_PARTS} ({number}.0 to {number}.9)."
            )
        if places[name.lower()] > 1 and name.lower() not in reported:
            reported.add(name.lower())  # said once, even if it is in 3 places
            problems.append(
                f'Line {names_line}: "{name}" is in more than one place. '
                "The parts of a split category must be side by side."
            )

    # Lines 4 and after: how a split category counts its parts (R19, spec.md section 17).
    rules, rule_problems = _read_rules(lines[3:], names, groups)

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
            f"Line {weights_line}: the weights add up to {show_number(sum(weights))}, "
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
                    f"Line {grades_line}: grade {position} is {show_number(grade)}, but its weight is 0, "
                    "so the grade must be 0 or N/A."
                )
            elif grade > weight:
                problems.append(
                    f"Line {grades_line}: grade {position} is {show_number(grade)}, "
                    f"but it can't be more than its weight ({show_number(weight)})."
                )

    problems += rule_problems  # after the weights and grades, in line order
    if problems:
        raise FileProblems(problems)
    return [
        Item(name, weight, grade, rules.get(name.lower()))
        for name, weight, grade in zip(names, weights, grades)
    ]


class GradeProblem(Exception):
    """A grade typed in the menu breaks a rule. The message says why."""


def parse_grade(text, weight):
    """Read one grade typed in the menu: a number from 0 to the weight, or N/A (None).

    Same rules as line 3 of the class file (spec.md section 1). Raises GradeProblem.
    """
    typed = text.strip()
    if typed.lower() == "n/a":
        return None
    grade = _parse_number(typed)
    if grade is None:
        raise GradeProblem(
            f'I didn\'t understand "{typed}". Type a number from 0 to {show_number(weight)}, or N/A.'
        )
    if weight == 0 and grade != 0:
        raise GradeProblem("This item has weight 0, so its grade must be 0 or N/A.")
    if grade > weight:
        raise GradeProblem(f"The grade can't be more than its weight ({show_number(weight)}).")
    return grade


def show_number(number):
    """Show a Fraction exactly, the way a person would write it: 20, 27.5, 20.123456.

    Not float(...): that cuts to 6 digits, so 20.123456 would be saved as 20.1235.
    Numbers typed by the user always end. Points worked out with a dropped grade (R19)
    may not (35/3 = 11.666...), so those are shown with 2 decimals, .5 going up (11.67).
    """
    if number.denominator == 1:
        return str(number.numerator)
    rest = number.denominator
    for factor in (2, 5):  # a fraction ends in decimals only if 2 and 5 divide its denominator
        while rest % factor == 0:
            rest //= factor
    if rest != 1:
        return show_number(Fraction(math.floor(number * 100 + Fraction(1, 2)), 100))
    return str(Decimal(number.numerator) / Decimal(number.denominator))


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


def _is_out(item):
    """True if the item counts so far: weight above 0 and a grade (not N/A).

    The weight > 0 check is only a safety net: parse_class already makes a weight-0
    item's grade 0 or N/A, so it would add 0 out of 0 anyway.
    """
    return item.weight > 0 and item.grade is not None


def dropped(items):
    """Positions of the parts not counted because their category drops its lowest grade
    or keeps only its highest (R19, spec.md section 17).

    Only parts that are out can be dropped, and only when at least 2 are out. Lowest and
    highest are by the part's own %; on a tie, min and max pick the first part.
    """
    found = set()
    for group in categories(items):
        rule = items[group[0]].rule
        out = [position for position in group if _is_out(items[position])]
        if rule is None or len(out) < 2:
            continue

        def percent(position):
            return items[position].grade / items[position].weight

        if rule == DROP_LOWEST:
            found.add(min(out, key=percent))
        else:
            highest = max(out, key=percent)
            found.update(position for position in out if position != highest)
    return found


def current_grade(items):
    """The grade from the items that count so far, or None if no grades are out yet.

    An item counts if it is out (_is_out). A category that drops a grade (R19) keeps its
    weight so far: the parts out count as the kept parts' %, so with 8, 4 and 9 out of 10
    and 4 dropped, it is 17 out of 20 = 85% of 30 = 25.5 out of 30.
    """
    left_out = dropped(items)
    earned = out_of = Fraction(0)
    for group in categories(items):
        out = [items[position] for position in group if _is_out(items[position])]
        if not out:
            continue
        kept = [items[p] for p in group if _is_out(items[p]) and p not in left_out]
        weight = sum((item.weight for item in out), Fraction(0))
        kept_weight = sum((item.weight for item in kept), Fraction(0))
        earned += sum((item.grade for item in kept), Fraction(0)) * weight / kept_weight
        out_of += weight
    if out_of == 0:
        return None
    percent = earned / out_of * 100
    rounded = round_percent(percent)
    letter, gpa = letter_for(rounded)
    return Grade(earned, out_of, percent, rounded, letter, gpa)


def item_percent(item):
    """One item's own % (spec.md section 14), rounded like the grade, or None if it has
    no grade yet or weight 0 (not in this class).
    """
    if item.weight == 0 or item.grade is None:
        return None
    return round_percent(item.grade / item.weight * 100)


def average_gpa(gpas):
    """The plain average of these GPAs ("4.0", "3.7", ...) as text with 2 decimals, or None.

    Used for the GPA across all classes (spec.md section 13). Each class counts the same.
    Exact Fractions and .5 going up, as for the % (3.925 -> 3.93, where round() gives 3.92).
    """
    if not gpas:
        return None
    average = sum((Fraction(gpa) for gpa in gpas), Fraction(0)) / len(gpas)
    hundredths = math.floor(average * 100 + Fraction(1, 2))
    return f"{hundredths // 100}.{hundredths % 100:02d}"


# --- The goal and what is needed to reach it (spec.md section 4) ---

class GoalProblem(Exception):
    """What the user typed as a goal can't be understood. The message says why."""


@dataclass
class Goal:
    """A goal: the lowest rounded % that reaches it, and how to show it."""

    lowest: int  # the goal is reached when the rounded final % is at least this
    label: str  # "A- (3.7)" or "91%"
    with_article: str  # "an A-", "a B" or "91%", for sentences like "to get an A-"
    letter: str | None = None  # "A-" for a goal typed as a letter or GPA, None for a %


def _letter_goal(letter, gpa, lowest):
    article = "an" if letter[0] in "AF" else "a"
    return Goal(lowest, f"{letter} ({gpa})", f"{article} {letter}", letter)


def parse_goal(text):
    """Read a goal typed as a letter (A-), a GPA (3.7) or a percent (90% or 90).

    A number of 4 or less is a GPA; above 4 it is a percent. Raises GoalProblem.
    """
    typed = text.strip()
    if not typed:
        raise GoalProblem("Please type a goal, like A-, 3.7 or 90%.")

    for letter, gpa, lowest in SCALE:
        if typed.upper() == letter:
            return _letter_goal(letter, gpa, lowest)

    is_percent = typed.endswith("%")
    number = _parse_number(typed.rstrip("%").strip())
    if number is None:
        raise GoalProblem(
            f'I didn\'t understand "{typed}". Type a letter (A-), a GPA (3.7) or a percent (90%).'
        )

    if not is_percent and number <= 4:
        for letter, gpa, lowest in SCALE:
            if number == Fraction(gpa):
                return _letter_goal(letter, gpa, lowest)
        gpas = ", ".join(gpa for _, gpa, _ in SCALE)
        raise GoalProblem(f"{typed} isn't a GPA on the scale. The GPAs are: {gpas}.")

    if number > 100:
        raise GoalProblem("A goal can't be more than 100%.")
    shown = show_number(number)
    # A rounded % of at least ceil(number) reaches the goal (90.5% needs 91%).
    return Goal(math.ceil(number), f"{shown}%", f"{shown}%")


@dataclass
class Needed:
    """What it takes to reach the goal.

    kind is one of:
      "need"        -> percent is the % needed on every N/A item
      "already"     -> the goal is reached even with 0 on the rest
      "unreachable" -> even 100% on the rest is not enough; best_rounded is the best possible
      "done"        -> nothing is N/A any more; final is the final grade
    """

    kind: str
    remaining: list  # names of the N/A items
    percent: int | None = None
    best_rounded: int | None = None
    final: Grade | None = None


def needed_for(items, goal):
    """Work out the same % needed on every N/A item to reach the goal (spec.md section 4).

    The weights add up to 100, so the final grade is the points earned once every N/A
    item has a grade. Because of rounding, a final of goal - 0.5 is already enough.
    Which part is dropped (R19) depends on the grades the N/A items get, so instead of a
    formula, each whole % from 0 to 100 is tried and the first that reaches the goal is
    the one needed. Without drops this is the formula's answer rounded up.
    """
    remaining = [p for p, item in enumerate(items) if item.weight > 0 and item.grade is None]
    # "homework 1.1" for a part of a split category (R17), else just the name.
    names = [labels(items)[position] for position in remaining]
    if not remaining:
        return Needed("done", names, final=current_grade(items))

    def final_points(percent):
        """The points out of 100 if every N/A item gets this %."""
        filled = list(items)
        for position in remaining:
            filled[position] = replace(items[position], grade=items[position].weight * percent / 100)
        return current_grade(filled).earned

    enough = goal.lowest - Fraction(1, 2)
    if final_points(0) >= enough:
        return Needed("already", names)
    for percent in range(1, 101):
        if final_points(percent) >= enough:
            return Needed("need", names, percent=percent)
    return Needed("unreachable", names, best_rounded=round_percent(final_points(100)))


def _join_names(names):
    """'final', 'final and project', 'final, project and quizzes'."""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def describe_needed(needed, goal):
    """The sentence shown to the user about reaching the goal."""
    if needed.kind == "need":
        return (
            f"You need at least {needed.percent}% on {_join_names(needed.remaining)} "
            f"to get {goal.with_article}."
        )
    if needed.kind == "already":
        return f"You already have {goal.with_article} even if you get 0 on the rest."
    if needed.kind == "unreachable":
        letter, _ = letter_for(needed.best_rounded)
        start = goal.with_article[0].upper() + goal.with_article[1:]
        return (
            f"{start} is not reachable anymore, even with 100% on the rest. "
            f"The best you can get is {letter} ({needed.best_rounded}%)."
        )
    final = needed.final
    reached = "reached" if final.rounded >= goal.lowest else "did not reach"
    return f"Your final grade is {final.letter}. You {reached} your goal of {goal.label}."


# --- The grade scale (spec.md section 19, R21) ---

SCALE_TITLE = "GRADE SCALE (nearest whole %, so 93.5% is 94% = A)"


def _scale_rows():
    """(letter, GPA, lowest %, highest %) for each line of the scale, best first."""
    highest = [100] + [lowest - 1 for _, _, lowest in SCALE[:-1]]
    return [(letter, gpa, lowest, top) for (letter, gpa, lowest), top in zip(SCALE, highest)]


def scale_lines(here, goal):
    """The full scale, with "<- your goal" on the goal's line and "<- you are here (89%)"
    on the line of here (a rounded %, or None if no grade is out yet).
    """
    goal_letter, _ = letter_for(goal.lowest)
    here_letter = None if here is None else letter_for(here)[0]
    lines = [SCALE_TITLE]
    for letter, gpa, lowest, highest in _scale_rows():
        marks = []
        if letter == goal_letter:
            # A goal typed as a % may be inside a line (91% is in A-), so it says which.
            marks.append("your goal" if goal.letter else f"your goal ({goal.lowest}%)")
        if letter == here_letter:
            marks.append(f"you are here ({here}%)")
        line = f"{letter:<2} = {gpa} = {lowest} to {highest}%"
        lines.append(line + "   <- " + ", ".join(marks) if marks else line)
    return lines


def distance_text(here, goal):
    """The line under the scale: how far the rounded % here is from the goal."""
    if here is None:
        return "No grade is out yet, so you are not on the scale yet."
    if here >= goal.lowest:
        target = f"{goal.letter} ({goal.lowest}%)" if goal.letter else goal.label
        return f"You reached your goal of {target}."
    if goal.letter:
        return f"You are {goal.lowest - here}% from {goal.with_article} ({goal.lowest}%)."
    return f"You are {goal.lowest - here}% from your goal of {goal.label}."


def average_percent(percents):
    """The plain average of these rounded %s, to the nearest whole %, .5 going up, or None
    if there are none. Used for all classes together on the grade scale (R21).
    """
    if not percents:
        return None
    return round_percent(Fraction(sum(percents), len(percents)))
