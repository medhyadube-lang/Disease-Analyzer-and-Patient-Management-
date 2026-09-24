"""Rule-based symptom analyzer.

Each condition maps symptoms to weights (1 = weak indicator, 3 = strong
indicator). A condition's score is the share of its total weight that the
patient's symptoms cover. This is an educational screening aid, NOT a
medical diagnosis.
"""

DISCLAIMER = (
    "This is an automated screening aid for educational use only. "
    "It is not a medical diagnosis. Please consult a qualified doctor."
)

DISEASES = {
    "Common Cold": {
        "symptoms": {"Runny nose": 3, "Sneezing": 3, "Sore throat": 2, "Cough": 2,
                     "Headache": 1, "Fatigue": 1},
        "severity": "Mild",
        "advice": "Rest, fluids and steam inhalation. See a doctor if it lasts over a week.",
    },
    "Influenza (Flu)": {
        "symptoms": {"Fever": 3, "Body ache": 3, "Chills": 2, "Cough": 2,
                     "Fatigue": 2, "Headache": 2, "Sore throat": 1},
        "severity": "Moderate",
        "advice": "Rest and hydration. Consult a doctor, especially if high-risk (elderly, pregnant, chronic illness).",
    },
    "COVID-19": {
        "symptoms": {"Fever": 2, "Cough": 2, "Loss of smell": 3, "Shortness of breath": 3,
                     "Fatigue": 2, "Body ache": 1, "Sore throat": 1, "Headache": 1},
        "severity": "Moderate to Severe",
        "advice": "Get tested, isolate, and seek urgent care if breathing becomes difficult.",
    },
    "Allergic Rhinitis": {
        "symptoms": {"Sneezing": 3, "Itchy eyes": 3, "Runny nose": 2, "Headache": 1},
        "severity": "Mild",
        "advice": "Avoid known triggers; antihistamines may help. Consult a doctor for recurring cases.",
    },
    "Dengue": {
        "symptoms": {"Fever": 3, "Headache": 2, "Joint pain": 3, "Body ache": 2,
                     "Rash": 2, "Nausea": 1, "Vomiting": 1, "Fatigue": 1},
        "severity": "Severe",
        "advice": "Needs a blood test (platelet count). Seek medical care promptly; stay hydrated.",
    },
    "Malaria": {
        "symptoms": {"Fever": 3, "Chills": 3, "Sweating": 2, "Headache": 2,
                     "Nausea": 1, "Vomiting": 1, "Body ache": 1},
        "severity": "Severe",
        "advice": "Get a blood smear / rapid test immediately; malaria needs prompt treatment.",
    },
    "Typhoid": {
        "symptoms": {"Fever": 3, "Abdominal pain": 2, "Loss of appetite": 2, "Headache": 1,
                     "Fatigue": 2, "Diarrhea": 1, "Nausea": 1},
        "severity": "Severe",
        "advice": "Blood culture / Widal test recommended. Consult a doctor; avoid unsafe food and water.",
    },
    "Gastroenteritis": {
        "symptoms": {"Diarrhea": 3, "Vomiting": 3, "Nausea": 2, "Abdominal pain": 2,
                     "Fever": 1, "Fatigue": 1},
        "severity": "Mild to Moderate",
        "advice": "Use oral rehydration solution. See a doctor if there is blood in stool or dehydration.",
    },
    "Pneumonia": {
        "symptoms": {"Cough": 2, "Fever": 2, "Shortness of breath": 3, "Chest pain": 3,
                     "Chills": 1, "Fatigue": 1},
        "severity": "Severe",
        "advice": "Chest X-ray and medical evaluation needed. Seek care urgently.",
    },
    "Asthma": {
        "symptoms": {"Shortness of breath": 3, "Cough": 2, "Chest pain": 1, "Fatigue": 1},
        "severity": "Moderate",
        "advice": "Use prescribed inhaler if available; see a doctor if breathlessness is worsening.",
    },
    "Migraine": {
        "symptoms": {"Headache": 3, "Nausea": 2, "Vomiting": 1, "Blurred vision": 2,
                     "Dizziness": 2},
        "severity": "Moderate",
        "advice": "Rest in a dark, quiet room. Consult a doctor for frequent episodes.",
    },
    "Diabetes (screening flag)": {
        "symptoms": {"Frequent urination": 3, "Increased thirst": 3, "Blurred vision": 2,
                     "Fatigue": 2, "Dizziness": 1},
        "severity": "Needs testing",
        "advice": "Get a fasting blood glucose / HbA1c test and consult a doctor.",
    },
    "Jaundice / Hepatitis": {
        "symptoms": {"Jaundice (yellow skin/eyes)": 3, "Nausea": 1, "Loss of appetite": 2,
                     "Abdominal pain": 2, "Fatigue": 2, "Vomiting": 1},
        "severity": "Severe",
        "advice": "Liver function tests needed. Consult a doctor without delay.",
    },
}

EMERGENCY_SYMPTOMS = {"Chest pain", "Shortness of breath"}

# Sorted list of every symptom known to the analyzer (used to build the UI).
ALL_SYMPTOMS = sorted({s for d in DISEASES.values() for s in d["symptoms"]})


def analyze(symptoms, min_score=0.2, top_n=3):
    """Return a result dict for the given list of symptom names.

    Result keys: matches (list of dicts), emergency (bool), disclaimer (str).
    Each match has: disease, score (0-1), matched (list), severity, advice.
    """
    chosen = set(symptoms)
    matches = []
    for disease, info in DISEASES.items():
        weights = info["symptoms"]
        total = sum(weights.values())
        matched = [s for s in weights if s in chosen]
        if not matched or total == 0:
            continue
        score = sum(weights[s] for s in matched) / total
        if score >= min_score:
            matches.append({
                "disease": disease,
                "score": round(score, 2),
                "matched": matched,
                "severity": info["severity"],
                "advice": info["advice"],
            })
    matches.sort(key=lambda m: (-m["score"], -len(m["matched"]), m["disease"]))
    return {
        "matches": matches[:top_n],
        "emergency": bool(chosen & EMERGENCY_SYMPTOMS),
        "disclaimer": DISCLAIMER,
    }


def format_result(result):
    """Turn an analyze() result into readable text."""
    lines = []
    if result["emergency"]:
        lines.append("!! Warning: chest pain or breathing difficulty can be an "
                     "emergency. Seek medical help immediately. !!\n")
    if not result["matches"]:
        lines.append("No condition matched strongly. Add more symptoms or "
                     "consult a doctor.")
    for i, m in enumerate(result["matches"], 1):
        lines.append(f"{i}. {m['disease']}  -  match {int(m['score'] * 100)}%")
        lines.append(f"   Severity : {m['severity']}")
        lines.append(f"   Matched  : {', '.join(m['matched'])}")
        lines.append(f"   Advice   : {m['advice']}\n")
    lines.append(result["disclaimer"])
    return "\n".join(lines)


def summarize(result):
    """Short one-line summary used when saving to a patient's record."""
    if not result["matches"]:
        return "No strong match"
    return "; ".join(f"{m['disease']} ({int(m['score'] * 100)}%)"
                     for m in result["matches"])
