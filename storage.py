"""Saving classes by name (spec.md section 6).

Each class is saved as <name>.txt in a folder (saved_classes/ when the program runs),
in the same three-line layout as a class file, so it can also be edited by hand.
"""

from pathlib import Path

from grades import parse_class, show_number

# Characters Windows does not allow in file names.
BAD_CHARACTERS = '\\/:*?"<>|'
# Names Windows reserves for devices; a file can't be called CON.txt, for example.
RESERVED = {"CON", "PRN", "AUX", "NUL"} | {f"COM{n}" for n in range(1, 10)} | {
    f"LPT{n}" for n in range(1, 10)
}


class NameProblem(Exception):
    """The class name can't be used as a file name. The message says why."""


def check_name(name):
    """Return the name without spaces around it, or raise NameProblem saying why not."""
    name = name.strip()
    if not name:
        raise NameProblem("Please type a name for the class, like CSC 299.")
    bad = [character for character in BAD_CHARACTERS if character in name]
    if bad:
        raise NameProblem(
            f"A class name can't contain {' '.join(bad)}. Try something like CSC 299."
        )
    if name.endswith("."):
        raise NameProblem("A class name can't end with a dot.")
    if name.upper() in RESERVED:
        raise NameProblem(f'Windows doesn\'t allow "{name}" as a name. Try another one.')
    return name


def class_to_text(items):
    """The three-line file text for these items, with values lined up under the names."""
    names = [item.name for item in items]
    widths = [len(name) + 3 for name in names]  # each name plus " / "

    def row(values):
        # At least one space after each value, even one longer than its name
        # (20.123456 under "hw" once came out as "20.123456N/A").
        cells = [value.ljust(width - 1) + " " for value, width in zip(values[:-1], widths)]
        return "".join(cells) + values[-1]

    weights = [show_number(item.weight) for item in items]
    grades = ["N/A" if item.grade is None else show_number(item.grade) for item in items]
    return " / ".join(names) + "\n" + row(weights) + "\n" + row(grades) + "\n"


def list_classes(folder):
    """The names of the saved classes in this folder, sorted (capitals ignored)."""
    folder = Path(folder)
    if not folder.is_dir():
        return []
    return sorted((path.stem for path in folder.glob("*.txt")), key=str.lower)


def find_class(folder, name):
    """The saved name matching this one, ignoring capitals, or None.

    Windows treats CSC 299 and csc 299 as the same file, so they must be the same class.
    """
    for saved in list_classes(folder):
        if saved.lower() == name.strip().lower():
            return saved
    return None


def save_class(folder, name, items):
    """Save the class as <name>.txt in the folder (made if missing). Returns the path.

    Replaces a class with the same name; the program asks before calling this.
    """
    name = check_name(name)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    existing = find_class(folder, name)
    if existing is not None and existing != name:
        (folder / f"{existing}.txt").unlink()  # renamed in capitals only: replace it
    path = folder / f"{name}.txt"
    path.write_text(class_to_text(items), encoding="utf-8")
    return path


def load_class(folder, name):
    """Load a saved class. Raises FileProblems if it was edited by hand and broke a rule."""
    path = Path(folder) / f"{name}.txt"
    return parse_class(path.read_text(encoding="utf-8"))


def rename_class(folder, old_name, new_name):
    """Rename a saved class (spec.md section 9). Returns the new name.

    Raises NameProblem if the new name can't be a file name, or if another saved class
    already has it (capitals ignored), so a rename never replaces another class.
    Changing only the capitals of the same class is allowed.
    """
    new_name = check_name(new_name)
    existing = find_class(folder, new_name)
    if existing is not None and existing.lower() != old_name.lower():
        raise NameProblem(f'There is already a saved class called "{existing}". Pick another name.')
    folder = Path(folder)
    (folder / f"{old_name}.txt").rename(folder / f"{new_name}.txt")
    return new_name


def delete_class(folder, name):
    """Delete a saved class's file (spec.md section 10). The program asks before calling this."""
    (Path(folder) / f"{name}.txt").unlink()
