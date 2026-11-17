"""Grade calculator: the program you run (spec.md sections 2, 5, 6, 7 and 9 to 13).

    python gradecalc.py csc299.txt     open a class file (first time)
    python gradecalc.py                pick one of your saved classes

All the questions and printing happen here; the math is in grades.py and saving is in
storage.py. `ask` and `say` are passed in so tests can type answers and read the screen.
"""

import sys
from dataclasses import replace
from pathlib import Path

from grades import (
    DROP_LOWEST, KEEP_HIGHEST, FileProblems, GoalProblem, GradeProblem, Item, average_gpa,
    average_percent, distance_text, scale_lines,
    categories, cleared, current_grade, dropped, has_grades,
    MAX_PARTS, SplitProblem, describe_needed, is_split, item_percent, labels, needed_for, numbers,
    parse_class, parse_goal, parse_grade, parse_part_weight, show_number, split_category,
    splittable, with_rule,
)
from storage import (
    NameProblem, aligned_row, check_name, class_to_text, delete_class, find_class, list_classes, load_class,
    rename_class, save_class,
)

SAVED_CLASSES = Path(__file__).parent / "saved_classes"

USAGE = (
    "How to run it:\n"
    "  python gradecalc.py csc299.txt     open a class file\n"
    "  python gradecalc.py                pick one of your saved classes\n"
    'If the file name has spaces, put it in quotes: python gradecalc.py "my class.txt"'
)


class Quit(Exception):
    """The user chose to quit (typed q, or closed the input)."""


def main(args, ask=input, say=print, folder=SAVED_CLASSES):
    """Run the program. Returns the exit code: 0 if all went well, 1 if not."""
    try:
        if len(args) > 1:
            say("Please give at most one class file.")
            say(USAGE)
            return 1
        if args:
            items, name = open_class_file(args[0], ask, say, folder)
        else:
            picked = pick_saved_class(ask, say, folder)
            if picked is None:
                return 0
            items, name = picked
        while True:
            goal = ask_goal(ask, say)
            run_menu(items, name, goal, ask, say, folder)
            # run_menu only returns when the open class was deleted: back to the list.
            picked = pick_saved_class(ask, say, folder)
            if picked is None:
                break
            items, name = picked
    except (Quit, EOFError, KeyboardInterrupt):
        say("")
    say("Bye!")
    return 0


def _ask(ask, question):
    """Ask a question. Typing q quits."""
    answer = ask(question)
    if answer.strip().lower() == "q":
        raise Quit
    return answer


def _ask_number(ask, say, count, question):
    """Ask for a number from 1 to count until one is typed. Returns it as an int."""
    while True:
        typed = _ask(ask, question).strip()
        if typed.isdigit() and 1 <= int(typed) <= count:
            return int(typed)
        say(f"Please type a number from 1 to {count}.")


# --- Getting the class ---

def read_class_file(path):
    """Read and check a class file. Returns (items, None) or (None, explanation lines)."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, [f'There is no file called "{path}".']
    except (OSError, UnicodeDecodeError) as error:
        return None, [f'"{path}" can\'t be read as a text file ({error.__class__.__name__}).']
    try:
        return parse_class(text), None
    except FileProblems as problems:
        return None, [f"There are problems with {path}:"] + [f"  - {p}" for p in problems.problems]


def open_class_file(path, ask, say, folder):
    """Read the class file (asking for another one until it works), then save it by name."""
    while True:
        items, explanation = read_class_file(path)
        if items is not None:
            break
        for line in explanation:
            say(line)
        say("Please fix the file or use a different one.")
        path = _ask(ask, "Type another file path, or q to quit: ").strip().strip('"')
    name = ask_class_name(Path(path).stem, ask, say, folder)
    save_class(folder, name, items)
    say(f'Saved as "{name}". Next time, just run: python gradecalc.py')
    return items, name


def ask_class_name(suggestion, ask, say, folder):
    """Ask what to call the class. Asks before replacing a class with the same name."""
    while True:
        typed = _ask(ask, f"What should this class be called? (press Enter for {suggestion}): ")
        try:
            name = check_name(typed or suggestion)
        except NameProblem as problem:
            say(str(problem))
            continue
        existing = find_class(folder, name)
        if existing is None:
            return name
        answer = _ask(ask, f'There is already a saved class called "{existing}". Replace it? (y/n): ')
        if answer.strip().lower() in ("y", "yes"):
            return name
        say("OK, pick another name.")


def gpa_across_classes(folder, names):
    """The lines shown above the saved-class list: each class's GPA and their average
    (spec.md section 13). Classes with no grades yet, or that can't be read, are not counted.
    """
    gpas, lines = [], []
    for name in names:
        try:
            grade = current_grade(load_class(folder, name))
        except (FileProblems, OSError, UnicodeDecodeError):
            lines.append(f"  {name}: can't be read, not counted")
            continue
        if grade is None:
            lines.append(f"  {name}: no grades out yet, not counted")
        else:
            gpas.append(grade.gpa)
            lines.append(f"  {name}: {grade.letter} ({grade.gpa}), {grade.rounded}%")
    average = average_gpa(gpas)
    if average is None:
        first = "GPA across all your classes: no grades out yet"
    else:
        classes = "class" if len(gpas) == 1 else "classes"
        first = f"GPA across all your classes: {average} (average of {len(gpas)} {classes})"
    return [first] + lines


def pick_saved_class(ask, say, folder):
    """List the saved classes and let the user pick one, rename one or delete one.

    Returns (items, name) for the class picked, or None if there are no classes (left).
    """
    while True:
        names = list_classes(folder)
        if not names:
            say("You have no saved classes yet. Start with a class file, for example:")
            say("  python gradecalc.py csc299.txt")
            return None
        if len(names) >= 2:
            for line in gpa_across_classes(folder, names):
                say(line)
            say("")
        say("Your saved classes:")
        for number, name in enumerate(names, start=1):
            say(f"  {number}) {name}")
        while True:
            typed = _ask(ask, "Pick a class by number, r to rename, d to delete, or q to quit: ")
            typed = typed.strip().lower()
            if typed in ("r", "d") or (typed.isdigit() and 1 <= int(typed) <= len(names)):
                break
            say(f"Please type a number from 1 to {len(names)}.")
        if typed.isdigit():
            break
        name = names[_ask_number(ask, say, len(names), "Which class? (number): ") - 1]
        if typed == "r":
            ask_rename(name, ask, say, folder)
        else:
            ask_delete(name, ask, say, folder)
        say("")
    name = names[int(typed) - 1]
    try:
        return load_class(folder, name), name
    except FileProblems as problems:
        say(f'The saved class "{name}" has problems:')
        for problem in problems.problems:
            say(f"  - {problem}")
        say(f"Please fix the file {Path(folder) / (name + '.txt')} and run the program again.")
        raise Quit


# --- The goal, the screen and the menu ---

def ask_goal(ask, say):
    """Ask for the goal until it can be understood."""
    while True:
        try:
            return parse_goal(_ask(ask, "What is your goal? (like A-, 3.7 or 90%): "))
        except GoalProblem as problem:
            say(str(problem))


def screen(items, name, goal):
    """The lines shown for a class (spec.md section 5)."""
    grade = current_grade(items)
    if grade is None:
        now = "no grades out yet"
        summary = "no grades out yet"
    else:
        now = f"{grade.letter} ({grade.gpa}), {grade.rounded}%"
        summary = (
            f"{show_number(grade.earned)} out of {show_number(grade.out_of)} = "
            f"{grade.rounded}% = {grade.letter} ({grade.gpa})"
        )
    names_row, weights_row, grades_row = class_to_text(items).splitlines()[:3]
    width = max(len(names_row), len(weights_row), len(grades_row)) + 2
    # R17: the numbers row (1.0 1.1 2.0 ...) only when a category is split.
    numbers_row = [aligned_row(items, numbers(items))] if is_split(items) else []
    return [
        name,
        f"GOAL = {goal.label} // CURRENT GRADE = {now}",
        "",
        *numbers_row,
        names_row,
        weights_row.ljust(width) + "= total weight",
        grades_row.ljust(width) + "= " + summary,
        SEPARATOR,
        *item_lines(items, labels(items)),
        "",
        describe_needed(needed_for(items, goal), goal),
    ]


SEPARATOR = "-------------------- === --------------------"


def item_lines(items, labels):
    """Each item's own %, then TOTAL (spec.md section 14). labels are the names shown.

    A part not counted (R19) has "   (dropped)" after its %, and each category that drops
    or keeps a grade has a line under TOTAL saying so (spec.md section 17).
    """
    left_out = dropped(items)
    rows = []  # (label, "15 out of 20" or None, what comes after it)
    for position, (item, label) in enumerate(zip(items, labels)):
        if item.weight == 0:
            rows.append((label, None, "not in this class"))
        elif item.grade is None:
            rows.append((label, None, "N/A"))
        else:
            out_of = f"{show_number(item.grade)} out of {show_number(item.weight)}"
            mark = "   (dropped)" if position in left_out else ""
            rows.append((label, out_of, f"{item_percent(item)}%{mark}"))
    grade = current_grade(items)
    if grade is None:
        rows.append(("TOTAL", None, "no grades out yet"))
    else:
        out_of = f"{show_number(grade.earned)} out of {show_number(grade.out_of)}"
        rows.append(("TOTAL", out_of, f"{grade.rounded}%"))
    # Labels padded to at least 16, as in the R16 example; the = signs line up.
    label_width = max(16, max(len(label) + 1 for label, _, _ in rows) + 3)
    out_of_width = max((len(out_of) for _, out_of, _ in rows if out_of), default=0)
    lines = []
    for label, out_of, value in rows:
        start = f"{label}:".ljust(label_width)
        if out_of is None:
            lines.append(start + value)
        else:
            lines.append(start + out_of.ljust(out_of_width) + " = " + value)
    return lines + [
        f"{items[group[0]].name} {RULE_TEXT[items[group[0]].rule]}."
        for group in categories(items) if items[group[0]].rule is not None
    ]


# How each R19 choice is described: under TOTAL, in the menu and in the history.
RULE_TEXT = {DROP_LOWEST: "drops its lowest grade", KEEP_HIGHEST: "keeps only its highest grade"}


MENU = [
    "", "1) Change a grade", "2) Change the goal", "3) Rename this class", "4) Delete this class",
    "5) What if (try grades without saving)", "6) Split a category",
    "7) Drop the lowest or keep the highest grade",
    "8) History (see this session's changes and go back)", "9) Clear all grades",
    "10) See the grade scale", "11) Quit",
]


def run_menu(items, name, goal, ask, say, folder):
    """Show the result and the menu until the user quits (raises Quit).

    Returns only if the class was deleted, so the caller can go back to the saved-class list.
    The history (R18) lives only here, in memory: it starts empty each time a class is
    opened and is lost when the program closes.
    """
    history = []  # (what changed, the items just before it), oldest first

    def remember(text, before, after):
        if after != before:  # a change that leaves everything as it was is not added
            history.append((text, before))

    while True:
        for line in screen(items, name, goal) + MENU:
            say(line)
        choice = _ask(ask, "Choose 1 to 11: ").strip()
        if choice == "1":
            changed = change_a_grade(items, ask, say)
            remember(grade_change_text(items, changed), items, changed)
            items = changed
            save_class(folder, name, items)
            say("Saved.")
        elif choice == "2":
            goal = ask_goal(ask, say)
        elif choice == "3":
            name = ask_rename(name, ask, say, folder)
        elif choice == "4":
            if ask_delete(name, ask, say, folder):
                say("")
                return
        elif choice == "5":
            what_if(items, name, goal, ask, say)
        elif choice == "6":
            split = ask_split(items, ask, say)
            if split is not None:
                changed, text = split
                remember(text, items, changed)
                items = changed
                save_class(folder, name, items)
                say("Saved.")
        elif choice == "7":
            counted = ask_rule(items, ask, say)
            if counted is not None:
                changed, text = counted
                remember(text, items, changed)
                items = changed
                save_class(folder, name, items)
                say("Saved.")
        elif choice == "8":
            back = ask_history(history, ask, say)
            if back is not None:
                items = back
                save_class(folder, name, items)
                say("Saved.")
        elif choice == "9":
            if ask_clear(items, name, ask, say):
                changed = cleared(items)
                remember("Cleared all grades", items, changed)
                items = changed
                save_class(folder, name, items)
                say("Saved.")
        elif choice == "10":
            see_grade_scale(items, name, goal, ask, say, folder)
        elif choice == "11":
            raise Quit
        else:
            say("Please type 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 or 11.")
        say("")


# --- History of this session (spec.md section 16, R18) ---

HISTORY_MENU = ["", "1) Go back to before a change", "2) Leave the history"]


def grade_change_text(before, after):
    """How Change a grade is listed in the history: "Changed homework 1.0 from 8 to 9"."""
    for item, new, label in zip(before, after, labels(before)):
        if item != new:
            return f"Changed {label} from {_grade_text(item.grade)} to {_grade_text(new.grade)}"
    return "Nothing changed"  # not added to the history (run_menu checks)


def _grade_text(grade):
    return "N/A" if grade is None else show_number(grade)


def ask_history(history, ask, say):
    """Show this session's changes and let the user go back to before one of them.

    Returns the items as they were before the change picked (that change and every later
    one leave the history), or None if nothing was undone.
    """
    if not history:
        say("No changes yet since the program was opened, so there is nothing to go back to.")
        return None
    while True:
        say("HISTORY: changes made since the program was opened (lost when it is closed)")
        for number, (text, _) in enumerate(history, start=1):
            say(f"  {number}) {text}")
        for line in HISTORY_MENU:
            say(line)
        choice = _ask(ask, "Choose 1 or 2: ").strip()
        if choice == "2":
            return None
        if choice == "1":
            last = len(history)
            number = _ask_number(ask, say, last, "Go back to before which change? (number): ")
            undone = (f"Change {number} will be undone." if number == last
                      else f"Changes {number} to {last} will be undone.")
            if _ask_yes_no(ask, say, f"Go back to before change {number}? {undone} Type Yes or No: "):
                items = history[number - 1][1]
                del history[number - 1:]
                say(f"Went back to before change {number}.")
                return items
            say("Nothing was undone.")
        else:
            say("Please type 1 or 2.")
        say("")


# --- Clearing all grades (spec.md section 18, R20) ---

def ask_clear(items, name, ask, say):
    """Ask Yes or No before clearing every grade of the open class. True for Yes.

    If every grade is already N/A, it says so and asks nothing (False).
    """
    if not has_grades(items):
        say("All the grades are already N/A, so there is nothing to clear.")
        return False
    question = (
        f'Are you sure you want to clear all the grades of "{name}"? They will all be N/A. '
        "You can go back with the history (option 8). Type Yes or No: "
    )
    if not _ask_yes_no(ask, say, question):
        say("Nothing was cleared.")
        return False
    say(f'Cleared all the grades of "{name}". They are all N/A now.')
    return True


# --- The grade scale (spec.md section 19, R21) ---

def see_grade_scale(items, name, goal, ask, say, folder):
    """The grade scale menu: each item in the class, then the whole class, then all saved
    classes together. Each one picked shows the scale with the goal and where it is.
    Enter goes back. Nothing is changed or saved.
    """
    shown = labels(items)
    left_out = dropped(items)
    choices = [position for position, item in enumerate(items) if item.weight > 0]
    count = len(choices) + 2
    while True:
        say("GRADE SCALE: see where a grade is on the scale")
        for number, position in enumerate(choices, start=1):
            say(f"  {number}) {shown[position]}")
        say(f"  {count - 1}) The whole class ({name})")
        say(f"  {count}) All your classes together")
        while True:
            typed = _ask(ask, "Pick one by number, or press Enter to go back: ").strip()
            if not typed:
                return
            if typed.isdigit() and 1 <= int(typed) <= count:
                break
            say(f"Please type a number from 1 to {count}, or press Enter to go back.")
        picked = int(typed)
        if picked <= len(choices):
            position = choices[picked - 1]
            first, here = _item_on_scale(items[position], shown[position], position in left_out)
        elif picked == count - 1:
            first, here = _class_on_scale(items, name)
        else:
            first, here = _all_classes_on_scale(folder)
        for line in first + [""] + scale_lines(here, goal) + ["", distance_text(here, goal), ""]:
            say(line)


def _item_on_scale(item, label, is_dropped):
    """(first lines, rounded %) for one item: "homework 1.0: 8 out of 10 = 80%"."""
    here = item_percent(item)
    if here is None:
        return [f"{label}: N/A"], None
    mark = "   (dropped)" if is_dropped else ""
    out_of = f"{show_number(item.grade)} out of {show_number(item.weight)}"
    return [f"{label}: {out_of} = {here}%{mark}"], here


def _class_on_scale(items, name):
    """(first lines, rounded %) for the whole class, as on the screen."""
    grade = current_grade(items)
    if grade is None:
        return [f"{name}: no grades out yet"], None
    return [
        f"{name}: {show_number(grade.earned)} out of {show_number(grade.out_of)} = "
        f"{grade.rounded}% = {grade.letter} ({grade.gpa})"
    ], grade.rounded


def _all_classes_on_scale(folder):
    """(first lines, rounded %) for all saved classes together: the plain average of each
    class's rounded %. Classes with no grades yet, or that can't be read, are not counted.
    """
    percents, lines = [], []
    for name in list_classes(folder):
        try:
            grade = current_grade(load_class(folder, name))
        except (FileProblems, OSError, UnicodeDecodeError):
            lines.append(f"  {name}: can't be read, not counted")
            continue
        if grade is None:
            lines.append(f"  {name}: no grades out yet, not counted")
        else:
            percents.append(grade.rounded)
            lines.append(f"  {name}: {grade.rounded}%")
    here = average_percent(percents)
    if here is None:
        return ["All your classes together: no grades out yet"] + lines, None
    classes = "class" if len(percents) == 1 else "classes"
    return [f"All your classes together: {here}%, the average of {len(percents)} {classes}"] + lines, here


# --- What if (spec.md section 12) ---

WHAT_IF_MENU = ["", "1) Try a grade", "2) Leave what-if mode"]


def what_if(items, name, goal, ask, say):
    """Try grades on a copy of the items until the user leaves. Nothing is ever saved.

    change_a_grade returns a new list, so the caller's items stay the real grades.
    """
    tried = list(items)
    while True:
        for line in ["WHAT IF: nothing here is saved"] + screen(tried, name, goal) + WHAT_IF_MENU:
            say(line)
        choice = _ask(ask, "Choose 1 or 2: ").strip()
        if choice == "1":
            tried = change_a_grade(tried, ask, say)
        elif choice == "2":
            say("Left what-if mode. Your real grades are back.")
            return
        else:
            say("Please type 1 or 2.")
        say("")


# --- Renaming and deleting a saved class (spec.md sections 9 and 10) ---

def ask_rename(name, ask, say, folder):
    """Ask for a new name until it can be used, then rename. Returns the name now in use."""
    while True:
        typed = _ask(ask, f'New name for "{name}" (press Enter to keep it): ')
        if not typed.strip():
            say(f'Kept the name "{name}".')
            return name
        try:
            new_name = rename_class(folder, name, typed)
        except NameProblem as problem:
            say(str(problem))
            continue
        except OSError as error:
            say(f'"{name}" could not be renamed ({error.__class__.__name__}). It was kept as it was.')
            return name
        say(f'Renamed "{name}" to "{new_name}".')
        return new_name


def _ask_yes_no(ask, say, question):
    """Ask until Yes or No is typed (capitals and spaces around it don't matter).
    True for Yes. Used to delete a class (R12) and to go back in the history (R18).
    """
    while True:
        typed = _ask(ask, question).strip().lower()
        if typed in ("yes", "no"):
            return typed == "yes"
        say("Please type Yes or No.")


def ask_delete(name, ask, say, folder):
    """Ask first until Yes or No is typed; delete only on Yes. True if it was deleted."""
    question = (
        f'Are you sure you want to delete "{name}"? It will be lost. '
        "Type Yes to delete it or No to keep it: "
    )
    if not _ask_yes_no(ask, say, question):
        say(f'Kept "{name}".')
        return False
    try:
        delete_class(folder, name)
    except OSError as error:
        say(f'"{name}" could not be deleted ({error.__class__.__name__}). It was kept.')
        return False
    say(f'Deleted "{name}".')
    return True


# --- Splitting a category (spec.md section 15, R17) ---

def ask_split(items, ask, say):
    """Ask which category to split and its parts. Returns (the new items, the history's
    line for it), or None if the category chosen can't be split (weight 0). Splitting a
    split category redoes it.
    """
    choices = splittable(items)
    say("Which category? (midterm and final can't be split)")
    for choice, (number, group) in enumerate(choices, start=1):
        weight = sum(items[position].weight for position in group)
        parts = f", in {len(group)} parts" if len(group) > 1 else ""
        say(f"  {choice}) {items[group[0]].name} ({number}), weight {show_number(weight)}{parts}")
    number, group = choices[_ask_number(ask, say, len(choices), "Which one? (number): ") - 1]
    name = items[group[0]].name
    weight = sum(items[position].weight for position in group)
    if weight == 0:
        say(f"{name} is not in this class (weight 0), so it can't be split.")
        return None

    count = _ask_number(ask, say, MAX_PARTS, "How many parts? (2 to 10, or 1 to join it back into one): ")
    part_labels = [f"{name} {number}.{part}" for part in range(count)] if count > 1 else [name]
    while True:
        weights = [weight] if count == 1 else [
            _ask_part_weight(ask, say, f"Weight of {label} (the {count} parts must add up to "
                                       f"{show_number(weight)}): ")
            for label in part_labels
        ]
        try:  # checks that the weights add up, before any grade is asked
            split_category(items, group, [Item(name, w, None) for w in weights])
            break
        except SplitProblem as problem:
            say(str(problem))
    parts = []
    for label, part_weight in zip(part_labels, weights):
        while True:
            typed = _ask(ask, f"Grade for {label} (out of {show_number(part_weight)}, or N/A): ")
            try:
                parts.append(Item(name, part_weight, parse_grade(typed, part_weight)))
                break
            except GradeProblem as problem:
                say(str(problem))
    text = f"Split {name} into {count} parts" if count > 1 else f"Joined {name} back into one"
    return split_category(items, group, parts), text


# --- Dropping the lowest grade or keeping the highest (spec.md section 17, R19) ---

# How each choice is named in the category list and after it is made ("homework now ...").
RULE_CHOICE = {
    None: "counts all parts", DROP_LOWEST: "drops the lowest grade",
    KEEP_HIGHEST: "keeps only the highest grade",
}
RULE_MENU = [
    "1) Count all parts (the standard)", "2) Drop the lowest grade", "3) Keep only the highest grade",
]


def ask_rule(items, ask, say):
    """Ask which split category and how it counts its parts. Returns (the new items, the
    history's line for it), or None if no category is split (nothing can be dropped).
    """
    choices = [
        (number, group) for number, group in enumerate(categories(items), start=1)
        if len(group) > 1
    ]
    if not choices:
        say("No category is split into parts yet, so no grade can be dropped. "
            "Split one first (option 6).")
        return None
    say("Which category? (only a split category can drop a grade)")
    for choice, (number, group) in enumerate(choices, start=1):
        first = items[group[0]]
        say(f"  {choice}) {first.name} ({number}), {len(group)} parts, {RULE_CHOICE[first.rule]}")
    _, group = choices[_ask_number(ask, say, len(choices), "Which one? (number): ") - 1]
    for line in RULE_MENU:
        say(line)
    rule = (None, DROP_LOWEST, KEEP_HIGHEST)[_ask_number(ask, say, 3, "Choose 1, 2 or 3: ") - 1]
    text = f"{items[group[0]].name} now {RULE_CHOICE[rule]}"  # also the history's line (R18)
    say(text + ".")
    return with_rule(items, group, rule), text


def _ask_part_weight(ask, say, question):
    """Ask for one part's weight until it is a number above 0."""
    while True:
        try:
            return parse_part_weight(_ask(ask, question))
        except SplitProblem as problem:
            say(str(problem))


def change_a_grade(items, ask, say):
    """Let the user pick an item and type its new grade. Returns the new list of items."""
    shown = labels(items)  # "homework 1.0" for a part of a split category (R17)
    for number, (item, label) in enumerate(zip(items, shown), start=1):
        grade = "N/A" if item.grade is None else show_number(item.grade)
        say(f"  {number}) {label}: {grade} out of {show_number(item.weight)}")
    position = _ask_number(ask, say, len(items), "Which one? (number): ") - 1
    item = items[position]
    while True:
        typed = _ask(
            ask, f"New grade for {shown[position]} (out of {show_number(item.weight)}, or N/A): "
        )
        try:
            new_grade = parse_grade(typed, item.weight)
            break
        except GradeProblem as problem:
            say(str(problem))
    changed = list(items)
    changed[position] = replace(item, grade=new_grade)  # keeps the drop/keep choice (R19)
    return changed


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
