import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext

DISEASES={
    "Common Cold":{
        "symptoms":["cough","runny nose","sneezing","sore throat","mild fever","headache"],
        "description":"A common viral infection that usually affects the nose and throat."
    },
    "Flu":{
        "symptoms":["fever","cough","sore throat","body ache","headache","fatigue","chills"],
        "description":"A viral respiratory illness that can cause fever, cough, aches and fatigue."
    },
    "Migraine":{
        "symptoms":["headache","nausea","vomiting","sensitivity to light","sensitivity to sound"],
        "description":"A type of headache that can be associated with nausea and sensitivity to light or sound."
    },
    "Food Poisoning":{
        "symptoms":["nausea","vomiting","diarrhea","stomach pain","fever","fatigue"],
        "description":"An illness that can occur after consuming contaminated food or drinks."
    },
    "Allergy":{
        "symptoms":["sneezing","runny nose","itchy eyes","watery eyes","cough"],
        "description":"An immune response to substances such as pollen, dust or other allergens."
    },
    "Sore Throat":{
        "symptoms":["sore throat","difficulty swallowing","fever","swollen glands","headache"],
        "description":"Throat irritation or inflammation that can have several different causes."
    },
    "Gastroenteritis":{
        "symptoms":["diarrhea","vomiting","nausea","stomach pain","fever","fatigue"],
        "description":"Inflammation of the stomach and intestines that can cause digestive symptoms."
    },
    "Sinusitis":{
        "symptoms":["headache","runny nose","nasal congestion","facial pain","cough","fever"],
        "description":"Inflammation of the tissues around the sinuses."
    },
    "Bronchitis":{
        "symptoms":["cough","chest discomfort","fatigue","mild fever","shortness of breath"],
        "description":"Inflammation of the bronchial tubes that can cause coughing and breathing discomfort."
    },
    "Dehydration":{
        "symptoms":["thirst","fatigue","dizziness","headache","dry mouth"],
        "description":"A condition that can occur when the body loses more fluids than it takes in."
    }
}

ALIASES={
    "temperature":"fever",
    "high temperature":"fever",
    "cold":"runny nose",
    "blocked nose":"nasal congestion",
    "stuffy nose":"nasal congestion",
    "loose motion":"diarrhea",
    "loose motions":"diarrhea",
    "tiredness":"fatigue",
    "weakness":"fatigue",
    "body pain":"body ache",
    "stomach ache":"stomach pain",
    "belly pain":"stomach pain",
    "light sensitivity":"sensitivity to light",
    "sound sensitivity":"sensitivity to sound"
}

def process_symptoms(inp):
    items=inp.lower().split(",")
    syms=set()
    for s in items:
        s=s.strip()
        if not s:
            continue
        if s in ALIASES:
            s=ALIASES[s]
        syms.add(s)
    return syms

def find_conditions(syms):
    results=[]
    for name,data in DISEASES.items():
        ds=set(data["symptoms"])
        match=syms.intersection(ds)
        if len(match)>0:
            percent=(len(match)/len(ds))*100
            results.append({
                "name":name,
                "percent":percent,
                "match":match,
                "desc":data["description"]
            })
    results.sort(key=lambda x:x["percent"],reverse=True)
    return results

def check():
    inp=entry.get().strip()
    if not inp:
        messagebox.showwarning("Input Required","Please enter at least one symptom.")
        return

    syms=process_symptoms(inp)
    results=find_conditions(syms)
    box.delete("1.0",tk.END)

    if not results:
        box.insert(tk.END,"No matching condition was found.\n\nTry entering symptoms such as:\nfever, cough, headache, nausea")
        return

    box.insert(tk.END,"POSSIBLE CONDITIONS\n","heading")
    box.insert(tk.END,"="*55+"\n\n")

    for i,r in enumerate(results[:3],start=1):
        box.insert(tk.END,f"{i}. {r['name']}\n","disease")
        box.insert(tk.END,f"Symptom match: {r['percent']:.1f}%\n")
        box.insert(tk.END,"Matching symptoms: "+", ".join(sorted(r["match"]))+"\n")
        box.insert(tk.END,"Description: "+r["desc"]+"\n\n")

    box.insert(tk.END,"="*55+"\n")
    box.insert(tk.END,"\nIMPORTANT:\n","warning")
    box.insert(tk.END,"This application is for educational purposes only.\nIt does not provide a medical diagnosis.\nSymptoms can have many different causes.\nConsult a qualified healthcare professional for medical concerns.")

def clear():
    entry.delete(0,tk.END)
    box.delete("1.0",tk.END)

def show():
    syms=set()
    for data in DISEASES.values():
        syms.update(data["symptoms"])
    syms=sorted(syms)
    box.delete("1.0",tk.END)
    box.insert(tk.END,"AVAILABLE SYMPTOMS\n","heading")
    box.insert(tk.END,"="*55+"\n\n")
    for s in syms:
        box.insert(tk.END,"• "+s+"\n")

root=tk.Tk()
root.title("Symptom Checker")
root.geometry("800x700")
root.resizable(False,False)
root.configure(bg="#F2F5F7")

title=tk.Label(root,text="SYMPTOM CHECKER",font=("Arial",26,"bold"),bg="#F2F5F7")
title.pack(pady=(25,5))

sub=tk.Label(root,text="Enter your symptoms to find possible matching conditions",font=("Arial",11),bg="#F2F5F7")
sub.pack(pady=(0,20))

frame=tk.Frame(root,bg="#FFFFFF",padx=20,pady=20)
frame.pack(padx=30,fill="x")

label=tk.Label(frame,text="Enter symptoms separated by commas:",font=("Arial",12,"bold"),bg="#FFFFFF")
label.pack(anchor="w")

entry=tk.Entry(frame,font=("Arial",12),width=75)
entry.pack(pady=12,ipady=8)

ex=tk.Label(frame,text="Example: fever, cough, headache",font=("Arial",9),fg="gray",bg="#FFFFFF")
ex.pack(anchor="w")

btnframe=tk.Frame(root,bg="#F2F5F7")
btnframe.pack(pady=20)

checkbtn=tk.Button(btnframe,text="Check Symptoms",command=check,font=("Arial",11,"bold"),padx=20,pady=10)
checkbtn.grid(row=0,column=0,padx=8)

clearbtn=tk.Button(btnframe,text="Clear",command=clear,font=("Arial",11),padx=25,pady=10)
clearbtn.grid(row=0,column=1,padx=8)

showbtn=tk.Button(btnframe,text="View Symptoms",command=show,font=("Arial",11),padx=20,pady=10)
showbtn.grid(row=0,column=2,padx=8)

rlabel=tk.Label(root,text="Result",font=("Arial",16,"bold"),bg="#F2F5F7")
rlabel.pack(anchor="w",padx=35)

box=scrolledtext.ScrolledText(root,width=88,height=20,font=("Arial",10),wrap=tk.WORD)
box.pack(padx=30,pady=10)

box.tag_config("heading",font=("Arial",14,"bold"))
box.tag_config("disease",font=("Arial",12,"bold"))
box.tag_config("warning",font=("Arial",11,"bold"))

foot=tk.Label(root,text="Educational project — Not a medical diagnostic tool",font=("Arial",9),fg="gray",bg="#F2F5F7")
foot.pack(pady=5)

root.mainloop()  
