"""Unit tests for the database and analyzer logic (no GUI needed).
Run from the project folder:  python -m unittest discover -s tests -v
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import analyzer
from database import Database, ValidationError


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.pid = self.db.add_patient("Asha Verma", 34, "Female", "9876543210", "Indore")

    def test_add_and_get_patient(self):
        p = self.db.get_patient(self.pid)
        self.assertEqual(p["name"], "Asha Verma")
        self.assertEqual(p["age"], 34)

    def test_search(self):
        self.assertEqual(len(self.db.get_patients("asha")), 1)
        self.assertEqual(len(self.db.get_patients("zzz")), 0)

    def test_update_patient(self):
        self.db.update_patient(self.pid, "Asha V", 35, "Female", "9876543210")
        self.assertEqual(self.db.get_patient(self.pid)["age"], 35)

    def test_validation_errors(self):
        with self.assertRaises(ValidationError):
            self.db.add_patient("", 20, "Male", "")
        with self.assertRaises(ValidationError):
            self.db.add_patient("Bob", "abc", "Male", "")
        with self.assertRaises(ValidationError):
            self.db.add_patient("Bob", 200, "Male", "")
        with self.assertRaises(ValidationError):
            self.db.add_patient("Bob", 20, "", "")
        with self.assertRaises(ValidationError):
            self.db.add_patient("Bob", 20, "Male", "12ab")

    def test_appointment_clash(self):
        self.db.add_appointment(self.pid, "Dr. Khan", "2026-10-01", "10:00", "checkup")
        with self.assertRaises(ValidationError):
            self.db.add_appointment(self.pid, "Dr. Khan", "2026-10-01", "10:00")

    def test_appointment_bad_date(self):
        with self.assertRaises(ValidationError):
            self.db.add_appointment(self.pid, "Dr. Khan", "01-10-2026", "10:00")

    def test_cancelled_slot_can_be_rebooked(self):
        aid = self.db.add_appointment(self.pid, "Dr. Khan", "2026-10-01", "10:00")
        self.db.set_appointment_status(aid, "Cancelled")
        self.db.add_appointment(self.pid, "Dr. Khan", "2026-10-01", "10:00")

    def test_cascade_delete(self):
        self.db.add_appointment(self.pid, "Dr. Khan", "2026-10-01", "10:00")
        self.db.add_diagnosis(self.pid, ["Fever"], "Flu")
        self.db.delete_patient(self.pid)
        self.assertEqual(self.db.stats(),
                         {"patients": 0, "scheduled": 0, "diagnoses": 0})

    def test_diagnosis_needs_patient(self):
        with self.assertRaises(ValidationError):
            self.db.add_diagnosis(None, ["Fever"], "Flu")


class AnalyzerTests(unittest.TestCase):
    def test_flu_like_symptoms(self):
        r = analyzer.analyze(["Fever", "Body ache", "Chills", "Cough"])
        self.assertTrue(r["matches"])
        self.assertEqual(r["matches"][0]["disease"], "Influenza (Flu)")

    def test_diabetes_flag(self):
        r = analyzer.analyze(["Frequent urination", "Increased thirst", "Blurred vision"])
        self.assertTrue(r["matches"][0]["disease"].startswith("Diabetes"))

    def test_emergency_flag(self):
        self.assertTrue(analyzer.analyze(["Chest pain"])["emergency"])
        self.assertFalse(analyzer.analyze(["Sneezing"])["emergency"])

    def test_no_symptoms_no_match(self):
        self.assertEqual(analyzer.analyze([])["matches"], [])

    def test_scores_are_sorted_and_bounded(self):
        r = analyzer.analyze(analyzer.ALL_SYMPTOMS)
        scores = [m["score"] for m in r["matches"]]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(all(0 < s <= 1 for s in scores))

    def test_format_includes_disclaimer(self):
        text = analyzer.format_result(analyzer.analyze(["Fever"]))
        self.assertIn("not a medical diagnosis", text)


if __name__ == "__main__":
    unittest.main()
