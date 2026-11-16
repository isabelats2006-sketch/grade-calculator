# 0005: Deleting a class is confirmed with Yes or No, not the class's name

Round 3, R12 (CHANGED): "Instead of typing the class name, you should type "Yes" or "No"
to confirm the deletion".

In the context of the question asked before a saved class is deleted (R12), which in
round 2 was `Are you sure you want to delete "CSC 299"? It will be lost. Type its name to
delete it, or press Enter to keep it:` and deleted the class only if its name was typed
exactly (capitals included, outer spaces ignored), keeping it on anything else,
facing a changed R12 that asks for "Yes" or "No" instead, and a known round 2 problem: a
class named `q` could never be deleted from the program, because typing its name, `q`,
at the question was read as "quit",
we decided to ask `Are you sure you want to delete "CSC 299"? It will be lost. Type Yes to
delete it or No to keep it:`, where `Yes` deletes and `No` keeps it, capitals and outer
spaces don't matter, and anything else, Enter included, says `Please type Yes or No.` and
asks again (`q` still quits and keeps the class),
and neglected keeping the round 2 name-typing question (R12 no longer allows it), and also
neglected accepting `y` and `n` as well, and also neglected "only Yes deletes, anything
else keeps it at once" without asking again,
to achieve the confirmation R12 now asks for, a question that is the same for every class
and quick to answer whatever the class is called, a class named `q` that can now be
deleted (its name is never typed), and no class deleted or kept by a typo, since an
unclear answer is asked again instead of being guessed,
accepting that `yes` is easier to type by habit than a class's name, so the question is a
lighter safety check than in round 2, and that `y`, which the program accepts for "Replace
it? (y/n)" when a new class has a used name, is not accepted here.

## What changed in the code and tests

- `ask_delete` in `gradecalc.py` (commit "Delete asks for Yes or No instead of the class
  name (R12 changed)").
- Old tests in `tests/test_cli.py` that changed:
  - `DELETE`, the expected question text used by the delete tests, has the new wording.
  - `test_deleting_asks_first_and_typing_the_name_deletes` became
    `test_deleting_asks_first_and_yes_deletes`, run with `Yes`, `yes`, `YES` and ` yEs `
    instead of ` CSC 299 `.
  - `test_anything_but_the_exact_name_keeps_the_class` became `test_no_keeps_the_class`,
    run with `No`, `no`, `NO` and ` nO `. Its old answers (`""`, `y`, `yes`, `csc 299`,
    `CSC 29`) no longer all keep the class: `yes` now deletes it, and the others are asked
    again (checked by the new test below).
  - `test_deleting_the_open_class_goes_back_to_the_list` and
    `test_deleting_the_last_class_says_none_are_left_and_ends` answer `yes` / `Yes`
    instead of the class's name.
  - `test_keeping_the_open_class_returns_to_the_menu` answers `No` instead of `n`.
- New tests: `test_anything_but_yes_or_no_asks_again` and
  `test_q_at_the_delete_question_quits_and_keeps_the_class`.
- `spec.md` section 10 has the new question. Round 2 decision 10 is marked as replaced by
  round 3 decision 15.

R12's change is the student's requirement. The exact answers accepted were chosen by the
student in the round 3 questions, from the options above.
