"""
gui.py
-------
Tkinter GUI for the Student Result Analyzer.

This module is only responsible for presentation: loading a CSV file,
showing computed results in a table, and exporting them. All real
computation lives in result_processor.py; all file reading lives in
data_handler.py. The table's columns are built dynamically from
whatever subjects the loaded file contains, so this works with any
CSV that has a Name column, a roll-number column, and one or more
subject columns.
"""

import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from data_handler import read_csv_rows
from exceptions import DataError, ValidationError
from result_processor import process_all_rows


class ResultAnalyzerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Result Analyzer")
        self.geometry("900x520")
        self.minsize(640, 400)

        self.results = []     # computed student dicts for the currently loaded file
        self.subjects = []    # ordered subject names for the currently loaded file
        self.errors = []      # (row_number, message) for rows skipped due to bad data
        self.source_path = None

        self._build_widgets()

    # ------------------------------------------------------- Layout
    def _build_widgets(self):
        toolbar = tk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=8)

        tk.Button(toolbar, text="Load CSV", command=self.load_csv).pack(side="left", padx=4)
        tk.Button(toolbar, text="Export Report", command=self.export_report).pack(side="left", padx=4)
        tk.Button(toolbar, text="View Errors", command=self.show_errors).pack(side="left", padx=4)

        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", padx=8)
        tk.Label(search_frame, text="Search (name / roll number):").pack(side="left")
        self.search_var = tk.StringVar()
        entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        entry.pack(side="left", padx=4)
        entry.bind("<KeyRelease>", lambda e: self.refresh_table())

        self.status_var = tk.StringVar(value="No file loaded. Click 'Load CSV' to begin.")
        tk.Label(self, textvariable=self.status_var, anchor="w").pack(fill="x", padx=8)

        self.tree = ttk.Treeview(self, show="headings")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

    # -------------------------------------------------------- Load
    def load_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select a student marks CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not file_path:
            return

        try:
            headers, rows = read_csv_rows(file_path)
            results, errors = process_all_rows(headers, rows)
        except DataError as e:
            messagebox.showerror("Could not load file", str(e))
            return
        except ValidationError as e:
            messagebox.showerror("Invalid file format", str(e))
            return

        self.results = results
        self.errors = errors
        self.source_path = file_path
        self.subjects = list(results[0]["marks"].keys()) if results else []

        self._configure_columns()
        self.refresh_table()

        summary = f"Loaded {len(results)} student(s) from {os.path.basename(file_path)}."
        if errors:
            summary += f" {len(errors)} row(s) had errors (see 'View Errors')."
        self.status_var.set(summary)

        if errors:
            messagebox.showwarning(
                "Some rows were skipped",
                f"{len(errors)} row(s) could not be processed and were skipped.\n"
                "Click 'View Errors' for details.",
            )

    def _configure_columns(self):
        columns = ["roll_number", "name"] + self.subjects + ["total", "average", "percentage", "grade", "result"]
        self.tree["columns"] = columns
        headings = {
            "roll_number": "Roll No", "name": "Name", "total": "Total",
            "average": "Average", "percentage": "Percentage", "grade": "Grade", "result": "Result",
        }
        for col in columns:
            self.tree.heading(col, text=headings.get(col, col))
            self.tree.column(
                col,
                width=150 if col == "name" else 90,
                anchor="w" if col == "name" else "center",
            )

    # ----------------------------------------------------- Refresh
    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        keyword = self.search_var.get().strip().lower()
        for student in self.results:
            if keyword and keyword not in student["name"].lower() and keyword not in student["roll_number"].lower():
                continue
            values = [student["roll_number"], student["name"]]
            values += [student["marks"][subj] for subj in self.subjects]
            values += [
                student["total"], student["average"],
                f"{student['percentage']}%", student["grade"], student["result"],
            ]
            tag = "fail" if student["result"] == "FAIL" else "pass"
            self.tree.insert("", "end", values=values, tags=(tag,))

        self.tree.tag_configure("fail", foreground="#B91C1C")
        self.tree.tag_configure("pass", foreground="#065F46")

    # ------------------------------------------------------ Errors
    def show_errors(self):
        if not self.errors:
            messagebox.showinfo("No errors", "There are no row errors to show.")
            return
        window = tk.Toplevel(self)
        window.title("Rows with errors")
        window.geometry("520x300")
        text = tk.Text(window, wrap="word")
        text.pack(fill="both", expand=True, padx=8, pady=8)
        for row_number, message in self.errors:
            text.insert("end", f"Row {row_number}: {message}\n")
        text.config(state="disabled")

    # ------------------------------------------------------ Export
    def export_report(self):
        if not self.results:
            messagebox.showinfo("Nothing to export", "Load a CSV file first.")
            return

        default_name = "analyzed_results.csv"
        if self.source_path:
            base, _ = os.path.splitext(os.path.basename(self.source_path))
            default_name = f"{base}_analyzed.csv"

        file_path = filedialog.asksaveasfilename(
            title="Save analyzed report",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv")],
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["RollNumber", "Name"] + self.subjects
                    + ["Total", "Average", "Percentage", "Grade", "Result"]
                )
                for student in self.results:
                    writer.writerow(
                        [student["roll_number"], student["name"]]
                        + [student["marks"][subj] for subj in self.subjects]
                        + [student["total"], student["average"], student["percentage"],
                           student["grade"], student["result"]]
                    )
            messagebox.showinfo("Export complete", f"Report saved to:\n{file_path}")
        except OSError as e:
            messagebox.showerror("Export failed", str(e))


if __name__ == "__main__":
    app = ResultAnalyzerApp()
    app.mainloop()
