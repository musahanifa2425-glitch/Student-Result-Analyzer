"""
validators.py
--------------
Input validation utilities for the Student Result Analyzer.

Each function validates one piece of input and raises a
ValidationError with a clear, row-specific message when something is
invalid. Keeping validation separate from file reading and score
computation makes each piece independently testable.
"""

from exceptions import ValidationError

ROLL_NUMBER_HEADER_ALIASES = ("rollnumber", "roll number", "roll_number", "roll no", "rollno")


def validate_headers(headers):
    """
    Validate a CSV header row.

    Expects a 'Name' column, a roll-number column (several common
    spellings accepted), and at least one further column, which is
    treated as a subject of marks.

    Returns (name_idx, roll_idx, subject_indices).
    """
    if not headers:
        raise ValidationError("The CSV file has no header row.")

    normalized = [h.strip().lower() for h in headers]

    if "name" not in normalized:
        raise ValidationError("CSV is missing a 'Name' column.")
    if not any(alias in normalized for alias in ROLL_NUMBER_HEADER_ALIASES):
        raise ValidationError("CSV is missing a 'RollNumber' column.")

    name_idx = normalized.index("name")
    roll_idx = next(i for i, h in enumerate(normalized) if h in ROLL_NUMBER_HEADER_ALIASES)

    subject_indices = [i for i in range(len(headers)) if i not in (name_idx, roll_idx)]
    if not subject_indices:
        raise ValidationError("CSV must have at least one subject column with marks.")

    return name_idx, roll_idx, subject_indices


def validate_name(value, row_number):
    """Validate a student's name for one row."""
    value = (value or "").strip()
    if not value:
        raise ValidationError(f"Row {row_number}: student name is required.")
    return value


def validate_roll_number(value, row_number):
    """Validate a student's roll number for one row."""
    value = (value or "").strip()
    if not value:
        raise ValidationError(f"Row {row_number}: roll number is required.")
    return value


def validate_mark(value, subject, row_number, max_marks=100):
    """Validate one subject's mark: must be a number between 0 and max_marks."""
    raw = (value or "").strip()
    if not raw:
        raise ValidationError(f"Row {row_number}: missing marks for {subject}.")
    try:
        mark = float(raw)
    except ValueError:
        raise ValidationError(
            f"Row {row_number}: marks for {subject} must be a number (got '{raw}')."
        )
    if mark < 0 or mark > max_marks:
        raise ValidationError(
            f"Row {row_number}: marks for {subject} must be between 0 and {max_marks} (got {mark})."
        )
    return mark
