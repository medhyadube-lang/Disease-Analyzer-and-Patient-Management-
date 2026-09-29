import tkinter as tk
from tkinter import messagebox, scrolledtext

DISEASES = {
    "Common Cold": {
        "symptoms": ["cough", "runny nose", "sneezing", "sore throat", "mild fever", "headache"],
        "info": "A common viral infection that usually affects the nose and throat.",
        "precautions": [
            "Rest as much as you can",
            "Drink plenty of warm fluids",
            "Wash your hands often",
            "Cover your mouth when you cough or sneeze",
            "Avoid close contact with others until you feel better"
        ]
    },
    "Flu": {
        "symptoms": ["fever", "cough", "sore throat", "body ache", "headache", "fatigue", "chills"],
        "info": "A viral respiratory illness that can cause fever, cough, aches and fatigue.",
        "precautions": [
            "Stay home and rest",
            "Drink lots of water and fluids",
            "Stay away from other people to avoid spreading it",
            "Wash your hands regularly",
            "See a doctor if the fever is high or lasts more than 3 days"
        ]
    },
    "Migraine": {
        "symptoms": ["headache", "nausea", "vomiting", "sensitivity to light", "sensitivity to sound"],
        "info": "A type of headache that can be associated with nausea and sensitivity to light or sound.",
        "precautions": [
            "Rest in a quiet, dark room",
            "Avoid bright screens and loud noise",
            "Keep a regular sleep schedule",
            "Do not skip meals and stay hydrated",
            "Note down your triggers such as stress, certain foods or lack of sleep"
        ]
    },
    "Food Poisoning": {
        "symptoms": ["nausea", "vomiting", "diarrhea", "stomach pain", "fever", "fatigue"],
        "info": "An illness that can occur after consuming contaminated food or drinks.",
        "precautions": [
            "Drink water or oral rehydration solution in small sips",
            "Avoid oily, spicy and outside food until you recover",
            "Eat light foods like rice, banana and toast when you feel better",
            "Wash your hands before eating and after using the toilet",
            "Get medical help if there is blood in stool or you cannot keep fluids down"
        ]
    },
    "Allergy": {
        "symptoms": ["sneezing", "runny nose", "itchy eyes", "watery eyes", "cough"],
        "info": "An immune response to substances such as pollen, dust or other allergens.",
        "precautions": [
            "Stay away from known triggers like dust, pollen or pets",
            "Keep your home clean and dust free",
            "Wear a mask when you go outside on dusty days",
            "Wash your face and hands after coming home",
            "Get help right away if you have swelling of the face or trouble breathing"
        ]
    },
    "Sore Throat": {
        "symptoms": ["sore throat", "difficulty swallowing", "fever", "swollen glands", "headache"],
        "info": "Throat irritation or inflammation that can have several different causes.",
        "precautions": [
            "Gargle with warm salt water",
            "Drink warm liquids like tea or soup",
            "Avoid cold drinks and very spicy food",
            "Rest your voice",
            "See a doctor if it lasts more than a week or you cannot swallow"
        ]
    },
    "Gastroenteritis": {
        "symptoms": ["diarrhea", "vomiting", "nausea", "stomach pain", "fever", "fatigue"],
        "info": "Inflammation of the stomach and intestines that can cause digestive symptoms.",
        "precautions": [
            "Keep drinking fluids to avoid dehydration",
            "Use oral rehydration solution",
            "Eat bland foods once vomiting stops",
            "Wash your hands well and often",
            "Avoid preparing food for others while you are sick"
        ]
    },
    "Sinusitis": {
        "symptoms": ["headache", "runny nose", "nasal congestion", "facial pain", "cough", "fever"],
        "info": "Inflammation of the tissues around the sinuses.",
        "precautions": [
            "Inhale steam a few times a day",
            "Drink plenty of fluids",
            "Use a warm compress on your face for comfort",
            "Avoid smoke, dust and strong smells",
            "See a doctor if symptoms last more than 10 days"
        ]
    },
    "Bronchitis": {
        "symptoms": ["cough", "chest discomfort", "fatigue", "mild fever", "shortness of breath"],
        "info": "Inflammation of the bronchial tubes that can cause coughing and breathing discomfort.",
        "precautions": [
            "Get plenty of rest",
            "Drink warm fluids to loosen mucus",
            "Avoid smoking and smoky places",
            "Use a humidifier or breathe in steam",
            "Get medical help if you have trouble breathing or a long lasting cough"
        ]
    },
    "Dehydration": {
        "symptoms": ["thirst", "fatigue", "dizziness", "headache", "dry mouth"],
        "info": "A condition that can occur when the body loses more fluids than it takes in.",
        "precautions": [
            "Drink water regularly through the day",
            "Use oral rehydration solution if you have lost a lot of fluid",
            "Avoid too much tea, coffee and soft drinks",
            "Stay out of the heat and rest in a cool place",
            "Get medical help if you feel very dizzy or confused"
        ]
    }
}

SAME_AS = {
    "temperature": "fever",
    "high temperature": "fever",
    "cold": "runny nose",
    "blocked nose": "nasal congestion",
    "stuffy nose": "nasal congestion",
    "loose motion": "diarrhea",
    "loose motions": "diarrhea",
    "tiredness": "fatigue",
    "weakness": "fatigue",
    "body pain": "body ache",
    "stomach ache": "stomach pain",
    "belly pain": "stomach pain",
    "light sensitivity": "sensitivity to light",
    "sound sensitivity": "sensitivity to sound"
}

def parse_input(text):
    symptoms = set()
    for item in text.lower().split(","):
        cleaned = item.strip()
        if cleaned:
            symptoms.add(SAME_AS.get(cleaned, cleaned))
    return symptoms

def calculate_matches(user_symptoms):
    matches = []
    for disease, details in DISEASES.items():
        disease_symptoms = set(details["symptoms"])
        matched = user_symptoms & disease_symptoms
        if matched:
            score = (len(matched) / len(disease_symptoms)) * 100
            matches.append({
                "name": disease,
                "score": score,
                "common": matched,
                "info": details["info"],
                "precautions": details["precautions"]
            })
    return sorted(matches, key=lambda x: x["score"], reverse=True)

def analyze(event=None):
    raw_input = entry.get().strip()
    if not raw_input:
        messagebox.showwarning("Input Required", "Please enter at least one symptom.")
        return

    results = calculate_matches(parse_input(raw_input))
    output.delete("1.0", tk.END)

    if not results:
        output.insert(tk.END, "No matching condition was found.\n\nTry symptoms like:\nfever, cough, headache, nausea")
        return

    output.insert(tk.END, "POSSIBLE CONDITIONS\n", "heading")
    output.insert(tk.END, "=" * 55 + "\n\n")

    for idx, match in enumerate(results[:3], start=1):
        output.insert(tk.END, f"{idx}. {match['name']}\n", "disease")
        output.insert(tk.END, f"Symptom match: {match['score']:.1f}%\n")
        output.insert(tk.END, f"Matching symptoms: {', '.join(sorted(match['common']))}\n")
        output.insert(tk.END, f"About: {match['info']}\n\n")
        output.insert(tk.END, "Precautions:\n", "sub")
        for precaution in match["precautions"]:
            output.insert(tk.END, f"  • {precaution}\n")
        output.insert(tk.END, "\n" + "-" * 55 + "\n\n")

    output.insert(tk.END, "IMPORTANT\n", "warning")
    output.insert(tk.END, "This app is for educational purposes only and is not a medical diagnosis.\n"
                          "Symptoms can have many different causes.\n"
                          "Please consult a qualified doctor for any health concern.")

def clear_all():
    entry.delete(0, tk.END)
    output.delete("1.0", tk.END)

def show_symptoms():
    all_symptoms = {symptom for data in DISEASES.values() for symptom in data["symptoms"]}
    output.delete("1.0", tk.END)
    output.insert(tk.END, "AVAILABLE SYMPTOMS\n", "heading")
    output.insert(tk.END, "=" * 55 + "\n\n")
    for symptom in sorted(all_symptoms):
        output.insert(tk.END, f"• {symptom}\n")

def show_diseases():
    output.delete("1.0", tk.END)
    output.insert(tk.END, "DISEASES COVERED\n", "heading")
    output.insert(tk.END, "=" * 55 + "\n\n")
    for name, data in DISEASES.items():
        output.insert(tk.END, f"{name}\n", "disease")
        output.insert(tk.END, f"{data['info']}\n\n")

root = tk.Tk()
root.title("Disease Analyzer")
root.geometry("820x760")
root.resizable(False, False)
root.configure(bg="#F2F5F7")

tk.Label(root, text="DISEASE ANALYZER", font=("Arial", 26, "bold"), bg="#F2F5F7").pack(pady=(25, 5))
tk.Label(root, text="Enter your symptoms to find possible conditions and precautions", font=("Arial", 11), bg="#F2F5F7").pack(pady=(0, 20))

input_card = tk.Frame(root, bg="#FFFFFF", padx=20, pady=20)
input_card.pack(padx=30, fill="x")

tk.Label(input_card, text="Enter symptoms separated by commas:", font=("Arial", 12, "bold"), bg="#FFFFFF").pack(anchor="w")
entry = tk.Entry(input_card, font=("Arial", 12), width=75)
entry.pack(pady=12, ipady=8)
entry.bind("<Return>", analyze)
tk.Label(input_card, text="Example: fever, cough, headache", font=("Arial", 9), fg="gray", bg="#FFFFFF").pack(anchor="w")

button_frame = tk.Frame(root, bg="#F2F5F7")
button_frame.pack(pady=20)

tk.Button(button_frame, text="Analyze", command=analyze, font=("Arial", 11, "bold"), padx=20, pady=10).grid(row=0, column=0, padx=6)
tk.Button(button_frame, text="Clear", command=clear_all, font=("Arial", 11), padx=20, pady=10).grid(row=0, column=1, padx=6)
tk.Button(button_frame, text="View Symptoms", command=show_symptoms, font=("Arial", 11), padx=15, pady=10).grid(row=0, column=2, padx=6)
tk.Button(button_frame, text="View Diseases", command=show_diseases, font=("Arial", 11), padx=15, pady=10).grid(row=0, column=3, padx=6)

tk.Label(root, text="Result", font=("Arial", 16, "bold"), bg="#F2F5F7").pack(anchor="w", padx=35)
output = scrolledtext.ScrolledText(root, width=88, height=20, font=("Arial", 10), wrap=tk.WORD)
output.pack(padx=30, pady=10)

output.tag_config("heading", font=("Arial", 14, "bold"))
output.tag_config("disease", font=("Arial", 12, "bold"))
output.tag_config("sub", font=("Arial", 10, "bold"))
output.tag_config("warning", font=("Arial", 11, "bold"))

tk.Label(root, text="Educational project — Not a medical diagnostic tool", font=("Arial", 9), fg="gray", bg="#F2F5F7").pack(pady=5)

root.mainloop()
