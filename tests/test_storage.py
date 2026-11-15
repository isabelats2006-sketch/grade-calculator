"""Tests for saving classes by name (spec.md section 6).

Every test uses tmp_path, a new empty folder pytest makes for that test, so the real
saved_classes/ folder is never touched.
"""

from fractions import Fraction

import pytest

from grades import FileProblems, Item, parse_class
from storage import (
    NameProblem, check_name, class_to_text, delete_class, find_class, list_classes, load_class,
    rename_class, save_class,
)

CSC299 = parse_class(
    "homework / midterm / final / attendance / project\n"
    "30 30 20 10 10\n"
    "20 25.5 N/A 10 N/A\n"
)


# --- The saved file ---

# Checks R10, R11.
def test_saved_text_lines_values_up_under_the_names():
    assert class_to_text(CSC299) == (
        "homework / midterm / final / attendance / project\n"
        "30         30        20      10           10\n"
        "20         25.5      N/A     10           N/A\n"
    )


# Checks R10.
def test_save_then_load_gives_back_the_same_class(tmp_path):
    save_class(tmp_path, "CSC 299", CSC299)
    assert load_class(tmp_path, "CSC 299") == CSC299


# Checks R10.
def test_exact_decimals_survive_saving(tmp_path):
    items = [
        Item("hw", Fraction(25), Fraction("20.123456")),
        Item("midterm", Fraction(25), None),
        Item("final", Fraction(40), None),
        Item("attendance", Fraction(10), Fraction("9.5")),
    ]
    save_class(tmp_path, "MATH 101", items)
    assert load_class(tmp_path, "MATH 101") == items


# Checks R10.
def test_save_makes_the_folder_if_missing(tmp_path):
    folder = tmp_path / "saved_classes"
    path = save_class(folder, "WRD 101", CSC299)
    assert path == folder / "WRD 101.txt"
    assert path.is_file()


# Checks R10, R11.
def test_saving_again_replaces_the_old_version(tmp_path):
    save_class(tmp_path, "CSC 299", CSC299)
    changed = [Item(i.name, i.weight, Fraction(18) if i.name == "final" else i.grade) for i in CSC299]
    save_class(tmp_path, "CSC 299", changed)
    assert load_class(tmp_path, "CSC 299")[2].grade == 18
    assert list_classes(tmp_path) == ["CSC 299"]


# Checks R10.
def test_saving_with_different_capitals_replaces_not_duplicates(tmp_path):
    save_class(tmp_path, "csc 299", CSC299)
    save_class(tmp_path, "CSC 299", CSC299)
    assert list_classes(tmp_path) == ["CSC 299"]


# Checks R8, R11.
def test_a_hand_edited_file_that_breaks_a_rule_is_explained(tmp_path):
    (tmp_path / "CSC 299.txt").write_text(
        "hw / midterm / final / attendance\n30 30 30 0\n20 20 20 0\n", encoding="utf-8"
    )
    with pytest.raises(FileProblems) as caught:
        load_class(tmp_path, "CSC 299")
    assert caught.value.problems == [
        "Line 2: the weights add up to 90, but they must add up to exactly 100."
    ]


# --- Listing and finding saved classes ---

# Checks R10.
def test_no_folder_yet_means_no_saved_classes(tmp_path):
    assert list_classes(tmp_path / "saved_classes") == []


# Checks R10.
def test_classes_are_listed_in_order_ignoring_capitals(tmp_path):
    for name in ["WRD 101", "csc 300", "MATH 101", "CSC 299"]:
        save_class(tmp_path, name, CSC299)
    assert list_classes(tmp_path) == ["CSC 299", "csc 300", "MATH 101", "WRD 101"]


# Checks R10.
def test_only_txt_files_are_classes(tmp_path):
    save_class(tmp_path, "CSC 299", CSC299)
    (tmp_path / "notes.md").write_text("not a class", encoding="utf-8")
    assert list_classes(tmp_path) == ["CSC 299"]


# Checks R10.
def test_find_class_ignores_capitals_and_spaces(tmp_path):
    save_class(tmp_path, "CSC 299", CSC299)
    assert find_class(tmp_path, "  csc 299 ") == "CSC 299"
    assert find_class(tmp_path, "CSC 300") is None


# --- Checking the name ---

# Checks R10.
def test_good_names_are_kept_without_outer_spaces():
    assert check_name("  CSC 299 ") == "CSC 299"
    assert check_name("MATH 101 (Fall)") == "MATH 101 (Fall)"


@pytest.mark.parametrize(
    "name, message",
    [
        ("", "Please type a name for the class, like CSC 299."),
        ("   ", "Please type a name for the class, like CSC 299."),
        ("CSC/299", "A class name can't contain /. Try something like CSC 299."),
        ('a:b?"c', 'A class name can\'t contain : ? ". Try something like CSC 299.'),
        ("CSC 299.", "A class name can't end with a dot."),
        ("con", 'Windows doesn\'t allow "con" as a name. Try another one.'),
        ("LPT1", 'Windows doesn\'t allow "LPT1" as a name. Try another one.'),
    ],
)
# Checks R7, R10.
def test_names_windows_cant_save_are_explained(name, message):
    with pytest.raises(NameProblem) as caught:
        check_name(name)
    assert str(caught.value) == message


# Checks R10.
def test_save_refuses_a_bad_name(tmp_path):
    with pytest.raises(NameProblem):
        save_class(tmp_path, "CSC/299", CSC299)
    assert list_classes(tmp_path) == []


# --- Renaming a saved class (spec.md section 9) ---

# Checks R13.
def test_rename_moves_the_class_and_keeps_its_grades(tmp_path):
    save_class(tmp_path, "CSC 299", CSC299)
    assert rename_class(tmp_path, "CSC 299", "CSC 299 (Fall)") == "CSC 299 (Fall)"
    assert list_classes(tmp_path) == ["CSC 299 (Fall)"]
    assert load_class(tmp_path, "CSC 299 (Fall)") == CSC299


@pytest.mark.parametrize("new_name", ["CSC 299 (Fall) & Lab #2", "Français 101", "MATH-101!", "it's 50% + €"])
# Checks R13.
def test_rename_allows_special_characters_windows_allows(tmp_path, new_name):
    save_class(tmp_path, "CSC 299", CSC299)
    rename_class(tmp_path, "CSC 299", new_name)
    assert list_classes(tmp_path) == [new_name]
    assert load_class(tmp_path, new_name) == CSC299


@pytest.mark.parametrize(
    "new_name, message",
    [
        ("CSC/299", "A class name can't contain /. Try something like CSC 299."),
        ("   ", "Please type a name for the class, like CSC 299."),
        ("CSC 299.", "A class name can't end with a dot."),
        ("NUL", "Windows doesn't allow \"NUL\" as a name. Try another one."),
    ],
)
# Checks R7, R13.
def test_rename_refuses_names_windows_cant_save_and_keeps_the_class(tmp_path, new_name, message):
    save_class(tmp_path, "CSC 299", CSC299)
    with pytest.raises(NameProblem) as caught:
        rename_class(tmp_path, "CSC 299", new_name)
    assert str(caught.value) == message
    assert list_classes(tmp_path) == ["CSC 299"]


# Checks R13.
def test_rename_refuses_a_name_another_class_has_and_keeps_both(tmp_path):
    save_class(tmp_path, "CSC 299", CSC299)
    other = parse_class("hw / midterm / final / attendance\n30 30 30 10\n1 1 1 1\n")
    save_class(tmp_path, "MATH 101", other)
    with pytest.raises(NameProblem) as caught:
        rename_class(tmp_path, "CSC 299", "math 101")
    assert str(caught.value) == 'There is already a saved class called "MATH 101". Pick another name.'
    assert load_class(tmp_path, "CSC 299") == CSC299
    assert load_class(tmp_path, "MATH 101") == other


# Checks R13.
def test_rename_can_change_only_the_capitals(tmp_path):
    save_class(tmp_path, "csc 299", CSC299)
    assert rename_class(tmp_path, "csc 299", "CSC 299") == "CSC 299"
    assert list_classes(tmp_path) == ["CSC 299"]
    assert load_class(tmp_path, "CSC 299") == CSC299


# Checks R13.
def test_rename_trims_spaces_around_the_new_name(tmp_path):
    save_class(tmp_path, "CSC 299", CSC299)
    assert rename_class(tmp_path, "CSC 299", "  WRD 101  ") == "WRD 101"
    assert list_classes(tmp_path) == ["WRD 101"]


# --- Deleting a saved class (spec.md section 10) ---

# Checks R12.
def test_delete_removes_only_that_class(tmp_path):
    save_class(tmp_path, "CSC 299", CSC299)
    save_class(tmp_path, "MATH 101", CSC299)
    delete_class(tmp_path, "CSC 299")
    assert list_classes(tmp_path) == ["MATH 101"]
    assert not (tmp_path / "CSC 299.txt").exists()
