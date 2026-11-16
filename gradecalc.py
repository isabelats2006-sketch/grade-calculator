"""Grade calculator: the program you run (spec.md sections 2, 5, 6, 7 and 9 to 13).

    python gradecalc.py csc299.txt     open a class file (first time)
    python gradecalc.py                pick one of your saved classes

All the questions and printing happen here; the math is in grades.py and saving is in
storage.py. `ask` and `say` are passed in so tests can type answers and read the screen.
"""

import sys
from pathlib import Path

from grades import (
    FileProblems, GoalProblem, GradeProblem, Item, average_gpa, current_grade,
    describe_needed, needed_for, parse_class, parse_goal, parse_grade, show_number,
)
from storage import (
    NameProblem, check_name, class_to_text, delete_class, find_class, list_classes, load_class,
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
    names_row, weights_row, grades_row = class_to_text(items).splitlines()
    width = max(len(names_row), len(weights_row), len(grades_row)) + 2
    return [
        name,
        f"GOAL = {goal.label} // CURRENT GRADE = {now}",
        "",
        names_row,
        weights_row.ljust(width) + "= total weight",
        grades_row.ljust(width) + "= " + summary,
        "",
        describe_needed(needed_for(items, goal), goal),
    ]


MENU = [
    "", "1) Change a grade", "2) Change the goal", "3) Rename this class", "4) Delete this class",
    "5) What if (try grades without saving)", "6) Quit",
]


def run_menu(items, name, goal, ask, say, folder):
    """Show the result and the menu until the user quits (raises Quit).

    Returns only if the class was deleted, so the caller can go back to the saved-class list.
    """
    while True:
        for line in screen(items, name, goal) + MENU:
            say(line)
        choice = _ask(ask, "Choose 1 to 6: ").strip()
        if choice == "1":
            items = change_a_grade(items, ask, say)
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
            raise Quit
        else:
            say("Please type 1, 2, 3, 4, 5 or 6.")
        say("")


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


def ask_delete(name, ask, say, folder):
    """Ask first until Yes or No is typed; delete only on Yes. True if it was deleted."""
    question = (
        f'Are you sure you want to delete "{name}"? It will be lost. '
        "Type Yes to delete it or No to keep it: "
    )
    while True:
        typed = _ask(ask, question).strip().lower()
        if typed in ("yes", "no"):
            break
        say("Please type Yes or No.")
    if typed == "no":
        say(f'Kept "{name}".')
        return False
    try:
        delete_class(folder, name)
    except OSError as error:
        say(f'"{name}" could not be deleted ({error.__class__.__name__}). It was kept.')
        return False
    say(f'Deleted "{name}".')
    return True


def change_a_grade(items, ask, say):
    """Let the user pick an item and type its new grade. Returns the new list of items."""
    for number, item in enumerate(items, start=1):
        grade = "N/A" if item.grade is None else show_number(item.grade)
        say(f"  {number}) {item.name}: {grade} out of {show_number(item.weight)}")
    position = _ask_number(ask, say, len(items), "Which one? (number): ") - 1
    item = items[position]
    while True:
        typed = _ask(ask, f"New grade for {item.name} (out of {show_number(item.weight)}, or N/A): ")
        try:
            new_grade = parse_grade(typed, item.weight)
            break
        except GradeProblem as problem:
            say(str(problem))
    changed = list(items)
    changed[position] = Item(item.name, item.weight, new_grade)
    return changed


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
