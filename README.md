# Student Result Analyzer

A desktop application built with Python and Tkinter that reads a CSV file
of student marks and computes each student's total, average, percentage,
grade, and pass/fail result — developed as a Python development
internship project.

## Features

- **Load any marks CSV** — works with any number of subject columns, as
  long as the file has a `Name` and a `RollNumber` column
- **Automatic computation** — total, average, percentage, letter grade,
  and pass/fail for every student
- **Per-subject failure detection** — a student fails if any single
  subject falls below the passing mark, even if their overall percentage
  looks fine
- **Row-level error handling** — a bad row (missing name, non-numeric
  mark, out-of-range mark, wrong column count) is skipped and reported,
  without stopping the rest of the file from being processed
- **Search** — filter the results table by name or roll number
- **Export** — save the fully computed report back out as a new CSV

## Project Structure

```
result_analyzer/
├── main.py               # Entry point — run this to launch the app
├── gui.py                 # Tkinter GUI (presentation layer only)
├── result_processor.py    # Core data processing: grades, %, pass/fail
├── data_handler.py        # CSV file reading (I/O and file errors only)
├── validators.py          # Field-level validation rules
├── exceptions.py          # Custom exception types
├── sample_marks.csv       # Sample data to try the app with
├── test_result_analyzer.py # Unit test suite
└── README.md
```

Each module has exactly one job: `data_handler.py` only reads bytes off
disk, `validators.py` only checks individual field values, and
`result_processor.py` only computes results from already-validated data.
That separation is what makes `result_processor.py` and `validators.py`
fully unit-testable without touching a real file or a display.

## Expected CSV Format

```csv
Name,RollNumber,Math,Science,English,History
Aditi Sharma,R101,88,92,79,85
Rahul Verma,R102,45,30,55,60
```

- `Name` and a roll-number column (`RollNumber`, `Roll Number`, `Roll No`,
  etc. — matching is case-insensitive) are required.
- Every other column is treated as a subject, with marks out of 100.
- Any number of subject columns is supported — the app builds its table
  columns dynamically from whatever the file contains.

## How to Run

Requires Python 3.8+. Tkinter ships with most standard Python installs;
on some Linux distributions you may need to install it separately:

```bash
# Debian/Ubuntu, only if you get "No module named tkinter"
sudo apt-get install python3-tk
```

Then launch the app and click **Load CSV**, picking `sample_marks.csv`
to try it immediately:

```bash
python main.py
```

## Design Decisions

- **Per-subject passing mark (33 by default)**: a student who fails even
  one subject is marked `FAIL` overall, regardless of their combined
  percentage — this mirrors how real report cards work (a strong
  average doesn't rescue a failed subject). The constant `PASSING_MARKS`
  in `result_processor.py` is the only place this rule lives, so it's a
  one-line change if a different policy is needed.
- **Grade scale as a table, not if/elif chains**: `GRADE_SCALE` in
  `result_processor.py` is a simple ordered list of (threshold, grade)
  pairs, making it easy to see and adjust the cutoffs at a glance.
- **Collect errors instead of stopping at the first one**:
  `process_all_rows` returns both the valid results and a list of row
  errors, rather than raising on the first bad row. A CSV of 100
  students with one typo shouldn't block the other 99 from being
  analyzed.
- **Dynamic subject columns**: the GUI's table columns are built at
  load-time from the current file's headers, so the same app works for
  a report card with 4 subjects or 8, without any code changes.

## Validation & Error Handling Covered

- Missing or unreadable CSV file
- Empty CSV file
- Missing `Name` or roll-number column in the header
- No subject columns at all
- Missing student name or roll number in a row
- Non-numeric marks
- Marks outside the 0–100 range
- Row with the wrong number of columns
- Export failures (e.g. permission denied) reported instead of crashing

## Testing

The suite covers header validation, field validation, grade-boundary
computation, per-row result computation (including the fail-on-one-
subject rule), batch processing with mixed valid/invalid rows, and CSV
file reading (valid, missing, and empty files) — using temporary files
so tests never touch real data.

```bash
python -m unittest test_result_analyzer.py -v
```

19 tests, all passing.

I also ran the actual GUI headlessly against `sample_marks.csv` (not just
the unit tests) to confirm the full pipeline end-to-end: all 5 sample
students loaded with zero errors, and every computed total, percentage,
grade, and pass/fail result matched hand-calculated expectations exactly
— including both intentional fail cases (Rahul Verma failing Science,
Karan Mehta failing English despite an otherwise decent average). The
Export Report feature was verified the same way, writing out a report
file with matching computed values.

## Possible Future Improvements

- Class-wide statistics: subject-wise averages, class topper, rank list
- Support for `.xlsx` input via a library like `openpyxl`
- Configurable passing mark and grade scale via a settings dialog
- Bar chart of grade distribution using `matplotlib`
