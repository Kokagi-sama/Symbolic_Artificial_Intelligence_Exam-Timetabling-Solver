import os
import sys
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QListWidget, QListWidgetItem, QCheckBox
from timeit import default_timer as timer
from utils import time_difference

class SolverApp(QMainWindow):
    """
    GUI application for selecting, solving, and displaying results of Z3 scheduling problem instances.

    Attributes:
        main_widget (QWidget): The main widget containing the layout.
        layout (QVBoxLayout): Vertical layout for organizing widgets.
        select_button (QPushButton): Button to select test instances.
        solve_button (QPushButton): Button to solve the selected test instances.
        multiple_solutions_checkbox (QCheckbox): Checkbox to toggle between single or multiple solutions
        invigilator_constraints_checkbox (QCheckbox): Checkbox to toggle between adding the additional invigilator constraints or not
        result_label (QLabel): Label for the results display area.
        result_display (QTextEdit): Text area to display the results of each test instance.
        selected_files_list (QListWidget): List widget displaying selected test instance files.
        selected_test_paths (list): Stores paths of selected test instance files.
    
    Methods:
        select_instances(): Opens a file dialog to select test instance files.
        solve_instances(): Runs the selected test instances in separate subprocesses and displays results.
    """
    
    def __init__(self):
        """
        Initializes the SolverApp window, setting up the layout and widgets for selecting and solving test instances.
        """
        super().__init__()
        self.setWindowTitle("Z3 Scheduling Solver")
        self.setGeometry(100, 100, 800, 600)
        
        # Main layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        
        # Instance selection button
        self.select_button = QPushButton("Select Test Instances")
        self.select_button.clicked.connect(self.select_instances)
        self.layout.addWidget(self.select_button)
        
        # Solve button
        self.solve_button = QPushButton("Solve Selected Instances")
        self.solve_button.clicked.connect(self.solve_instances)
        self.layout.addWidget(self.solve_button)

        # Options
        self.multiple_solutions_checkbox = QCheckBox("Find Multiple Solutions")
        self.layout.addWidget(self.multiple_solutions_checkbox)
        
        self.invigilator_constraints_checkbox = QCheckBox("Include Invigilator Constraints")
        self.layout.addWidget(self.invigilator_constraints_checkbox)
        
        # Results display area
        self.result_label = QLabel("Results:")
        self.layout.addWidget(self.result_label)
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.layout.addWidget(self.result_display)
        
        # List to display selected files
        self.selected_files_list = QListWidget()
        self.layout.addWidget(self.selected_files_list)
        
        # Store paths of selected test instances
        self.selected_test_paths = []

    def select_instances(self):
        """
        Opens a file dialog to select test instances and displays the selected file names in the list widget.
        """
        files, _ = QFileDialog.getOpenFileNames(self, "Select Test Instances", "./test_instances", "Text Files (*.txt)")
        self.selected_test_paths = files
        self.selected_files_list.clear()
        # Add each selected file to the list widget
        for file in files:
            self.selected_files_list.addItem(QListWidgetItem(Path(file).name))

    def solve_instances(self):
        """
        Runs each selected test instance in a separate subprocess using solver_worker.py,
        captures the result or error output, and displays it in the result display area.
        """
        # Check if any test instances were selected
        if not self.selected_test_paths:
            self.result_display.append("No test instances selected!")
            return

        self.result_display.clear()  # Clear previous results

        # Detect venv
        venv = os.path.join(os.getenv("VIRTUAL_ENV", ""), "bin" if os.name != "nt" else "Scripts", "python")
        python_env = venv if os.path.exists(venv) else sys.executable

        # Get user options
        include_multiple_solutions = self.multiple_solutions_checkbox.isChecked()
        include_invigilator_constraints = self.invigilator_constraints_checkbox.isChecked()

        # Start total timer
        start_total = timer()
        
        # Number of instances
        number_of_instances = len(self.selected_test_paths)

        # Run each test instance in a separate subprocess
        for test_path in self.selected_test_paths:
            test_name = Path(test_path).name  # Get the file name of the test instance
            
            # Prepare the arguments
            args = [
                python_env, os.path.join('src', 'solver_worker.py'),
                test_path,
                str(include_multiple_solutions),
                str(include_invigilator_constraints)
            ]

            # Run solver_worker.py with test_path as an argument
            result = subprocess.run(
                args,
                capture_output=True,
                text=True
            )
            
            # Check if the subprocess was successful
            if result.returncode == 0:
                # Process the output from solver_worker.py
                output_lines = result.stdout.strip().splitlines()
                sat_unsat = output_lines[0] if output_lines else "No output!"
                remaining_output = "\n".join(output_lines[1:]) if len(output_lines) > 1 else ""
                
                # Display sat/unsat status with the test file name
                self.result_display.append(f"{test_name}: {sat_unsat}")
                
                # Display additional output if present
                if remaining_output:
                    self.result_display.append(remaining_output)
            else:
                # Display error message if the subprocess returned a non-zero exit code
                self.result_display.append(f"{test_name}: An error occurred")
                self.result_display.append(result.stderr.strip())
            
            # Add separator for readability
            self.result_display.append("――――――――――――――――――――――――")

        # End total timer and calculate total elapsed time
        end_total = timer()
        total_time_elapsed = time_difference(start_total, end_total, factor=1000)  # in milliseconds
        average_time_elapsed = total_time_elapsed / number_of_instances

        # Display metrics
        self.result_display.append(f"\nInstances Tested: {number_of_instances}")
        self.result_display.append(f"\nTotal Time Elapsed: {total_time_elapsed:.3f} milliseconds")
        self.result_display.append(f"\nAverage Time Elapsed per Instance: {average_time_elapsed:.3f} milliseconds")

# Main loop to run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    solver_app = SolverApp()
    solver_app.show()
    sys.exit(app.exec_())