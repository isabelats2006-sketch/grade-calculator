"""Tests for the program's questions, screen and menu (spec.md sections 2, 5, 6, 7).

Each test types answers in advance and reads back what the program printed. Every test
uses tmp_path (an empty folder) for files and saved classes, never the real ones.
"""

from fractions import Fraction

import pytest

from gradecalc import main
from grades import parse_grade, GradeProblem
from storage import list_classes, load_class, save_class
from grades import parse_class

SPEC_EXAMPLE = (
    "homework / midterm / final / attendance / project\n"
    "30 30 20 10 10\n"
    "20 25 N/A 10 N/A\n"
)


def run(args, answers, folder):
    """Run the program with these typed answers. Returns (exit code, printed text, questions)."""
    typed = iter(answers)
    questions, printed = [], []

    def ask(question):
        questions.append(question)
        try:
            return next(typed)
        except StopIteration:
            raise EOFError  # out of answers: like closing the input

    code = main(args, ask=ask, say=lambda line="": printed.append(str(line)), folder=folder)
    return code, "\n".join(printed), questions


@pytest.fixture
def class_file(tmp_path):
    path = tmp_path / "csc299.txt"
    path.write_text(SPEC_EXAMPLE, encoding="utf-8")
    return path


@pytest.fixture
def saved(tmp_path):
    return tmp_path / "saved_classes"


# --- The screen (spec.md section 5) ---

# Checks R3, R5, R6, R9.
def test_the_screen_matches_the_spec_example(class_file, saved):
    code, printed, _ = run([str(class_file)], ["CSC 299", "B", "9"], saved)
    assert code == 0
    assert (
        "CSC 299\n"
        "GOAL = B (3.0) // CURRENT GRADE = C+ (2.3), 79%\n"
        "\n"
        "homework / midterm / final / attendance / project\n"
        "30         30        20      10           10       = total weight\n"
        "20         25        N/A     10           N/A      = 55 out of 70 = 79% = C+ (2.3)\n"
        "-------------------- === --------------------\n"
        "homework:       20 out of 30 = 67%\n"
        "midterm:        25 out of 30 = 83%\n"
        "final:          N/A\n"
        "attendance:     10 out of 10 = 100%\n"
        "project:        N/A\n"
        "TOTAL:          55 out of 70 = 79%\n"
        "\n"
        "You need at least 92% on final and project to get a B.\n"
    ) in printed
    assert printed.endswith("Bye!")


# Checks R5, R7.
def test_no_grades_out_yet_is_shown_instead_of_a_grade(tmp_path, saved):
    path = tmp_path / "new.txt"
    path.write_text("hw / midterm / final / attendance\n30 30 30 10\nN/A N/A N/A N/A\n", encoding="utf-8")
    _, printed, _ = run([str(path)], ["", "A", "9"], saved)
    assert "CURRENT GRADE = no grades out yet" in printed
    assert "= no grades out yet" in printed


# --- Opening a file and saving it by name (sections 2 and 6) ---

# Checks R10.
def test_first_run_saves_the_class_with_the_suggested_name(class_file, saved):
    _, printed, questions = run([str(class_file)], ["", "B", "9"], saved)
    assert "(press Enter for csc299)" in questions[0]
    assert list_classes(saved) == ["csc299"]
    assert 'Saved as "csc299". Next time, just run: python gradecalc.py' in printed


# Checks R2, R3, R8.
def test_a_file_with_problems_is_explained_then_another_file_is_used(tmp_path, class_file, saved):
    bad = tmp_path / "bad.txt"
    bad.write_text("hw / midtrem / final / attendance\n30 30 30 0\n20 20 20 0\n", encoding="utf-8")
    _, printed, _ = run([str(bad)], [str(class_file), "CSC 299", "B", "9"], saved)
    assert f"There are problems with {bad}:" in printed
    assert '  - Line 1: name 2 should be "midterm", but it is "midtrem".' in printed
    assert "  - Line 2: the weights add up to 90, but they must add up to exactly 100." in printed
    assert "Please fix the file or use a different one." in printed
    assert "You need at least 92% on final and project to get a B." in printed


# Checks R7, R8.
def test_a_missing_file_is_explained_and_q_quits(tmp_path, saved):
    missing = tmp_path / "nope.txt"
    code, printed, _ = run([str(missing)], ["q"], saved)
    assert code == 0
    assert f'There is no file called "{missing}".' in printed
    assert printed.endswith("Bye!")
    assert list_classes(saved) == []


# Checks R7, R10.
def test_a_bad_class_name_is_explained_and_asked_again(class_file, saved):
    _, printed, _ = run([str(class_file)], ["CSC/299", "CSC 299", "B", "9"], saved)
    assert "A class name can't contain /. Try something like CSC 299." in printed
    assert list_classes(saved) == ["CSC 299"]


# Checks R10.
def test_replacing_a_saved_class_asks_first_and_no_keeps_it(class_file, saved):
    save_class(saved, "CSC 299", parse_class("hw / midterm / final / attendance\n30 30 30 10\n1 1 1 1\n"))
    _, printed, _ = run([str(class_file)], ["csc 299", "n", "CSC 299 new", "B", "9"], saved)
    assert "OK, pick another name." in printed
    assert list_classes(saved) == ["CSC 299", "CSC 299 new"]
    assert load_class(saved, "CSC 299")[0].grade == 1  # the old one was kept


# Checks R10.
def test_replacing_a_saved_class_with_yes(class_file, saved):
    save_class(saved, "CSC 299", parse_class("hw / midterm / final / attendance\n30 30 30 10\n1 1 1 1\n"))
    _, _, questions = run([str(class_file)], ["CSC 299", "y", "B", "9"], saved)
    assert 'There is already a saved class called "CSC 299". Replace it? (y/n): ' in questions
    assert list_classes(saved) == ["CSC 299"]
    assert load_class(saved, "CSC 299")[0].grade == 20  # replaced by the new file


# --- Picking a saved class (section 6) ---

# Checks R10.
def test_no_file_lists_saved_classes_and_opens_the_one_picked(saved):
    save_class(saved, "MATH 101", parse_class("hw / midterm / final / attendance\n30 30 30 10\n30 30 30 10\n"))
    save_class(saved, "CSC 299", parse_class(SPEC_EXAMPLE))
    _, printed, _ = run([], ["5", "1", "B", "9"], saved)
    assert "Your saved classes:\n  1) CSC 299\n  2) MATH 101" in printed
    assert "Please type a number from 1 to 2." in printed
    assert "You need at least 92% on final and project to get a B." in printed


# Checks R6, R10.
def test_no_saved_classes_explains_how_to_start(saved):
    code, printed, questions = run([], [], saved)
    assert code == 0
    assert questions == []
    assert "You have no saved classes yet. Start with a class file, for example:" in printed


# Checks R8, R11.
def test_a_saved_class_edited_by_hand_with_problems_is_explained(saved):
    saved.mkdir()
    (saved / "CSC 299.txt").write_text("hw / midterm / final / attendance\n30 30 30 0\n1 1 1 0\n", encoding="utf-8")
    code, printed, _ = run([], ["1"], saved)
    assert code == 0
    assert 'The saved class "CSC 299" has problems:' in printed
    assert "the weights add up to 90" in printed


# Checks R6, R7.
def test_more_than_one_file_shows_how_to_run_it(saved):
    code, printed, _ = run(["a.txt", "b.txt"], [], saved)
    assert code == 1
    assert "Please give at most one class file." in printed
    assert "python gradecalc.py csc299.txt" in printed


# --- The goal (section 4) ---

# Checks R6, R7.
def test_a_goal_that_cant_be_understood_is_asked_again(class_file, saved):
    _, printed, _ = run([str(class_file)], ["CSC 299", "A+", "3.5", "b", "9"], saved)
    assert 'I didn\'t understand "A+".' in printed
    assert "3.5 isn't a GPA on the scale." in printed
    assert "GOAL = B (3.0)" in printed


# Checks R6, R11.
def test_changing_the_goal_from_the_menu(class_file, saved):
    _, printed, _ = run([str(class_file)], ["CSC 299", "B", "2", "D", "9"], saved)
    assert "You need at least 92% on final and project to get a B." in printed
    assert "GOAL = D (1.0)" in printed
    assert "You need at least 15% on final and project to get a D." in printed


# --- Changing a grade (section 7) ---

# Checks R10, R11.
def test_changing_a_grade_updates_the_screen_and_the_saved_class(class_file, saved):
    _, printed, _ = run([str(class_file)], ["CSC 299", "B", "1", "3", "18", "9"], saved)
    assert "  3) final: N/A out of 20" in printed
    assert "Saved." in printed
    assert "= 73 out of 90 = 81% = B- (2.7)" in printed
    assert "You need at least 95% on project to get a B." in printed
    assert load_class(saved, "CSC 299")[2].grade == 18


# Checks R7, R11.
def test_a_bad_new_grade_is_explained_and_asked_again(class_file, saved):
    answers = ["CSC 299", "B", "1", "9", "3", "25", "eighteen", "n/a", "9"]
    _, printed, _ = run([str(class_file)], answers, saved)
    assert "Please type a number from 1 to 5." in printed
    assert "The grade can't be more than its weight (20)." in printed
    assert 'I didn\'t understand "eighteen". Type a number from 0 to 20, or N/A.' in printed


# Checks R7.
def test_a_wrong_menu_choice_is_explained(class_file, saved):
    _, printed, _ = run([str(class_file)], ["CSC 299", "B", "10", "9"], saved)
    assert "Please type 1, 2, 3, 4, 5, 6, 7, 8 or 9." in printed


# --- Quitting ---

@pytest.mark.parametrize("answers", [["CSC 299", "q"], ["CSC 299", "B", "q"], ["CSC 299", "B"]])
# Checks R7.
def test_q_or_closing_the_input_quits_cleanly_at_any_question(class_file, saved, answers):
    code, printed, _ = run([str(class_file)], answers, saved)
    assert code == 0
    assert printed.endswith("Bye!")


# --- parse_grade, the check behind "Change a grade" ---

@pytest.mark.parametrize("typed, weight, grade", [("18", 20, 18), ("0", 0, 0), ("N/A", 20, None), (" 19.5 ", 20, Fraction("19.5"))])
# Checks R3, R5, R11.
def test_parse_grade_accepts_the_same_grades_as_the_file(typed, weight, grade):
    assert parse_grade(typed, Fraction(weight)) == grade


@pytest.mark.parametrize(
    "typed, weight, message",
    [
        ("5", 0, "This item has weight 0, so its grade must be 0 or N/A."),
        ("-1", 20, 'I didn\'t understand "-1". Type a number from 0 to 20, or N/A.'),
    ],
)
# Checks R3, R4, R11.
def test_parse_grade_rejects_what_the_file_rejects(typed, weight, message):
    with pytest.raises(GradeProblem) as caught:
        parse_grade(typed, Fraction(weight))
    assert str(caught.value) == message


# --- Renaming a class (spec.md sections 9 and 11) ---

RENAME = 'New name for "CSC 299" (press Enter to keep it): '
DELETE = (
    'Are you sure you want to delete "CSC 299"? It will be lost. '
    "Type Yes to delete it or No to keep it: "
)
OTHER_CLASS = "hw / midterm / final / attendance\n30 30 30 10\n30 30 30 10\n"


# Checks R13, R15, R17, R18, R19.
def test_the_menu_lists_every_option_with_quit_last(class_file, saved):
    _, printed, questions = run([str(class_file)], ["CSC 299", "B", "9"], saved)
    assert (
        "1) Change a grade\n2) Change the goal\n3) Rename this class\n4) Delete this class\n"
        "5) What if (try grades without saving)\n6) Split a category\n"
        "7) Drop the lowest or keep the highest grade\n"
        "8) History (see this session's changes and go back)\n9) Quit"
    ) in printed
    assert questions[-1] == "Choose 1 to 9: "


# Checks R13.
def test_renaming_from_the_menu_renames_the_saved_class_and_the_screen(class_file, saved):
    answers = ["CSC 299", "B", "3", "CSC 299 (Fall) & Lab #2", "9"]
    _, printed, questions = run([str(class_file)], answers, saved)
    assert RENAME in questions
    assert 'Renamed "CSC 299" to "CSC 299 (Fall) & Lab #2".' in printed
    assert "CSC 299 (Fall) & Lab #2\nGOAL = B (3.0)" in printed
    assert list_classes(saved) == ["CSC 299 (Fall) & Lab #2"]
    assert load_class(saved, "CSC 299 (Fall) & Lab #2") == parse_class(SPEC_EXAMPLE)


# Checks R10, R13.
def test_a_grade_changed_after_renaming_is_saved_under_the_new_name(class_file, saved):
    answers = ["CSC 299", "B", "3", "WRD 101", "1", "3", "18", "9"]
    run([str(class_file)], answers, saved)
    assert list_classes(saved) == ["WRD 101"]
    assert load_class(saved, "WRD 101")[2].grade == 18


# Checks R7, R13.
def test_a_rename_to_a_bad_or_used_name_is_explained_and_asked_again(class_file, saved):
    save_class(saved, "MATH 101", parse_class(OTHER_CLASS))
    answers = ["CSC 299", "B", "3", "CSC: 299", "math 101", "CSC 299 Fall", "9"]
    _, printed, _ = run([str(class_file)], answers, saved)
    assert "A class name can't contain :. Try something like CSC 299." in printed
    assert 'There is already a saved class called "MATH 101". Pick another name.' in printed
    assert list_classes(saved) == ["CSC 299 Fall", "MATH 101"]
    assert load_class(saved, "MATH 101") == parse_class(OTHER_CLASS)


# Checks R13.
def test_enter_at_the_rename_question_keeps_the_name(class_file, saved):
    _, printed, _ = run([str(class_file)], ["CSC 299", "B", "3", "", "9"], saved)
    assert 'Kept the name "CSC 299".' in printed
    assert list_classes(saved) == ["CSC 299"]


# Checks R13.
def test_renaming_from_the_saved_class_list(saved):
    save_class(saved, "CSC 299", parse_class(SPEC_EXAMPLE))
    save_class(saved, "MATH 101", parse_class(OTHER_CLASS))
    answers = ["r", "1", "Zoology 1", "2", "B", "9"]
    _, printed, questions = run([], answers, saved)
    assert "Which class? (number): " in questions
    assert RENAME in questions
    assert 'Renamed "CSC 299" to "Zoology 1".' in printed
    assert "Your saved classes:\n  1) MATH 101\n  2) Zoology 1" in printed
    assert "Zoology 1\nGOAL = B (3.0)" in printed  # 2 now opens the renamed class
    assert list_classes(saved) == ["MATH 101", "Zoology 1"]


# --- Deleting a class (spec.md sections 10 and 11) ---

@pytest.mark.parametrize("typed", ["Yes", "yes", "YES", " yEs "])
# Checks R12.
def test_deleting_asks_first_and_yes_deletes(saved, typed):
    save_class(saved, "CSC 299", parse_class(SPEC_EXAMPLE))
    save_class(saved, "MATH 101", parse_class(OTHER_CLASS))
    _, printed, questions = run([], ["d", "1", typed, "q"], saved)
    assert DELETE in questions
    assert 'Deleted "CSC 299".' in printed
    assert printed.count("Your saved classes:") == 2
    assert printed.endswith("Your saved classes:\n  1) MATH 101\n\nBye!")
    assert list_classes(saved) == ["MATH 101"]


@pytest.mark.parametrize("typed", ["No", "no", "NO", " nO "])
# Checks R12.
def test_no_keeps_the_class(saved, typed):
    save_class(saved, "CSC 299", parse_class(SPEC_EXAMPLE))
    _, printed, questions = run([], ["d", "1", typed, "q"], saved)
    assert DELETE in questions
    assert 'Kept "CSC 299".' in printed
    assert "Deleted" not in printed
    assert load_class(saved, "CSC 299") == parse_class(SPEC_EXAMPLE)


# Checks R7, R12.
def test_anything_but_yes_or_no_asks_again(saved):
    save_class(saved, "CSC 299", parse_class(SPEC_EXAMPLE))
    answers = ["d", "1", "", "y", "n", "CSC 299", "yess", "yes"]
    _, printed, questions = run([], answers + ["q"], saved)
    assert questions.count(DELETE) == 6
    assert printed.count("Please type Yes or No.") == 5
    assert 'Deleted "CSC 299".' in printed
    assert list_classes(saved) == []


# Checks R7, R12.
def test_q_at_the_delete_question_quits_and_keeps_the_class(saved):
    save_class(saved, "CSC 299", parse_class(SPEC_EXAMPLE))
    _, printed, questions = run([], ["d", "1", "q"], saved)
    assert questions[-1] == DELETE
    assert printed.endswith("Bye!")
    assert load_class(saved, "CSC 299") == parse_class(SPEC_EXAMPLE)


# Checks R12.
def test_deleting_the_open_class_goes_back_to_the_list(class_file, saved):
    save_class(saved, "MATH 101", parse_class(OTHER_CLASS))
    answers = ["CSC 299", "B", "4", "yes", "1", "A", "9"]
    _, printed, questions = run([str(class_file)], answers, saved)
    assert DELETE in questions
    assert 'Deleted "CSC 299".' in printed
    assert "Your saved classes:\n  1) MATH 101" in printed
    assert "MATH 101\nGOAL = A (4.0)" in printed  # the other class opened, with a new goal
    assert list_classes(saved) == ["MATH 101"]


# Checks R12.
def test_deleting_the_last_class_says_none_are_left_and_ends(class_file, saved):
    code, printed, _ = run([str(class_file)], ["CSC 299", "B", "4", "Yes"], saved)
    assert code == 0
    assert 'Deleted "CSC 299".' in printed
    assert "You have no saved classes yet. Start with a class file, for example:" in printed
    assert printed.endswith("Bye!")
    assert list_classes(saved) == []


# Checks R12.
def test_keeping_the_open_class_returns_to_the_menu(class_file, saved):
    _, printed, _ = run([str(class_file)], ["CSC 299", "B", "4", "No", "9"], saved)
    assert 'Kept "CSC 299".' in printed
    assert printed.count("You need at least 92% on final and project to get a B.") == 2
    assert list_classes(saved) == ["CSC 299"]


# Checks R7, R12, R13.
def test_a_wrong_choice_in_the_saved_class_list_is_explained(saved):
    save_class(saved, "CSC 299", parse_class(SPEC_EXAMPLE))
    _, printed, questions = run([], ["x", "d", "7", "q"], saved)
    assert questions[0] == "Pick a class by number, r to rename, d to delete, or q to quit: "
    assert printed.count("Please type a number from 1 to 1.") == 2
    assert list_classes(saved) == ["CSC 299"]


# --- What if (spec.md section 12) ---

WHAT_IF_MENU = "1) Try a grade\n2) Leave what-if mode"
REAL_ROW = "= 55 out of 70 = 79% = C+ (2.3)"


# Checks R15.
def test_what_if_shows_the_tried_grade_without_saving_it(class_file, saved):
    # 5 = what if, 1 = try a grade, 3 = final, 20 out of 20, then q quits from inside.
    answers = ["CSC 299", "B", "5", "1", "3", "20", "q"]
    _, printed, questions = run([str(class_file)], answers, saved)
    assert "WHAT IF: nothing here is saved\nCSC 299\nGOAL = B (3.0) // CURRENT GRADE = B (3.0), 83%" in printed
    assert "= 75 out of 90 = 83% = B (3.0)" in printed
    assert WHAT_IF_MENU in printed
    assert questions[-1] == "Choose 1 or 2: "
    assert load_class(saved, "CSC 299") == parse_class(SPEC_EXAMPLE)


# Checks R15.
def test_leaving_what_if_brings_the_real_grades_back(class_file, saved):
    answers = ["CSC 299", "B", "5", "1", "3", "20", "1", "5", "0", "2", "9"]
    _, printed, _ = run([str(class_file)], answers, saved)
    assert "= 75 out of 100 = 75% = C (2.0)" in printed  # final 20 and project 0 tried
    left = printed.split("Left what-if mode. Your real grades are back.")
    assert len(left) == 2
    assert REAL_ROW in left[1]
    assert "WHAT IF" not in left[1]
    assert load_class(saved, "CSC 299") == parse_class(SPEC_EXAMPLE)


# Checks R15.
def test_what_if_can_change_a_grade_that_is_already_out(class_file, saved):
    answers = ["CSC 299", "B", "5", "1", "2", "30", "2", "9"]
    _, printed, _ = run([str(class_file)], answers, saved)
    assert "= 60 out of 70 = 86% = B (3.0)" in printed  # midterm 25 tried as 30
    assert load_class(saved, "CSC 299")[1].grade == 25


# Checks R10, R15.
def test_changing_a_grade_after_what_if_saves_only_the_real_change(class_file, saved):
    # Try final = 20 in what if, leave, then really change homework to 30.
    answers = ["CSC 299", "B", "5", "1", "3", "20", "2", "1", "1", "30", "9"]
    run([str(class_file)], answers, saved)
    saved_items = load_class(saved, "CSC 299")
    assert saved_items[0].grade == 30
    assert saved_items[2].grade is None  # the tried final grade was not kept


# Checks R7, R15.
def test_a_wrong_choice_or_bad_grade_in_what_if_is_explained(class_file, saved):
    # 3 is not a what-if choice; 25 is above final's weight of 20, so it asks again.
    answers = ["CSC 299", "B", "5", "3", "1", "3", "25", "N/A", "2", "9"]
    _, printed, _ = run([str(class_file)], answers, saved)
    assert "Please type 1 or 2." in printed
    assert "The grade can't be more than its weight (20)." in printed
    assert "Left what-if mode. Your real grades are back." in printed
    assert load_class(saved, "CSC 299") == parse_class(SPEC_EXAMPLE)


# --- GPA across all classes (spec.md section 13) ---

NO_GRADES_YET = "hw / midterm / final / attendance\n30 30 30 10\nN/A N/A N/A N/A\n"


# Checks R14.
def test_two_classes_show_their_gpas_and_the_average_above_the_list(saved):
    save_class(saved, "CSC 299", parse_class(SPEC_EXAMPLE))  # C+ (2.3)
    save_class(saved, "MATH 101", parse_class(OTHER_CLASS))  # A (4.0)
    _, printed, _ = run([], ["q"], saved)
    assert printed.startswith(
        "GPA across all your classes: 3.15 (average of 2 classes)\n"
        "  CSC 299: C+ (2.3), 79%\n"
        "  MATH 101: A (4.0), 100%\n"
        "\n"
        "Your saved classes:\n  1) CSC 299\n  2) MATH 101"
    )


# Checks R14.
def test_one_class_shows_no_gpa_across_classes(saved):
    save_class(saved, "CSC 299", parse_class(SPEC_EXAMPLE))
    _, printed, _ = run([], ["q"], saved)
    assert "GPA across" not in printed
    assert printed.startswith("Your saved classes:\n  1) CSC 299")


# Checks R5, R14.
def test_a_class_with_no_grades_yet_is_listed_but_not_counted(saved):
    save_class(saved, "CSC 299", parse_class(SPEC_EXAMPLE))
    save_class(saved, "WRD 101", parse_class(NO_GRADES_YET))
    _, printed, _ = run([], ["q"], saved)
    assert printed.startswith(
        "GPA across all your classes: 2.30 (average of 1 class)\n"
        "  CSC 299: C+ (2.3), 79%\n"
        "  WRD 101: no grades out yet, not counted\n"
    )


# Checks R5, R14.
def test_no_grades_out_in_any_class(saved):
    save_class(saved, "ART 100", parse_class(NO_GRADES_YET))
    save_class(saved, "WRD 101", parse_class(NO_GRADES_YET))
    _, printed, _ = run([], ["q"], saved)
    assert printed.startswith("GPA across all your classes: no grades out yet\n")


# Checks R8, R14.
def test_a_class_that_cant_be_read_is_listed_but_not_counted(saved):
    save_class(saved, "CSC 299", parse_class(SPEC_EXAMPLE))
    save_class(saved, "MATH 101", parse_class(OTHER_CLASS))
    (saved / "MATH 101.txt").write_text("hw / midterm\n50 50\n1 2\n", encoding="utf-8")
    code, printed, _ = run([], ["q"], saved)
    assert code == 0
    assert printed.startswith(
        "GPA across all your classes: 2.30 (average of 1 class)\n"
        "  CSC 299: C+ (2.3), 79%\n"
        "  MATH 101: can't be read, not counted\n"
    )


# Checks R12, R14.
def test_the_gpa_across_classes_is_updated_after_a_delete(saved):
    save_class(saved, "CSC 299", parse_class(SPEC_EXAMPLE))  # C+ (2.3)
    save_class(saved, "MATH 101", parse_class(OTHER_CLASS))  # A (4.0)
    save_class(saved, "STAT 200", parse_class(OTHER_CLASS))  # A (4.0)
    _, printed, _ = run([], ["d", "1", "yes", "d", "1", "yes", "q"], saved)
    assert "GPA across all your classes: 3.43 (average of 3 classes)" in printed  # 3.4333...
    assert "GPA across all your classes: 4.00 (average of 2 classes)" in printed
    assert printed.count("GPA across") == 2  # not shown once only STAT 200 is left
    assert printed.endswith("Your saved classes:\n  1) STAT 200\n\nBye!")
