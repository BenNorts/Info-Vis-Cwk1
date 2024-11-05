import matplotlib.pyplot as plt
import numpy as np
import time
import csv
import tkinter as tk
from tkinter import simpledialog
import os

# Configuration parameters
NUM_TRIALS = 5
NUM_SCHOOLS = 10
NUM_MONTHS = 12
IMAGE_DIR = 'charts'  # Directory to save chart images
RESULTS_DIR = 'Results'  # Directory to save CSV results

# Ensure directories exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Data recording
results = []
current_trial = 0
chart_type = 'heatmap'  # Start with heatmap
task_description = ''
target_school_id = 0
current_data = None

# Generate random data
def generate_data():
    return np.random.randint(0, 100, (NUM_SCHOOLS, NUM_MONTHS))

# Event handler for text input
def on_input(response):
    global current_trial, chart_type, task_description, target_school_id
    response_time = time.time() - start_time
    correct = False

    if chart_type == 'heatmap':
        try:
            month = int(response.strip()) - 1
            if month >= 0 and month < NUM_MONTHS:
                target_value = np.max(current_data[target_school_id])
                if current_data[target_school_id, month] == target_value:
                    correct = True
        except ValueError:
            print("Invalid input. Please enter a valid month number.")

    elif chart_type == 'scatterplot':
        try:
            max_absence = np.max(current_data[target_school_id])
            response_value = float(response.strip())
            correct = abs(response_value - max_absence) < 5
        except ValueError:
            print("Invalid input. Please enter a valid absence number.")

    image_filename = save_plot(chart_type)
    results.append([chart_type, task_description, correct, response_time, image_filename])

    current_trial += 1
    plt.close()
    root.after(1000, run_next_trial)

# Helper function to save plot images
def save_plot(chart_type):
    image_filename = f"{IMAGE_DIR}/trial_{current_trial + 1}_{chart_type}.png"
    plt.savefig(image_filename)
    return image_filename

def show_heatmap(data, task):
    plt.imshow(data, cmap='YlOrRd', aspect='auto')
    plt.colorbar()
    plt.xlabel('Month')
    plt.ylabel('School')
    plt.title(f"Find {task}")
    months = [f'Month {i+1}' for i in range(data.shape[1])]
    schools = [f'School {i+1}' for i in range(data.shape[0])]
    plt.xticks(ticks=np.arange(data.shape[1]), labels=months, rotation=45)
    plt.yticks(ticks=np.arange(data.shape[0]), labels=schools)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            plt.text(j, i, str(data[i, j]), ha='center', va='center', color='black')

    save_plot(chart_type)
    plt.get_current_fig_manager().full_screen_toggle()
    plt.tight_layout()
    plt.show(block=False)

def show_scatterplot(data, task):
    colors = plt.cm.tab10(np.linspace(0, 1, NUM_SCHOOLS))
    markers = ['o', '^', 'v', 's', 'D', 'x', '+', 'P', '*', 'H']
    plt.figure(figsize=(12, 8))

    for school_id in range(NUM_SCHOOLS):
        plt.scatter(np.arange(NUM_MONTHS), data[school_id], 
                    color=colors[school_id], 
                    marker=markers[school_id % len(markers)], 
                    label=f'School {school_id + 1}', s=100)

    plt.xlabel('Month')
    plt.ylabel('Absences')
    plt.title(f"Find {task}")
    months_labels = [f'Month {i + 1}' for i in range(NUM_MONTHS)]
    plt.xticks(ticks=np.arange(NUM_MONTHS), labels=months_labels, rotation=45)
    plt.yticks(ticks=range(0, 101, 10))
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.grid(False)
    plt.get_current_fig_manager().full_screen_toggle()
    plt.tight_layout()
    plt.show(block=False)

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

    if chart_type == 'heatmap':
        show_heatmap(current_data, task_description)
    else:
        show_scatterplot(current_data, task_description)

    # Prompt user input
    if chart_type == 'heatmap':
        response = simpledialog.askstring("Input", f"Enter the month number with highest absence for School {target_school_id + 1}:")
    else:
        response = simpledialog.askstring("Input", f"Enter the highest absence for School {target_school_id + 1}:")
    
    if response is not None:
        on_input(response)

def save_results():
    with open(f'{RESULTS_DIR}/experiment_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ChartType', 'Task', 'Correct', 'ResponseTime', 'ImageFilename'])
        writer.writerows(results)
    print(f"Experiment complete. Results saved to {RESULTS_DIR}/experiment_results.csv.")

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    run_next_trial()
    root.mainloop()
