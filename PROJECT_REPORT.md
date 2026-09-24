# Project Report

**Project title:** Hospital Management System - Disease Analyzer & Patient Management
**Platform:** VITyarthi - Build Your Own Project
**Language / tools:** Python 3, Tkinter, SQLite

## 1. Problem statement
Small clinics often track patients, appointments and preliminary symptom
assessments on paper or in scattered spreadsheets. This makes it hard to find
records quickly, avoid double-booked appointments, and keep a history of past
assessments. This project provides one simple desktop application that stores
patient data, helps screen symptoms against common conditions, and manages
doctor appointments.

## 2. Objectives
- Maintain patient records with validated input (add, update, delete, search).
- Provide a symptom-based disease analyzer that ranks likely conditions.
- Let staff book, complete and cancel appointments without time clashes.
- Keep a saved diagnosis history for each patient.

## 3. Scope and users
Intended users are clinic front-desk staff and doctors. The system runs
offline on a single computer and stores everything in a local SQLite file.

## 4. System design
**Architecture (three layers):**
- *Presentation* - `main.py`: Tkinter window with three tabs (Patients, Disease
  Analyzer, Appointments) and a live status bar.
- *Logic* - `analyzer.py`: weighted rule-based scoring; `database.py` contains
  the validation rules.
- *Data* - SQLite database with three tables.

**Database schema**

| Table | Key columns |
|---|---|
| patients | id, name, age, gender, phone, address, created_at |
| appointments | id, patient_id (FK), doctor, date, time, reason, status |
| diagnoses | id, patient_id (FK), symptoms, result, created_at |

Foreign keys use `ON DELETE CASCADE`, so removing a patient removes their
appointments and diagnoses.

## 5. Disease analyzer algorithm
1. The user selects symptoms.
2. For each condition, `score = sum(weights of selected symptoms) / sum(all
   weights of that condition)`.
3. Conditions with score >= 0.20 are sorted by score (ties broken by number of
   matched symptoms) and the top three are shown.
4. If chest pain or shortness of breath is selected, an emergency warning is
   displayed.

The knowledge base covers 13 conditions (e.g. cold, influenza, COVID-19,
dengue, malaria, typhoid, pneumonia, asthma, migraine) and 26 symptoms.

## 6. Validation and error handling
- Name: letters, spaces and . ' - only. Age: integer 0-120. Gender required.
- Phone: optional, 7-15 digits with optional leading `+`.
- Appointment date `YYYY-MM-DD`, time `HH:MM`, and no double booking for the
  same doctor, date and time (cancelled slots can be rebooked).
- Destructive actions ask for confirmation; errors show message boxes instead
  of crashing.

## 7. Testing
15 automated unit tests (`tests/test_core.py`) cover patient CRUD, search,
validation failures, appointment clashes, cascade deletion and analyzer
ranking, emergency flag and output. All tests pass. The GUI was checked
manually by following the test cases below.

| # | Test case | Expected result |
|---|---|---|
| 1 | Add patient with valid data | Appears in the list; status bar count increases |
| 2 | Add patient with age "abc" | Error message, nothing saved |
| 3 | Select a patient, edit and Update | Row shows updated values |
| 4 | Delete a patient | Confirmation; record and related data removed |
| 5 | Select Fever, Body ache, Chills, Cough and Analyze | Influenza ranked first |
| 6 | Select Chest pain | Emergency warning shown |
| 7 | Save result without choosing a patient | Error asking to select a patient |
| 8 | Book the same doctor at the same time twice | Second booking rejected |
| 9 | Book with date 01-10-2026 | Format error |

## 8. Limitations
- The analyzer is rule-based and not a clinical diagnostic tool.
- Single-user, local database; no login or role management.
- Doctors are a fixed list in the code.

## 9. Future enhancements
- Login with roles (admin, doctor, receptionist).
- Machine-learning classifier trained on a real symptom dataset.
- Billing, prescriptions, and PDF report export.
- Calendar date picker and appointment reminders.

## 10. Conclusion
The project delivers a working, validated and tested patient management
system with an integrated symptom analyzer, built only with the Python
standard library so it runs anywhere Python is installed.

## 11. Disclaimer
The disease analyzer is for educational use only and is not a substitute for
professional medical advice.
