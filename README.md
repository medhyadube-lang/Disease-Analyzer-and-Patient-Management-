# Hospital Management System - Disease Analyzer & Patient Management

A desktop application built with **Python, Tkinter and SQLite** for the
VITyarthi *Build Your Own Project* submission.

## Features
- **Patient management:** add, update, delete and search patient records.
- **Disease analyzer:** pick symptoms and get the top matching conditions with
  a match percentage, severity, advice, and an emergency warning for chest pain
  or breathing difficulty. Results can be saved to a patient's history.
- **Appointments:** book appointments with doctors, with date/time validation
  and double-booking prevention. Mark as completed, cancel or delete.
- **Data safety:** input validation everywhere; deleting a patient also removes
  their appointments and diagnosis history (with a confirmation prompt).
- **Sample data:** File > Load sample data for a quick demo.

## Project structure
```
hospital_system/
├── main.py            # Tkinter GUI (run this)
├── database.py        # SQLite data layer + validation
├── analyzer.py        # Rule-based disease analyzer
├── tests/test_core.py # Unit tests (database + analyzer)
├── requirements.txt
├── README.md
└── PROJECT_REPORT.md
```

## How to run
1. Install Python 3.8+ (from python.org; Tkinter is included on Windows/macOS.
   On Ubuntu/Debian run `sudo apt install python3-tk`).
2. Open a terminal in the project folder and run:
   ```
   python main.py
   ```
   The database file `hospital.db` is created automatically on first run.

## How to run the tests
```
python -m unittest discover -s tests -v
```

## How the disease analyzer works
Each condition has weighted symptoms (1 = weak indicator, 3 = strong). The
score is the share of a condition's total weight covered by the selected
symptoms. Conditions scoring at least 20% are ranked and the top 3 are shown.

## Disclaimer
The analyzer is a rule-based educational tool. It is **not** a medical
diagnosis and must not replace advice from a qualified doctor.
