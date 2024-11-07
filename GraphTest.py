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
    "Are there more absences in the first half of the year (1 to 6) or the second half (7 to 12) in School -?"
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
        # Exclude 8 from the list of possible months
        month_choices = [m for m in range(1, NUM_MONTHS + 1) if m != 8]
        
        # Sample two distinct months, excluding 8
        month1, month2 = random.sample(month_choices, 2)
        question = question.replace("_", str(month1)).replace("*", str(month2))
        
        # Sample two distinct schools as before
        school1, school2 = random.sample(range(1, NUM_SCHOOLS + 1), 2)
        question = question.replace("-", str(school1)).replace("^", str(school2))
        
        customised_questions.append(question)
    return customised_questions


# Initial question list with randomised elements
question_list = get_randomised_questions()

# Ensure directories exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Generate random data
def generate_data():
    # Generate random data
    data = np.random.randint(0, 100, (NUM_SCHOOLS, NUM_MONTHS)).astype(float)
    data[:, 7] = np.nan  # Set absences for August (8th month) to zero
    return data

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
    fig, ax = plt.subplots(figsize=(15, 9))

    #To set Nan cells as grey
    cmap = plt.cm.YlOrRd
    cmap.set_bad(color='lightgrey')
    
    # Create the heatmap
    cax = ax.imshow(data, cmap=cmap, aspect='auto')
    
    # Adjust layout to make space for the color bar
    fig.subplots_adjust(right=0.95)  # Adjusts figure to create space on the right

    # Add the color bar with custom positioning
    cbar = fig.colorbar(cax, ax=ax, orientation='vertical', fraction=0.046, pad=0.05)
    cbar.set_label('Number of Absences')  # Label for the color bar
    
    # Set labels and title
    ax.set_xlabel('Month', fontsize=11)
    ax.set_ylabel('School', fontsize=11)
    ax.set_title("Pupil absences across 10 schools in Leeds", fontsize=11)
    
    # Set ticks for months and schools
    months = [f'Month {i+1}' for i in range(data.shape[1])]
    schools = [f'School {i+1}' for i in range(data.shape[0])]
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_xticklabels(months, rotation=45)
    ax.set_yticks(np.arange(data.shape[0]))
    ax.set_yticklabels(schools)

    for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                if not np.isnan(data[i, j]):  # Only add text if the value is not NaN
                    ax.text(j, i, str(int(data[i, j])), ha='center', va='center', color='black')
    
    # Embed the plot in tkinter
    embed_plot_in_tkinter(fig)



def show_scatterplot(data):
    fig, ax = plt.subplots(figsize=(15, 9))
    colors = plt.cm.tab10(np.linspace(0, 1, NUM_SCHOOLS))

    markers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']  # Number labels for each school

    for school_id in range(NUM_SCHOOLS):
        x_values = np.arange(NUM_MONTHS)
        y_values = data[school_id]

        # Plotting invisible scatter points (just for positioning)
        ax.scatter(x_values, y_values, color=colors[school_id], s=0)

        # Adding text annotations as markers
        for x, y in zip(x_values, y_values):
            color = 'grey' if x == 7 else colors[school_id]  # Grey text for August
            ax.text(x, y, markers[school_id], ha='center', va='center', fontsize=14, fontweight='bold', color=color)

    ax.set_xlabel('Month', fontsize=11)
    ax.set_ylabel('Absences', fontsize=11)
    ax.set_title("Pupil absences across 10 schools in Leeds", fontsize=11)

    months_labels = [f'Month {i + 1}' for i in range(NUM_MONTHS)]
    ax.set_xticks(np.arange(NUM_MONTHS))
    ax.set_xticklabels(months_labels, rotation=45)
    ax.set_yticks(range(0, 101, 10))

    # Manually create a "legend" using text outside the plot area
    for school_id in range(NUM_SCHOOLS):
        ax.text(1.01, 0.98 - (school_id * 0.05), markers[school_id], transform=ax.transAxes,
                ha='left', va='center', fontsize=14, fontweight='bold', color=colors[school_id])
        ax.text(1.038, 0.98 - (school_id * 0.05), f'School {school_id + 1}', transform=ax.transAxes,
                ha='left', va='center', fontsize=11, color='black')

    ax.grid(False)

    embed_plot_in_tkinter(fig)


# Embedding plot into tkinter window
def embed_plot_in_tkinter(fig):
    for widget in plot_frame.winfo_children():
        widget.destroy()  # Clear previous plot

    #################

    # Ensuring figure in full size adjusts for screen size
    # Calculate available screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Leave space for entry and submit button (about 150 pixels)
    plot_height = screen_height - 150  

    # Convert pixel dimensions to inches (assuming 100 DPI)
    fig.set_size_inches(screen_width / 100, plot_height / 100)

    ####################


    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

    # Ensure the question label is updated and repacked
    entry_label.config(text=f"Question: {state['task_description']}")
    entry_label.pack()  # Make sure it is packed after updating the text
    entry.pack()
    submit_button.pack()



# Function to display a blank screen for a specified duration
def show_blank_screen(duration=1000):
    # Clear any existing plot
    for widget in plot_frame.winfo_children():
        widget.destroy()

    # Add a blank canvas as the blank screen
    blank_label = tk.Label(plot_frame, text="", background="white")
    blank_label.pack(fill=tk.BOTH, expand=True)
    
    # Hide the question, submit box, and button during the blank screen
    entry_label.pack_forget()
    entry.pack_forget()
    submit_button.pack_forget()

    # Wait for the specified duration before proceeding to the next trial
    root.after(duration, run_next_trial_actual)

# Separate actual trial execution from the blank screen timing
def run_next_trial():
    if state["current_trial"] >= 2 * NUM_TRIALS:
        save_results()
        root.quit()
        return
    # Display the blank screen for 1 second before showing the next graph
    show_blank_screen(1000)

# Function that actually runs the next trial after the blank screen
def run_next_trial_actual():
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

# Tkinter setup with fullscreen
root = tk.Tk()
root.title("Data Analysis Task")
root.attributes("-fullscreen", True)  # Enable fullscreen mode

# Create a frame to hold the plot and make it expandable
plot_frame = ttk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=True)  # Make it fill the entire window

entry_label = ttk.Label(root, text="", font=("Arial", 11))
entry_label.pack(pady=5)
entry = ttk.Entry(root, font=("Arial", 11), width=20)
submit_button = ttk.Button(root, text="Submit", command=on_input)
entry.bind('<Return>', on_input)

# Function to close fullscreen with Escape key
def quit_fullscreen(event=None):
    root.attributes("-fullscreen", False)  # Exit fullscreen mode

# Bind Escape key to quit fullscreen mode
root.bind("<Escape>", quit_fullscreen)

# Start the trials
root.after(1000, run_next_trial)
root.mainloop()
