import matplotlib.pyplot as plt
import numpy as np
import time
import csv
import tkinter as tk
import os

# Configuration parameters
NUM_TRIALS = 5
NUM_SCHOOLS = 10
NUM_MONTHS = 12
IMAGE_DIR = 'charts'  # Directory to save chart images

# Ensure the image directory exists
os.makedirs(IMAGE_DIR, exist_ok=True)

# Data recording
results = []
current_trial = 0
chart_type = 'heatmap'  # Start with heatmap
task_description = ''  # Initialize task description
target_school_id = 0  # The target school for each heatmap trial
current_data = None  # Store current data for use in click validation

# Generate random data
def generate_data():
    return np.random.randint(0, 100, (NUM_SCHOOLS, NUM_MONTHS))

# Event handler for clicks
def on_click(event):
    global current_trial, chart_type, task_description, target_school_id
    response_time = time.time() - start_time

    # Determine if the click was correct
    correct = False
    if chart_type == 'heatmap' and event.xdata is not None and event.ydata is not None:
        # Convert click coordinates to array indices
        x_idx = int(event.xdata)
        y_idx = int(event.ydata)

        # Check if the clicked cell corresponds to the highest absence in the target school
        if y_idx == target_school_id:
            data = current_data
            target_value = np.max(data[target_school_id])  # highest absence for the target school
            if data[y_idx, x_idx] == target_value:
                correct = True

    elif chart_type == 'scatterplot' and event.xdata is not None:
        # Find the closest point in the scatter plot to where the user clicked
        clicked_month = int(round(event.xdata))
        clicked_absence = event.ydata
        
        # Get the correct answer for scatter plot task (highest absence for target school)
        data = current_data
        max_absence = np.max(data[target_school_id])
        correct = abs(clicked_absence - max_absence) < 5  # Allow some margin around the max point

    # Create image filename for the current chart
    image_filename = f"{IMAGE_DIR}/trial_{current_trial + 1}_{chart_type}.png"
    
    # Record result, now including task description and image filename
    results.append([chart_type, task_description, correct, response_time, image_filename])

    # Move to the next trial
    current_trial += 1
    plt.close()  # Close the current plot
    root.after(1000, run_next_trial)  # Wait 1 second before showing the next trial

# Updated show_heatmap function
def show_heatmap(data, task):
    plt.imshow(data, cmap='YlOrRd', aspect='auto')
    plt.colorbar()
    plt.xlabel('Month')
    plt.ylabel('School')
    plt.title(f"Find {task}")
    
    # Set custom ticks for months and schools
    months = [f'Month {i+1}' for i in range(data.shape[1])]
    schools = [f'School {i+1}' for i in range(data.shape[0])]
    plt.xticks(ticks=np.arange(data.shape[1]), labels=months, rotation=45)
    plt.yticks(ticks=np.arange(data.shape[0]), labels=schools)
    
    # Display numerical values in each cell
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            plt.text(j, i, str(data[i, j]), ha='center', va='center', color='black')

    # Connect the click event to capture responses
    plt.gcf().canvas.mpl_connect('button_press_event', on_click)
    
    # Save the figure as an image
    image_filename = f"{IMAGE_DIR}/trial_{current_trial + 1}_{chart_type}.png"
    plt.savefig(image_filename)

    # Set plot to full screen
    plt.get_current_fig_manager().full_screen_toggle()
    
    plt.tight_layout()
    plt.show(block=False)

# Show scatterplot with enhancements for ticks and school distinction
def show_scatterplot(data, task):
    # Define color map and distinct markers for each school
    colors = plt.cm.tab10(np.linspace(0, 1, NUM_SCHOOLS))  # Using tab10 for distinct colors
    markers = ['o', '^', 'v', 's', 'D', 'x', '+', 'P', '*', 'H', '<', '>', '1', '2', '3', '4', '|', '-', '_', '.', 'o']  # More distinct markers

    plt.figure(figsize=(12, 8))  # Set figure size for better clarity
    for school_id in range(NUM_SCHOOLS):
        # Scatter plot each school separately with unique color and marker
        plt.scatter(np.arange(NUM_MONTHS), data[school_id], 
                    color=colors[school_id], 
                    marker=markers[school_id % len(markers)], 
                    label=f'School {school_id + 1}', 
                    s=100)  # Adjust size for visibility
    
    # Set axis labels and title
    plt.xlabel('Month')
    plt.ylabel('Absences')
    plt.title(f"Find {task}")

    # Set ticks for each month
    months_labels = [f'Month {i + 1}' for i in range(NUM_MONTHS)]
    plt.xticks(ticks=np.arange(NUM_MONTHS), labels=months_labels, rotation=45)
    plt.yticks(ticks=range(0, 101, 10))  # Set y-ticks with a reasonable range for absences (0-100 as an example)
    
    # Show legend to distinguish between schools
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))  # Position legend outside plot for clarity

    # Remove gridlines
    plt.grid(False)  # Ensure gridlines are turned off

    # Set plot to full screen
    plt.get_current_fig_manager().full_screen_toggle()

    # Connect the click event to capture responses
    plt.gcf().canvas.mpl_connect('button_press_event', on_click)
    plt.tight_layout()
    plt.show(block=False)



# Run next trial
def run_next_trial():
    global start_time, chart_type, task_description, target_school_id, current_data
    if current_trial >= 2 * NUM_TRIALS:
        save_results()
        root.quit()  # End the experiment
        return
    
    # Alternate between heatmap and scatterplot
    if current_trial == NUM_TRIALS:
        chart_type = 'scatterplot'  # Switch to scatterplot after NUM_TRIALS

    current_data = generate_data()  # Store generated data for reference in click validation
    target_school_id = np.random.choice(range(NUM_SCHOOLS))
    task_description = f"highest absences for School {target_school_id + 1}"

    # Show the appropriate chart
    start_time = time.time()
    if chart_type == 'heatmap':
        show_heatmap(current_data, task_description)
    else:
        show_scatterplot(current_data, task_description)

# Save results to CSV

# Define the directory for saving results
RESULTS_DIR = 'Results'  # Change this to your desired directory

def save_results():
    with open(f'{RESULTS_DIR}/experiment_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ChartType', 'Task', 'Correct', 'ResponseTime', 'ImageFilename'])
        writer.writerows(results)
    print(f"Experiment complete. Results saved to {RESULTS_DIR}/experiment_results.csv.")

# Main experiment run
if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()  # Hide tkinter main window
    run_next_trial()  # Start the experiment
    root.mainloop()