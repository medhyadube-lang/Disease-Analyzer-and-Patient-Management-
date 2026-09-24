"""Hospital Management System - Disease Analyzer & Patient Management.

Run with:  python main.py
Requires Python 3.8+ (Tkinter and SQLite ship with the standard library).
"""
import tkinter as tk
from datetime import date, timedelta
from tkinter import messagebox, ttk

import analyzer
from database import (APPOINTMENT_STATUSES, GENDERS, Database,
                      ValidationError)

DOCTORS = [
    "Dr. Sharma - General Medicine",
    "Dr. Iyer - Pediatrics",
    "Dr. Khan - Cardiology",
    "Dr. Patel - Orthopedics",
    "Dr. Rao - Gynecology",
    "Dr. Das - ENT",
]


class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Management System - Disease Analyzer & Patient Management")
        self.geometry("1050x680")
        self.minsize(950, 620)
        self.db = Database()
        self.selected_patient_id = None
        self.last_result = None
        self.last_symptoms = []

        self._build_menu()
        self.status_var = tk.StringVar()
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=(8, 0))
        self.patients_tab = ttk.Frame(notebook)
        self.analyzer_tab = ttk.Frame(notebook)
        self.appt_tab = ttk.Frame(notebook)
        notebook.add(self.patients_tab, text="  Patients  ")
        notebook.add(self.analyzer_tab, text="  Disease Analyzer  ")
        notebook.add(self.appt_tab, text="  Appointments  ")
        ttk.Label(self, textvariable=self.status_var, relief="sunken",
                  anchor="w").pack(fill="x", side="bottom", padx=8, pady=6)

        self._build_patients_tab()
        self._build_analyzer_tab()
        self._build_appointments_tab()
        self.refresh_all()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ menu
    def _build_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load sample data", command=self.load_sample_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo(
            "About", "Hospital Management System\nDisease Analyzer & Patient "
            "Management\nBuilt with Python, Tkinter and SQLite.\n\n"
            + analyzer.DISCLAIMER))
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    # ---------------------------------------------------------- patients tab
    def _build_patients_tab(self):
        tab = self.patients_tab
        form = ttk.LabelFrame(tab, text="Patient details", padding=10)
        form.pack(side="left", fill="y", padx=8, pady=8)

        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        rows = [("Name", self.name_var), ("Age", self.age_var),
                ("Gender", self.gender_var), ("Phone", self.phone_var)]
        for r, (label, var) in enumerate(rows):
            ttk.Label(form, text=label).grid(row=r, column=0, sticky="w", pady=4)
            if label == "Gender":
                w = ttk.Combobox(form, textvariable=var, values=GENDERS,
                                 state="readonly", width=23)
            else:
                w = ttk.Entry(form, textvariable=var, width=26)
            w.grid(row=r, column=1, pady=4, padx=(8, 0))
        ttk.Label(form, text="Address").grid(row=4, column=0, sticky="nw", pady=4)
        self.address_text = tk.Text(form, width=20, height=4)
        self.address_text.grid(row=4, column=1, pady=4, padx=(8, 0))

        btns = ttk.Frame(form)
        btns.grid(row=5, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btns, text="Add", command=self.add_patient).grid(row=0, column=0, padx=3, pady=3)
        ttk.Button(btns, text="Update", command=self.update_patient).grid(row=0, column=1, padx=3, pady=3)
        ttk.Button(btns, text="Delete", command=self.delete_patient).grid(row=1, column=0, padx=3, pady=3)
        ttk.Button(btns, text="Clear", command=self.clear_patient_form).grid(row=1, column=1, padx=3, pady=3)

        right = ttk.Frame(tab)
        right.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=8)
        search_row = ttk.Frame(right)
        search_row.pack(fill="x")
        ttk.Label(search_row, text="Search (name / phone / ID):").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_patients())
        ttk.Entry(search_row, textvariable=self.search_var, width=30).pack(side="left", padx=8)

        cols = ("id", "name", "age", "gender", "phone", "address")
        self.patient_tree = ttk.Treeview(right, columns=cols, show="headings", height=18)
        widths = {"id": 50, "name": 170, "age": 50, "gender": 70, "phone": 110, "address": 200}
        for c in cols:
            self.patient_tree.heading(c, text=c.title())
            self.patient_tree.column(c, width=widths[c], anchor="w")
        sb = ttk.Scrollbar(right, orient="vertical", command=self.patient_tree.yview)
        self.patient_tree.configure(yscrollcommand=sb.set)
        self.patient_tree.pack(side="left", fill="both", expand=True, pady=(8, 0))
        sb.pack(side="left", fill="y", pady=(8, 0))
        self.patient_tree.bind("<<TreeviewSelect>>", self.on_patient_select)

    def _address(self):
        return self.address_text.get("1.0", "end").strip()

    def add_patient(self):
        try:
            self.db.add_patient(self.name_var.get(), self.age_var.get(),
                                self.gender_var.get(), self.phone_var.get(),
                                self._address())
        except ValidationError as e:
            messagebox.showerror("Invalid input", str(e))
            return
        self.clear_patient_form()
        self.refresh_all()
        messagebox.showinfo("Success", "Patient added.")

    def update_patient(self):
        if not self.selected_patient_id:
            messagebox.showwarning("No selection", "Select a patient from the list first.")
            return
        try:
            self.db.update_patient(self.selected_patient_id, self.name_var.get(),
                                   self.age_var.get(), self.gender_var.get(),
                                   self.phone_var.get(), self._address())
        except ValidationError as e:
            messagebox.showerror("Invalid input", str(e))
            return
        self.refresh_all()
        messagebox.showinfo("Success", "Patient updated.")

    def delete_patient(self):
        if not self.selected_patient_id:
            messagebox.showwarning("No selection", "Select a patient from the list first.")
            return
        if messagebox.askyesno("Confirm delete",
                               "Delete this patient and all their appointments "
                               "and diagnosis history?"):
            self.db.delete_patient(self.selected_patient_id)
            self.clear_patient_form()
            self.refresh_all()

    def clear_patient_form(self):
        self.selected_patient_id = None
        for v in (self.name_var, self.age_var, self.gender_var, self.phone_var):
            v.set("")
        self.address_text.delete("1.0", "end")
        self.patient_tree.selection_remove(self.patient_tree.selection())

    def on_patient_select(self, _event=None):
        sel = self.patient_tree.selection()
        if not sel:
            return
        pid = int(self.patient_tree.item(sel[0])["values"][0])
        p = self.db.get_patient(pid)
        if not p:
            return
        self.selected_patient_id = pid
        self.name_var.set(p["name"])
        self.age_var.set(p["age"])
        self.gender_var.set(p["gender"])
        self.phone_var.set(p["phone"] or "")
        self.address_text.delete("1.0", "end")
        self.address_text.insert("1.0", p["address"] or "")

    def refresh_patients(self):
        self.patient_tree.delete(*self.patient_tree.get_children())
        for p in self.db.get_patients(self.search_var.get()):
            self.patient_tree.insert("", "end", values=(
                p["id"], p["name"], p["age"], p["gender"], p["phone"] or "",
                (p["address"] or "").replace("\n", ", ")))

    # ---------------------------------------------------------- analyzer tab
    def _build_analyzer_tab(self):
        tab = self.analyzer_tab
        top = ttk.Frame(tab)
        top.pack(fill="x", padx=8, pady=8)
        ttk.Label(top, text="Patient:").pack(side="left")
        self.an_patient_var = tk.StringVar()
        self.an_patient_cb = ttk.Combobox(top, textvariable=self.an_patient_var,
                                          state="readonly", width=40)
        self.an_patient_cb.pack(side="left", padx=8)
        self.an_patient_cb.bind("<<ComboboxSelected>>", lambda _e: self.refresh_history())

        body = ttk.Frame(tab)
        body.pack(fill="both", expand=True, padx=8)

        sym_frame = ttk.LabelFrame(body, text="Select symptoms", padding=8)
        sym_frame.pack(side="left", fill="y")
        self.symptom_vars = {}
        per_col = 9
        for i, s in enumerate(analyzer.ALL_SYMPTOMS):
            var = tk.BooleanVar()
            self.symptom_vars[s] = var
            ttk.Checkbutton(sym_frame, text=s, variable=var).grid(
                row=i % per_col, column=i // per_col, sticky="w", padx=6, pady=2)
        btn_row = ttk.Frame(sym_frame)
        btn_row.grid(row=per_col, column=0, columnspan=3, pady=(10, 0), sticky="w")
        ttk.Button(btn_row, text="Analyze", command=self.run_analysis).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Save to patient record",
                   command=self.save_diagnosis).pack(side="left", padx=3)
        ttk.Button(btn_row, text="Reset", command=self.reset_analysis).pack(side="left", padx=3)

        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))
        res_frame = ttk.LabelFrame(right, text="Analysis result", padding=6)
        res_frame.pack(fill="both", expand=True)
        self.result_text = tk.Text(res_frame, height=12, wrap="word", state="disabled")
        self.result_text.pack(fill="both", expand=True)

        hist_frame = ttk.LabelFrame(right, text="Patient diagnosis history", padding=6)
        hist_frame.pack(fill="both", expand=True, pady=(8, 0))
        cols = ("date", "symptoms", "result")
        self.history_tree = ttk.Treeview(hist_frame, columns=cols, show="headings", height=6)
        for c, w in (("date", 120), ("symptoms", 220), ("result", 260)):
            self.history_tree.heading(c, text=c.title())
            self.history_tree.column(c, width=w, anchor="w")
        self.history_tree.pack(fill="both", expand=True)

    def _patient_choices(self):
        return [f"{p['id']} - {p['name']}" for p in self.db.get_patients()]

    @staticmethod
    def _id_from_choice(text):
        try:
            return int(text.split(" - ")[0])
        except (ValueError, IndexError):
            return None

    def _set_result(self, text):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")

    def run_analysis(self):
        symptoms = [s for s, v in self.symptom_vars.items() if v.get()]
        if not symptoms:
            messagebox.showwarning("No symptoms", "Select at least one symptom.")
            return
        self.last_symptoms = symptoms
        self.last_result = analyzer.analyze(symptoms)
        self._set_result(analyzer.format_result(self.last_result))

    def save_diagnosis(self):
        if not self.last_result:
            messagebox.showwarning("Nothing to save", "Run an analysis first.")
            return
        pid = self._id_from_choice(self.an_patient_var.get())
        try:
            self.db.add_diagnosis(pid, self.last_symptoms,
                                  analyzer.summarize(self.last_result))
        except ValidationError as e:
            messagebox.showerror("Cannot save", str(e))
            return
        self.refresh_history()
        self.update_status()
        messagebox.showinfo("Saved", "Result saved to the patient's record.")

    def reset_analysis(self):
        for v in self.symptom_vars.values():
            v.set(False)
        self.last_result = None
        self.last_symptoms = []
        self._set_result("")

    def refresh_history(self):
        self.history_tree.delete(*self.history_tree.get_children())
        pid = self._id_from_choice(self.an_patient_var.get())
        if pid:
            for d in self.db.get_diagnoses(pid):
                self.history_tree.insert("", "end", values=(
                    d["created_at"], d["symptoms"], d["result"]))

    # ------------------------------------------------------ appointments tab
    def _build_appointments_tab(self):
        tab = self.appt_tab
        form = ttk.LabelFrame(tab, text="Book appointment", padding=10)
        form.pack(side="left", fill="y", padx=8, pady=8)

        self.ap_patient_var = tk.StringVar()
        self.ap_doctor_var = tk.StringVar()
        self.ap_date_var = tk.StringVar(value=(date.today() + timedelta(days=1)).isoformat())
        self.ap_time_var = tk.StringVar(value="10:00")
        self.ap_reason_var = tk.StringVar()

        ttk.Label(form, text="Patient").grid(row=0, column=0, sticky="w", pady=4)
        self.ap_patient_cb = ttk.Combobox(form, textvariable=self.ap_patient_var,
                                          state="readonly", width=28)
        self.ap_patient_cb.grid(row=0, column=1, pady=4, padx=(8, 0))
        ttk.Label(form, text="Doctor").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Combobox(form, textvariable=self.ap_doctor_var, values=DOCTORS,
                     state="readonly", width=28).grid(row=1, column=1, pady=4, padx=(8, 0))
        for r, (label, var) in enumerate(
                [("Date (YYYY-MM-DD)", self.ap_date_var),
                 ("Time (HH:MM)", self.ap_time_var),
                 ("Reason", self.ap_reason_var)], start=2):
            ttk.Label(form, text=label).grid(row=r, column=0, sticky="w", pady=4)
            ttk.Entry(form, textvariable=var, width=31).grid(row=r, column=1, pady=4, padx=(8, 0))
        ttk.Button(form, text="Book appointment", command=self.book_appointment).grid(
            row=5, column=0, columnspan=2, pady=(12, 0))

        right = ttk.Frame(tab)
        right.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=8)
        cols = ("id", "patient", "doctor", "date", "time", "reason", "status")
        self.appt_tree = ttk.Treeview(right, columns=cols, show="headings", height=18)
        widths = {"id": 40, "patient": 120, "doctor": 190, "date": 85,
                  "time": 55, "reason": 140, "status": 80}
        for c in cols:
            self.appt_tree.heading(c, text=c.title())
            self.appt_tree.column(c, width=widths[c], anchor="w")
        self.appt_tree.pack(fill="both", expand=True)
        row = ttk.Frame(right)
        row.pack(fill="x", pady=(8, 0))
        ttk.Button(row, text="Mark completed",
                   command=lambda: self.set_status("Completed")).pack(side="left", padx=3)
        ttk.Button(row, text="Cancel appointment",
                   command=lambda: self.set_status("Cancelled")).pack(side="left", padx=3)
        ttk.Button(row, text="Delete", command=self.delete_appointment).pack(side="left", padx=3)

    def book_appointment(self):
        pid = self._id_from_choice(self.ap_patient_var.get())
        try:
            self.db.add_appointment(pid, self.ap_doctor_var.get(),
                                    self.ap_date_var.get(), self.ap_time_var.get(),
                                    self.ap_reason_var.get())
        except ValidationError as e:
            messagebox.showerror("Cannot book", str(e))
            return
        self.ap_reason_var.set("")
        self.refresh_appointments()
        self.update_status()
        messagebox.showinfo("Booked", "Appointment booked.")

    def _selected_appointment(self):
        sel = self.appt_tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select an appointment first.")
            return None
        return int(self.appt_tree.item(sel[0])["values"][0])

    def set_status(self, status):
        aid = self._selected_appointment()
        if aid:
            assert status in APPOINTMENT_STATUSES
            self.db.set_appointment_status(aid, status)
            self.refresh_appointments()
            self.update_status()

    def delete_appointment(self):
        aid = self._selected_appointment()
        if aid and messagebox.askyesno("Confirm delete", "Delete this appointment?"):
            self.db.delete_appointment(aid)
            self.refresh_appointments()
            self.update_status()

    def refresh_appointments(self):
        self.appt_tree.delete(*self.appt_tree.get_children())
        for a in self.db.get_appointments():
            self.appt_tree.insert("", "end", values=(
                a["id"], a["patient_name"], a["doctor"], a["date"], a["time"],
                a["reason"] or "", a["status"]))

    # --------------------------------------------------------------- shared
    def update_status(self):
        s = self.db.stats()
        self.status_var.set(
            f"  Patients: {s['patients']}   |   Scheduled appointments: "
            f"{s['scheduled']}   |   Saved diagnoses: {s['diagnoses']}")

    def refresh_all(self):
        self.refresh_patients()
        choices = self._patient_choices()
        self.an_patient_cb["values"] = choices
        self.ap_patient_cb["values"] = choices
        for var in (self.an_patient_var, self.ap_patient_var):
            if var.get() not in choices:
                var.set("")
        self.refresh_history()
        self.refresh_appointments()
        self.update_status()

    def load_sample_data(self):
        if self.db.stats()["patients"] > 0 and not messagebox.askyesno(
                "Load sample data", "Add sample patients to the existing data?"):
            return
        samples = [("Asha Verma", 34, "Female", "9876543210", "12 MG Road, Indore"),
                   ("Rohit Kumar", 45, "Male", "9123456780", "45 Park Street, Bhopal"),
                   ("Meena Singh", 8, "Female", "9988776655", "7 Lake View, Ujjain")]
        for s in samples:
            self.db.add_patient(*s)
        self.refresh_all()

    def _on_close(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    HospitalApp().mainloop()
