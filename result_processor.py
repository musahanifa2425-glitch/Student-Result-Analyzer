"""
result_processor.py
---------------------
Core data-processing logic: turns raw CSV rows into fully computed
student result records (total, average, percentage, grade, pass/fail).

Kept separate from data_handler.py (file I/O) and validators.py
(field-level rules) so each module has exactly one job and can be
tested independently of the other two.
"""

from exceptions import ValidationError
from validators import validate_headers, validate_mark, validate_name, validate_roll_number

PASSING_MARKS = 33   # per-subject passing mark (common CBSE/state-board convention)
MAX_MARKS = 100

# Checked in order; the first threshold a percentage meets or exceeds wins.
GRADE_SCALE = [
    (90, "A+"),
    (80, "A"),
    (70, "B+"),
    (60, "B"),
    (50, "C"),
    (40, "D"),
    (0, "F"),
]


def compute_grade(percentage):
    """Map an overall percentage to a letter grade using GRADE_SCALE."""
    for threshold, grade in GRADE_SCALE:
        if percentage >= threshold:
            return grade
    return "F"


def process_student_row(headers, row, name_idx, roll_idx, subject_indices, row_number):
    """
    Validate and compute the full result for a single CSV row.
    Raises ValidationError (with the row number folded into the
    message) if anything about this row is invalid.
    """
    if len(row) != len(headers):
        raise ValidationError(
            f"Row {row_number}: expected {len(headers)} columns, found {len(row)}."
        )

    name = validate_name(row[name_idx], row_number)
    roll_number = validate_roll_number(row[roll_idx], row_number)

    marks = {}
    for idx in subject_indices:
        subject = headers[idx].strip()
        marks[subject] = validate_mark(row[idx], subject, row_number, MAX_MARKS)

    total = sum(marks.values())
    max_total = MAX_MARKS * len(marks)
    percentage = round((total / max_total) * 100, 2) if max_total else 0.0
    average = round(total / len(marks), 2) if marks else 0.0

    failed_subjects = [subject for subject, mark in marks.items() if mark < PASSING_MARKS]
    result = "FAIL" if failed_subjects else "PASS"
    grade = "F" if failed_subjects else compute_grade(percentage)

    return {
        "roll_number": roll_number,
        "name": name,
        "marks": marks,
        "total": total,
        "average": average,
        "percentage": percentage,
        "grade": grade,
        "result": result,
        "failed_subjects": failed_subjects,
    }


def process_all_rows(headers, rows):
    """
    Validate headers once, then process every row.

    Returns (results, errors): results is a list of computed student
    dicts for the valid rows; errors is a list of (row_number,
    message) tuples for rows that failed validation. One bad row
    doesn't stop the rest of the file from being processed.
    """
    name_idx, roll_idx, subject_indices = validate_headers(headers)

    results = []
    errors = []
    for i, row in enumerate(rows, start=2):  # data starts at row 2 (row 1 is the header)
        try:
            result = process_student_row(headers, row, name_idx, roll_idx, subject_indices, i)
            results.append(result)
        except ValidationError as e:
            errors.append((i, str(e)))

    return results, errors
