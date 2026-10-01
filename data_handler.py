"""
data_handler.py
----------------
Handles reading the raw CSV file. This module's only job is getting
rows of text out of a file - validating field values and computing
results happen in later stages (validators.py and
result_processor.py). Keeping file I/O isolated here means every
filesystem-related error is caught in exactly one place.
"""

import csv
import os

from exceptions import DataError


def read_csv_rows(file_path):
    """
    Read a CSV file and return (headers, rows), where rows is a list
    of lists of raw string values (not yet validated or converted).
    Blank lines are skipped. Raises DataError for any problem reading
    or parsing the file.
    """
    if not os.path.exists(file_path):
        raise DataError(f"File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            rows = [row for row in reader if any(cell.strip() for cell in row)]
    except PermissionError:
        raise DataError(f"Permission denied when reading '{file_path}'.")
    except UnicodeDecodeError:
        raise DataError("Could not read the file: it doesn't appear to be a valid text/CSV file.")
    except csv.Error as e:
        raise DataError(f"Could not parse CSV file: {e}")

    if not rows:
        raise DataError("The CSV file is empty.")

    headers, *data_rows = rows
    return headers, data_rows
