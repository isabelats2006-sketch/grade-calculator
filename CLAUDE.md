# CLAUDE.md: grade calculator

A command-line app for my CSC 299 final project. Read `problem.md` (what it must do) and
`spec.md` (exactly how) before changing anything.

## Ground rules: the assignment's rules, never broken unless I say otherwise

- **problem.md is mine.** I write the requirements and any "Round N requirements" myself.
  Don't reword or add to it unless I ask, and keep my text.
- **Requirements come first.** In a round, my requirements are committed and pushed before
  any spec, test or code change.
- **Tests for everything.** Every new or changed behaviour gets a pytest test, and
  `python -m pytest` must pass with 0 failed and 0 skipped. A skipped test has not passed.
  A test must fail if the code it checks were wrong. Requirements have IDs (R1, R2...), and
  each test names the ID(s) it checks in a comment right above it: `# Checks R3, R8.`
- **Commits:** one change per commit. The message says what changed and why. Never
  "update", "fix", "wip" or similar. Never undo or amend a commit.
- **Show me every commit message before committing**, and wait for my OK. The assignment
  says I must read assistant-written messages before they are committed.
- **Push at least once on every day of work.**
- **Requirement IDs never change meaning.** A changed requirement keeps its number; a removed
  one stays in problem.md, marked removed; new ones get the next number, never a reused one.
- **Every round gets at least one decision record** in `docs/decisions/`, as a Y-statement,
  for a decision that had real alternatives. Files are numbered 0001, 0002, ... in order.
- **When breaking code on purpose to check a test fails**, check that the break really
  happened (that the file changed), then restore it and check that it matches the original.
- **Never in the repo:** `.jsonl` transcripts, `.venv`, `node_modules`, API keys or
  passwords, `saved_classes/` (real grades), or any personal info. The repo is public.
- **README.md** always says what the program does, the command to run it, and the command
  to run the tests.
- **Runs with one command** on my computer. No API key, login or paid service.
- **Ask before installing, changing, deleting, adding or modifying anything.**
- **Quote my requirements exactly** (in decision records, spec.md, anywhere), typos
  included. Don't fix my wording inside quotes.
- **Never run the program against the real `saved_classes/`.** Tests pass
  `folder=tmp_path`. For a real run, copy `gradecalc.py`, `grades.py`, `storage.py` and an
  example file into the scratchpad and run it there.

## How to run

```
python gradecalc.py csc299.txt     # open a class file
python gradecalc.py                # pick a saved class
python -m pytest                   # run the tests
```

## Code notes

- Python 3.13 on Windows, using Git Bash. Only the standard library, plus pytest for tests.
- Logic (reading files, grade math, goal math, saving) is kept apart from input/output, so
  it can be tested without typing.
- Grade math uses `fractions.Fraction`, not floats, so edge cases like 89.5% round
  correctly (with floats, 115 came out as 114.99999999999999).
- Rounding: nearest whole %, .5 goes up (Python's `round()` rounds .5 to even, so don't
  use it).
- For multi-line Python edit scripts, write the script to a file in the scratchpad **with
  the Write tool** and run it. Inline `python - <<'EOF'` in the Bash tool once failed to
  parse, and once turned `\n` inside a test string into real line breaks. Writing the
  script file with a Bash heredoc (`cat > x.py <<'EOF'`) did the same in round 3.
- `sed -i` in Git Bash rewrites the whole file's line endings, so `git diff` then shows
  every line as changed. When breaking code on purpose, copy the file to the scratchpad
  first, restore from that copy, and check it with `cmp` or `sha256sum`, not `git diff`.
- **Some files are CRLF, some LF** (check with `file *.py tests/*.py`). A search pattern
  with `\n` in it doesn't match a CRLF file. When breaking code on purpose, replace a
  single line, using a script that stops if the text isn't found exactly once, so a break
  that didn't happen is never mistaken for a test that passed.
- **Before writing a test that compares screen text, print the real output** and copy
  from it; don't count spaces by hand. To import from both the project and `tests/` in a
  one-off command: `PYTHONPATH=".;tests" python -c "..."` (Windows uses `;`, not `:`).
  Check every example of program output in `spec.md` the same way before committing it.
- **Test counts in commit messages come from pytest's totals** (after minus before), not
  from counting functions: parametrized tests count once per input.
- In a piped real run, the questions have no line break after them, so the answer and the
  next line run together; use `tail` to read the output, not `grep`/`sed` on a line.
- **When two changes end up in the same files** (and `git add -p` can't be used, since it
  is interactive), save a snapshot of each step's files in the scratchpad, then commit them
  one at a time, running the tests at each step.
