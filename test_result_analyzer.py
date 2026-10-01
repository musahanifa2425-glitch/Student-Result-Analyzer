"""
test_result_analyzer.py
-------------------------
Unit tests for the Student Result Analyzer.

Run with:
    python -m unittest test_result_analyzer.py -v

Tests run headless (no tkinter import) and use temporary CSV files
so they never touch any real data.
"""

import os
import tempfile
import unittest

from data_handler import read_csv_rows
from exceptions import DataError, ValidationError
from result_processor import compute_grade, process_all_rows, process_student_row
from validators import validate_headers, validate_mark, validate_name, validate_roll_number


class TestValidators(unittest.TestCase):
    def test_validate_headers_accepts_valid_headers(self):
        name_idx, roll_idx, subject_indices = validate_headers(["Name", "RollNumber", "Math", "Science"])
        self.assertEqual(name_idx, 0)
        self.assertEqual(roll_idx, 1)
        self.assertEqual(subject_indices, [2, 3])

    def test_validate_headers_is_case_insensitive_and_accepts_aliases(self):
        name_idx, roll_idx, subject_indices = validate_headers(["name", "Roll Number", "Math"])
        self.assertEqual((name_idx, roll_idx, subject_indices), (0, 1, [2]))

    def test_validate_headers_rejects_missing_name(self):
        with self.assertRaises(ValidationError):
            validate_headers(["RollNumber", "Math"])

    def test_validate_headers_rejects_missing_roll_number(self):
        with self.assertRaises(ValidationError):
            validate_headers(["Name", "Math"])

    def test_validate_headers_rejects_no_subject_columns(self):
        with self.assertRaises(ValidationError):
            validate_headers(["Name", "RollNumber"])

    def test_validate_name_rejects_empty(self):
        with self.assertRaises(ValidationError):
            validate_name("   ", row_number=2)

    def test_validate_roll_number_rejects_empty(self):
        with self.assertRaises(ValidationError):
            validate_roll_number("", row_number=2)

    def test_validate_mark_accepts_valid_number(self):
        self.assertEqual(validate_mark("85", "Math", row_number=2), 85.0)

    def test_validate_mark_rejects_non_numeric(self):
        with self.assertRaises(ValidationError):
            validate_mark("abc", "Math", row_number=2)

    def test_validate_mark_rejects_out_of_range(self):
        with self.assertRaises(ValidationError):
            validate_mark("150", "Math", row_number=2)
        with self.assertRaises(ValidationError):
            validate_mark("-5", "Math", row_number=2)

    def test_validate_mark_rejects_missing(self):
        with self.assertRaises(ValidationError):
            validate_mark("", "Math", row_number=2)


class TestResultProcessor(unittest.TestCase):
    def test_compute_grade_boundaries(self):
        self.assertEqual(compute_grade(95), "A+")
        self.assertEqual(compute_grade(90), "A+")
        self.assertEqual(compute_grade(85), "A")
        self.assertEqual(compute_grade(75), "B+")
        self.assertEqual(compute_grade(65), "B")
        self.assertEqual(compute_grade(55), "C")
        self.assertEqual(compute_grade(45), "D")
        self.assertEqual(compute_grade(20), "F")

    def test_process_student_row_computes_expected_fields(self):
        headers = ["Name", "RollNumber", "Math", "Science"]
        row = ["Aditi Sharma", "R101", "90", "80"]
        result = process_student_row(headers, row, 0, 1, [2, 3], row_number=2)
        self.assertEqual(result["name"], "Aditi Sharma")
        self.assertEqual(result["roll_number"], "R101")
        self.assertEqual(result["total"], 170)
        self.assertEqual(result["average"], 85.0)
        self.assertEqual(result["percentage"], 85.0)
        self.assertEqual(result["grade"], "A")
        self.assertEqual(result["result"], "PASS")

    def test_process_student_row_marks_fail_on_low_subject(self):
        headers = ["Name", "RollNumber", "Math", "Science"]
        row = ["Rahul Verma", "R102", "90", "20"]  # Science below the passing mark
        result = process_student_row(headers, row, 0, 1, [2, 3], row_number=3)
        self.assertEqual(result["result"], "FAIL")
        self.assertEqual(result["grade"], "F")
        self.assertIn("Science", result["failed_subjects"])

    def test_process_student_row_rejects_wrong_column_count(self):
        headers = ["Name", "RollNumber", "Math", "Science"]
        row = ["Aditi Sharma", "R101", "90"]  # missing one column
        with self.assertRaises(ValidationError):
            process_student_row(headers, row, 0, 1, [2, 3], row_number=2)

    def test_process_all_rows_collects_errors_without_stopping(self):
        headers = ["Name", "RollNumber", "Math", "Science"]
        rows = [
            ["Aditi Sharma", "R101", "90", "80"],
            ["", "R102", "70", "60"],           # invalid: empty name
            ["Priya Singh", "R103", "95", "88"],
        ]
        results, errors = process_all_rows(headers, rows)
        self.assertEqual(len(results), 2)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], 3)  # row number of the bad row


class TestDataHandler(unittest.TestCase):
    def setUp(self):
        fd, self.tmp_path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)

    def tearDown(self):
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    def test_read_csv_rows_parses_valid_file(self):
        with open(self.tmp_path, "w", newline="", encoding="utf-8") as f:
            f.write("Name,RollNumber,Math\nAditi Sharma,R101,90\n")
        headers, rows = read_csv_rows(self.tmp_path)
        self.assertEqual(headers, ["Name", "RollNumber", "Math"])
        self.assertEqual(rows, [["Aditi Sharma", "R101", "90"]])

    def test_read_csv_rows_raises_on_missing_file(self):
        os.remove(self.tmp_path)
        with self.assertRaises(DataError):
            read_csv_rows(self.tmp_path)

    def test_read_csv_rows_raises_on_empty_file(self):
        open(self.tmp_path, "w").close()
        with self.assertRaises(DataError):
            read_csv_rows(self.tmp_path)


if __name__ == "__main__":
    unittest.main()
