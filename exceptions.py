"""
exceptions.py
--------------
Custom exception types used across the Student Result Analyzer.

Keeping these separate from generic Python exceptions lets the GUI
catch exactly the failures it expects (a bad file vs. a bad row of
data) and show a precise message, without hiding real bugs behind a
blanket `except Exception`.
"""


class DataError(Exception):
    """Raised when the CSV file itself cannot be found, opened, or parsed."""
    pass


class ValidationError(Exception):
    """Raised when a header or a row's field values fail validation."""
    pass
