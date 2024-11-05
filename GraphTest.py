import matplotlib.pyplot as plt
import numpy as np
import time
import csv
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# Configuration parameters
NUM_TRIALS = 5
NUM_SCHOOLS = 10
NUM_MONTHS = 12
IMAGE_DIR = 'charts'
RESULTS_DIR = 'Results'

# Ensure directories exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Data recording
results = []
current_trial = 0
chart_type = 'heatmap'
task_description = ''
target_school_id = 0
current_data = None

# Generate random data
def generate_data():
    return np.random.randint(0, 100, (NUM_SCHOOLS, NUM_MONTHS))

def on_input(event=None):
    global current_trial, chart_type, task_description, target_school_id
    response_time = time.time() - start_time
    response = entry.get().strip()  # Get text from entry box
    entry.delete(0, tk.END)  # Clear input box after reading the value
    correct = False

    # If the chart is a heatmap, expect user to input a month number (1-12)
    if chart_type == 'heatmap':
        try:
            month = int(response) - 1  # Convert input to zero-indexed month
            if 0 <= month < NUM_MONTHS:
                # Find the target value (highest absence for the target school)
                target_value = np.max(current_data[target_school_id])
                # Check if the absence in the specified month matches the target value
                if current_data[target_school_id, month] == target_value:
                    correct = True
                else:
                    print(f"Incorrect: Highest absence for School {target_school_id + 1} "
                          f"is not in Month {month + 1}.")
            else:
                print("Invalid month number. Please enter a number between 1 and 12.")
        except ValueError:
            print("Invalid input. Please enter a valid month number.")

    # If the chart is a scatterplot, expect user to input an absence value (float)
    elif chart_type == 'scatterplot':
        try:
            response_value = float(response)
            # Get the maximum absence for the target school
            max_absence = np.max(current_data[target_school_id])
            # Check if user's response is within 5 of the max absence
            if abs(response_value - max_absence) < 5:  # Allows a small margin of error
                correct = True
            else:
                print(f"Incorrect: Maximum absence for School {target_school_id + 1} "
                      f"is {max_absence}. Your input was {response_value}.")
        except ValueError:
            print("Invalid input. Please enter a valid absence number.")

    # Create image filename for the current chart
    image_filename = save_plot(chart_type)
    
    # Append the results
    results.append([chart_type, task_description, correct, response_time, image_filename])

    # Move to the next trial
    current_trial += 1
    plt.close()  # Close the current plot
    root.after(1000, run_next_trial)  # Wait 1 second before showing the next trial


# Helper function to save plot images
def save_plot(chart_type):
    image_filename = f"{IMAGE_DIR}/trial_{current_trial + 1}_{chart_type}.png"
    plt.savefig(image_filename)
    return image_filename

def show_heatmap(data, task):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(data, cmap='YlOrRd', aspect='auto')
    ax.set_xlabel('Month')
    ax.set_ylabel('School')
    ax.set_title(f"Find {task}")

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

def show_scatterplot(data, task):
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
    ax.set_title(f"Find {task}")
    months_labels = [f'Month {i + 1}' for i in range(NUM_MONTHS)]
    ax.set_xticks(np.arange(NUM_MONTHS))
    ax.set_xticklabels(months_labels, rotation=45)
    ax.set_yticks(range(0, 101, 10))
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    ax.grid(False)

    embed_plot_in_tkinter(fig)

def embed_plot_in_tkinter(fig):
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    # Set up the input box below the plot
    entry_label.config(text=f"Enter your response for {task_description}:")
    entry.pack()
    submit_button.pack()

def run_next_trial():
    global start_time, chart_type, task_description, target_school_id, current_data
    if current_trial >= 2 * NUM_TRIALS:
        save_results()
        root.quit()
        return

    if current_trial == NUM_TRIALS:
        chart_type = 'scatterplot'

    current_data = generate_data()
    target_school_id = np.random.choice(range(NUM_SCHOOLS))
    task_description = f"highest absences for School {target_school_id + 1}"
    start_time = time.time()

    for widget in plot_frame.winfo_children():
        widget.destroy()  # Clear previous plot

    if chart_type == 'heatmap':
        show_heatmap(current_data, task_description)
    else:
        show_scatterplot(current_data, task_description)

def save_results():
    with open(f'{RESULTS_DIR}/experiment_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ChartType', 'Task', 'Correct', 'ResponseTime', 'ImageFilename'])
        writer.writerows(results)
    print(f"Experiment complete. Results saved to {RESULTS_DIR}/experiment_results.csv.")

# Tkinter main setup
root = tk.Tk()
root.title("Data Analysis Task")

# Frames to organize layout
plot_frame = ttk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=True)

entry_label = ttk.Label(root, text="", font=("Arial", 14))
entry_label.pack(pady=5)

entry = ttk.Entry(root, font=("Arial", 14), width=20)
submit_button = ttk.Button(root, text="Submit", command=on_input)
# Bind the Enter key to the on_input function
entry.bind('<Return>', on_input)
root.after(1000, run_next_trial)
root.mainloop()
