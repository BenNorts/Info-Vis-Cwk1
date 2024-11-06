import matplotlib.pyplot as plt
import numpy as np
import time
import csv
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import random

# Configuration parameters
NUM_TRIALS = 10
NUM_SCHOOLS = 10
NUM_MONTHS = 12
IMAGE_DIR = 'charts'
RESULTS_DIR = 'Results'
questions = [
    "Which school had the highest number of absences in month _?",
    "Which school had the lowest number of absences in month _?",
    "Which month were absences across all schools the highest?",
    "Is there a noticeable difference in absences between School - and School ^ in Month _? (A difference of 10 or more)",
    "Did School - have more absences in Month _ or Month *?",
    "Which month shows the greatest range in absences across schools?",
    "Which school had the most consistent number of absences throughout the year?",
    "Identify the school with the largest decrease in absences from one month to the next.",
    "Which month had the second highest absences for School -?",
    "Are there more absences in the first half of the year (January to June) or the second half (July to December) in School -?"
]

# Global state variables encapsulated in a dictionary for clarity
state = {
    "current_trial": 0,
    "chart_type": 'heatmap',
    "task_description": '',
    "target_school_id": 0,
    "current_data": None,
    "correct_answer": None,
    "results": []
}

# Function to randomise and customise questions
def get_randomised_questions():
    customised_questions = []
    for question in random.sample(questions, len(questions)):
        # Replace "_" and "-" with randomised values
        if "_" or "*" or "-" or "^" in question:
            question = question.replace("_", str(np.random.randint(1, NUM_MONTHS + 1)))
            question = question.replace("*", str(np.random.randint(1, NUM_MONTHS + 1)))
            question = question.replace("-", str(np.random.randint(1, NUM_SCHOOLS + 1)))
            question = question.replace("^", str(np.random.randint(1, NUM_SCHOOLS + 1)))
        customised_questions.append(question)
    return customised_questions

# Initial question list with randomised elements
question_list = get_randomised_questions()

# Ensure directories exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Generate random data
def generate_data():
    return np.random.randint(0, 100, (NUM_SCHOOLS, NUM_MONTHS))

# Adjusted calculate_answer function
def calculate_answer(question, data):
    # Generate answers based on each question type
    try:
        if "highest number of absences" in question:
            school_id = int(question.split()[-1][:-1]) - 1
            result = np.argmax(data[:, school_id]) + 1
            print(f"Correct answer calculated: {result}")
            return result 

        elif "lowest number of absences" in question:
            school_id = int(question.split()[-1][:-1]) - 1
            result = np.argmin(data[:, school_id]) + 1
            print(f"Correct answer calculated: {result}")
            return result 

        elif "absences across all schools the highest" in question:
            result = np.argmax(data.sum(axis=0)) + 1
            print(f"Correct answer calculated: {result}")
            return result

        elif "difference in absences between School" in question:
            school1 = int(question.split()[-13]) - 1
            school2 = int(question.split()[-10]) - 1
            month = int(question.split()[-7][:-1]) - 1
            difference = abs(data[school1, month] - data[school2, month])
            if difference < 10:
                result = "no"
            else:
                result = "yes"
            print(f"Correct answer calculated: {result}")
            return result 

        elif "more absences in Month" in question:
            school_id = int(question.split()[-10]) - 1
            month1 = int(question.split()[-1][:-1]) - 1
            month2 = int(question.split()[-4]) - 1
            if data[school_id, month1] > data[school_id, month2]:
                result = month1 + 1  
            else:
                result = month2 + 1
            print(f"Correct answer calculated: {result}")
            return result
        

        elif "greatest range in absences across schools" in question:
            result = np.argmax(data.max(axis=0) - data.min(axis=0)) + 1
            print(f"Correct answer calculated: {result}")
            return result

        elif "most consistent number of absences throughout the year" in question:
            result = np.argmin(np.std(data, axis=1)) + 1
            print(f"Correct answer calculated: {result}")
            return result

        elif "largest decrease in absences from one month to the next" in question:
            diffs = np.diff(data, axis=1)
            school, month = np.unravel_index(np.argmin(diffs), diffs.shape)
            result = school + 1
            print(f"Correct answer calculated: {result}")
            return result

        elif "second highest absences for School" in question:
            school_id = int(question.split()[-1][:-1]) - 1
            sorted_absences = np.argsort(data[school_id])
            result = sorted_absences[-2] + 1
            print(f"Correct answer calculated: {result}")
            return result

        elif "more absences in the first half of the year" in question:
            school_id = int(question.split()[-1][:-1]) - 1
            first_half_sum = data[school_id, :6].sum()
            second_half_sum = data[school_id, 6:].sum()
            if first_half_sum > second_half_sum:
                result = "first half" 
            else:
                result = "second half"
            print(f"Correct answer calculated: {result}")
            return result
            

    except ValueError:
        print("Error in parsing question for calculation.")

    return None

# Tkinter event handler for responses
def on_input(event=None):
    response_time = time.time() - start_time
    response = entry.get().strip()
    entry.delete(0, tk.END)
    
    correct = response == str(state["correct_answer"])  # Compare strings for accuracy
    
    # Save result with added error handling
    try:
        image_filename = save_plot(state["chart_type"])
        state["results"].append([
            state["chart_type"], 
            state["task_description"], 
            correct, 
            state["correct_answer"],  # Store correct answer for easy comparison
            response,                 # Store user response
            response_time, 
            image_filename
        ])
    except Exception as e:
        print("Error saving result:", e)

    state["current_trial"] += 1
    plt.close()
    root.after(1000, run_next_trial)

# Function to display plots and save image
def save_plot(chart_type):
    image_filename = f"{IMAGE_DIR}/trial_{state['current_trial'] + 1}_{chart_type}.png"
    plt.savefig(image_filename)
    return image_filename

# Heatmap and scatterplot functions
def show_heatmap(data):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(data, cmap='YlOrRd', aspect='auto')
    ax.set_xlabel('Month')
    ax.set_ylabel('School')
    ax.set_title("Pupil absences across 10 schools in Leeds")
    months = [f'Month {i+1}' for i in range(data.shape[1])]
    schools = [f'School {i+1}' for i in range(data.shape[0])]
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_xticklabels(months, rotation=45)
    ax.set_yticks(np.arange(data.shape[0]))
    ax.set_yticklabels(schools)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, str(data[i, j]), ha='center', va='center', color='black')
    embed_plot_in_tkinter(fig)

def show_scatterplot(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.tab10(np.linspace(0, 1, NUM_SCHOOLS))
    markers = ['o', '^', 'v', 's', 'D', 'x', '+', 'P', '*', 'H']

    for school_id in range(NUM_SCHOOLS):
        ax.scatter(np.arange(NUM_MONTHS), data[school_id], 
                   color=colors[school_id], 
                   marker=markers[school_id % len(markers)], 
                   label=f'School {school_id + 1}', s=100)

    ax.set_xlabel('Month')
    ax.set_ylabel('Absences')
    ax.set_title(f"Pupil abscences across 10 schools in Leeds")
    months_labels = [f'Month {i + 1}' for i in range(NUM_MONTHS)]
    ax.set_xticks(np.arange(NUM_MONTHS))
    ax.set_xticklabels(months_labels, rotation=45)
    ax.set_yticks(range(0, 101, 10))
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    ax.grid(False)

    embed_plot_in_tkinter(fig)

# Embedding plot into tkinter window
def embed_plot_in_tkinter(fig):
    for widget in plot_frame.winfo_children():
        widget.destroy()  # Clear previous plot

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    entry_label.config(text=f"Question: {state['task_description']}")
    entry.pack()
    submit_button.pack()

# Start a new trial
def run_next_trial():
    if state["current_trial"] >= 2 * NUM_TRIALS:
        save_results()
        root.quit()
        return
    
    # Regenerate questions every 10 trials
    if state["current_trial"] % NUM_TRIALS == 0:
        global question_list
        question_list = get_randomised_questions()

    # Switch between heatmap and scatterplot
    state["chart_type"] = 'scatterplot' if state["current_trial"] >= NUM_TRIALS else 'heatmap'
    state["current_data"] = generate_data()
    state["task_description"] = question_list[state["current_trial"] % len(question_list)]
    state["correct_answer"] = calculate_answer(state["task_description"], state["current_data"])
    
    global start_time
    start_time = time.time()

    if state["chart_type"] == 'heatmap':
        show_heatmap(state["current_data"])
    else:
        show_scatterplot(state["current_data"])

# Save results to CSV
def save_results():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(f'{RESULTS_DIR}/experiment_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ChartType', 'Task', 'Correct', 'CorrectAnswer', 'UserResponse', 'ResponseTime', 'ImageFilename'])
        writer.writerows(state["results"])
    print(f"Experiment complete. Results saved to {RESULTS_DIR}/experiment_results.csv.")

# Tkinter setup
root = tk.Tk()
root.title("Data Analysis Task")
plot_frame = ttk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=True)
entry_label = ttk.Label(root, text="", font=("Arial", 14))
entry_label.pack(pady=5)
entry = ttk.Entry(root, font=("Arial", 14), width=20)
submit_button = ttk.Button(root, text="Submit", command=on_input)
entry.bind('<Return>', on_input)
root.after(1000, run_next_trial)
root.mainloop()