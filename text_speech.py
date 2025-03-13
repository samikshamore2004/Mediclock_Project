import json
import time
import tkinter as tk
from datetime import datetime
from plyer import notification
from tkinter import messagebox, ttk
import pyttsx3  # Text-to-speech library

# File paths
JSON_FILE = "data/prescriptions/prescription_20250227_164720.json"

# Initialize text-to-speech engine
tts_engine = pyttsx3.init()

# Create GUI window
root = tk.Tk()
root.title("Medicine Reminder")
root.geometry("450x550")
root.configure(bg="#f0f8ff")

# Heading Label
heading_label = tk.Label(root, text="Medicine Reminder", font=("Arial", 16, "bold"), bg="#f0f8ff", fg="#2c3e50")
heading_label.pack(pady=10)

# Label to show the next medicine reminder
reminder_label = tk.Label(root, text="Checking schedule...", font=("Arial", 14), bg="#f0f8ff", fg="black")
reminder_label.pack(pady=10)

# Patient name entry
patient_frame = tk.Frame(root, bg="#f0f8ff")
patient_frame.pack(pady=5)
patient_label = tk.Label(patient_frame, text="Patient Name:", font=("Arial", 12), bg="#f0f8ff")
patient_label.pack(side="left", padx=5)
patient_name = tk.StringVar(value="Patient")  # Default value
patient_entry = tk.Entry(patient_frame, textvariable=patient_name, font=("Arial", 12), width=20)
patient_entry.pack(side="left", padx=5)

# Frame to contain the list
frame = tk.Frame(root, bg="#f0f8ff")
frame.pack(pady=10)

# Scrollable Listbox for medicine schedule
listbox = tk.Listbox(frame, font=("Arial", 12), width=50, height=10)
listbox.pack(side="left", padx=10)

# Add scrollbar
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview)
scrollbar.pack(side="right", fill="y")
listbox.config(yscrollcommand=scrollbar.set)

# Function to load and process medicine schedule
def load_medicine_schedule():
    """Loads medicine schedule from JSON file."""
    try:
        with open(JSON_FILE, "r") as file:
            data = json.load(file)

        medicine_schedule = {}

        for med in data.get("Medicines", []):
            name = med.get("Medicine", "Unknown Medicine")
            timings = [t.strip() for t in med.get("Timings", [])]

            formatted_timings = []
            for t in timings:
                if ":" not in t:
                    formatted_timings.append(f"{int(t):02d}:00")
                else:
                    formatted_timings.append(t)

            medicine_schedule[name] = {
                "dosage": med.get("Dosage", "Unknown Dosage"),
                "timings": formatted_timings
            }

        return medicine_schedule

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load JSON file: {e}")
        return {}

# Function to update UI with medicine schedule
def update_medicine_list():
    """Updates the listbox with medicines and timings."""
    listbox.delete(0, tk.END)
    schedule = load_medicine_schedule()
    
    for medicine, details in schedule.items():
        listbox.insert(tk.END, f"{medicine} - {details['dosage']} at {', '.join(details['timings'])}")

update_medicine_list()

# Function to speak the reminder
def speak_reminder(medicine, dosage):
    """Uses text-to-speech to remind the patient to take medicine."""
    try:
        name = patient_name.get()
        reminder_text = f"Hey {name}, it's time to take your {medicine}, {dosage}"
        
        # Speak the reminder
        tts_engine.say(reminder_text)
        tts_engine.runAndWait()
        
        # Show message box after speaking
        messagebox.showinfo("Medicine Alert", f"⏰ {reminder_text} ⏰")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to speak reminder: {e}")

# Function to check for medicine reminders
def check_medicine_reminders():
    """Checks if it's time for a medicine and updates UI accordingly."""
    schedule = load_medicine_schedule()
    current_time = datetime.now().strftime("%H:%M")

    for medicine, details in schedule.items():
        if current_time in details["timings"]:
            message = f"Time to take {medicine} - {details['dosage']}"
            
            # Show notification
            notification.notify(title="Medicine Reminder", message=message, timeout=10)
            
            # Update UI
            reminder_label.config(text=message, fg="red")
            
            # Speak the reminder
            speak_reminder(medicine, details["dosage"])

            break  # Avoid multiple triggers at the same time
    
    root.after(30000, check_medicine_reminders)  # Check every 30 seconds

# Save patient name button
def save_patient_name():
    """Saves the patient name and shows confirmation."""
    messagebox.showinfo("Patient Name", f"Patient name set to: {patient_name.get()}")

save_button = tk.Button(root, text="Save Patient Name", command=save_patient_name, 
                        font=("Arial", 10), bg="#3498db", fg="white")
save_button.pack(pady=5)

# Start checking reminders
check_medicine_reminders()

# Run the GUI
root.mainloop()