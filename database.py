"""SQLite data layer for the Hospital Management System."""
import re
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).with_name("hospital.db")

GENDERS = ("Male", "Female", "Other")
APPOINTMENT_STATUSES = ("Scheduled", "Completed", "Cancelled")


class ValidationError(ValueError):
    """Raised when user input fails validation."""


def validate_patient(name, age, gender, phone):
    """Validate patient fields and return cleaned (name, age, gender, phone)."""
    name = (name or "").strip()
    phone = (phone or "").strip()
    if not name:
        raise ValidationError("Name is required.")
    if not re.fullmatch(r"[A-Za-z .'-]+", name):
        raise ValidationError("Name may contain only letters, spaces, . ' and -.")
    try:
        age = int(age)
    except (TypeError, ValueError):
        raise ValidationError("Age must be a whole number.")
    if not 0 <= age <= 120:
        raise ValidationError("Age must be between 0 and 120.")
    if gender not in GENDERS:
        raise ValidationError("Please select a gender.")
    if phone and not re.fullmatch(r"\+?\d{7,15}", phone):
        raise ValidationError("Phone must be 7-15 digits (optional leading +).")
    return name, age, gender, phone


def validate_appointment(date, time):
    """Validate appointment date (YYYY-MM-DD) and time (HH:MM)."""
    try:
        datetime.strptime(date.strip(), "%Y-%m-%d")
    except ValueError:
        raise ValidationError("Date must be in YYYY-MM-DD format.")
    try:
        datetime.strptime(time.strip(), "%H:%M")
    except ValueError:
        raise ValidationError("Time must be in HH:MM (24-hour) format.")
    return date.strip(), time.strip()


class Database:
    def __init__(self, path=DB_PATH):
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL
                    REFERENCES patients(id) ON DELETE CASCADE,
                doctor TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                reason TEXT,
                status TEXT NOT NULL DEFAULT 'Scheduled'
            );
            CREATE TABLE IF NOT EXISTS diagnoses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL
                    REFERENCES patients(id) ON DELETE CASCADE,
                symptoms TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        self.conn.commit()

    # ---------------- patients ----------------
    def add_patient(self, name, age, gender, phone, address=""):
        name, age, gender, phone = validate_patient(name, age, gender, phone)
        cur = self.conn.execute(
            "INSERT INTO patients (name, age, gender, phone, address, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, age, gender, phone, address.strip(),
             datetime.now().strftime("%Y-%m-%d %H:%M")),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_patient(self, patient_id, name, age, gender, phone, address=""):
        name, age, gender, phone = validate_patient(name, age, gender, phone)
        self.conn.execute(
            "UPDATE patients SET name=?, age=?, gender=?, phone=?, address=? "
            "WHERE id=?",
            (name, age, gender, phone, address.strip(), patient_id),
        )
        self.conn.commit()

    def delete_patient(self, patient_id):
        self.conn.execute("DELETE FROM patients WHERE id=?", (patient_id,))
        self.conn.commit()

    def get_patient(self, patient_id):
        return self.conn.execute(
            "SELECT * FROM patients WHERE id=?", (patient_id,)
        ).fetchone()

    def get_patients(self, search=""):
        like = f"%{search.strip()}%"
        return self.conn.execute(
            "SELECT * FROM patients WHERE name LIKE ? OR phone LIKE ? "
            "OR CAST(id AS TEXT) LIKE ? ORDER BY id DESC",
            (like, like, like),
        ).fetchall()

    # ---------------- appointments ----------------
    def add_appointment(self, patient_id, doctor, date, time, reason=""):
        if not patient_id:
            raise ValidationError("Please select a patient.")
        if not (doctor or "").strip():
            raise ValidationError("Please choose a doctor / department.")
        date, time = validate_appointment(date, time)
        clash = self.conn.execute(
            "SELECT 1 FROM appointments WHERE doctor=? AND date=? AND time=? "
            "AND status='Scheduled'",
            (doctor.strip(), date, time),
        ).fetchone()
        if clash:
            raise ValidationError("That doctor already has an appointment at this time.")
        cur = self.conn.execute(
            "INSERT INTO appointments (patient_id, doctor, date, time, reason) "
            "VALUES (?, ?, ?, ?, ?)",
            (patient_id, doctor.strip(), date, time, reason.strip()),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_appointments(self):
        return self.conn.execute(
            "SELECT a.*, p.name AS patient_name FROM appointments a "
            "JOIN patients p ON p.id = a.patient_id "
            "ORDER BY a.date DESC, a.time DESC"
        ).fetchall()

    def set_appointment_status(self, appointment_id, status):
        if status not in APPOINTMENT_STATUSES:
            raise ValidationError("Invalid status.")
        self.conn.execute(
            "UPDATE appointments SET status=? WHERE id=?", (status, appointment_id)
        )
        self.conn.commit()

    def delete_appointment(self, appointment_id):
        self.conn.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
        self.conn.commit()

    # ---------------- diagnoses ----------------
    def add_diagnosis(self, patient_id, symptoms, result):
        if not patient_id:
            raise ValidationError("Please select a patient to save this result.")
        cur = self.conn.execute(
            "INSERT INTO diagnoses (patient_id, symptoms, result, created_at) "
            "VALUES (?, ?, ?, ?)",
            (patient_id, ", ".join(symptoms), result,
             datetime.now().strftime("%Y-%m-%d %H:%M")),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_diagnoses(self, patient_id):
        return self.conn.execute(
            "SELECT * FROM diagnoses WHERE patient_id=? ORDER BY id DESC",
            (patient_id,),
        ).fetchall()

    # ---------------- stats ----------------
    def stats(self):
        q = lambda sql: self.conn.execute(sql).fetchone()[0]
        return {
            "patients": q("SELECT COUNT(*) FROM patients"),
            "scheduled": q("SELECT COUNT(*) FROM appointments WHERE status='Scheduled'"),
            "diagnoses": q("SELECT COUNT(*) FROM diagnoses"),
        }

    def close(self):
        self.conn.close()
