
# Exam Timetabling Solver

This project provides a solution to the exam timetabling problem using Python and the Z3 solver for constraint satisfaction. A graphical user interface (GUI) allows users to select specific problem instances and view results in a user-friendly format.

## Overview
The solution uses Python and the Z3 solver to satisfy constraints involved in exam scheduling. A GUI is available to enable users to select instances and see results in real-time. To ensure that the GUI remains responsive, a subprocess approach is implemented to avoid threading issues with Z3, allowing multiple instances to be solved concurrently. Also, an alternative solver made in Ortools is also available to make comparison between solvers' runtime.

### Features
- **Multiple Solutions**: The solver iteratively excludes each solution to find alternative results where possible.
- **Subprocess Management**: Uses subprocesses to maintain GUI responsiveness and prevent threading issues with Z3.
- **Flexible Execution Options**: Run the solver via command-line interface (CLI) or GUI.

## Setup and Execution

### 1. Create a Virtual Environment
It is recommended to create a virtual environment to manage dependencies in isolation.

```bash
python -m venv venv
```

### 2. Install Required Dependencies
After activating the virtual environment, install all required packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 3. Run the Solver
You have two options for running the solver:

- **CLI Mode**: Run `CLI.py` to process all instances in a specified folder without a GUI.
  
  ```bash
  python src/CLI.py
  ```

- **GUI Mode**: Run `GUI.py` to launch the graphical interface, allowing users to select specific test instances, initiate the solver, and view results.

  ```bash
  python src/GUI.py
  ```

- **Alternative solver**: Run `alt_ortools.py` to process all instances in a specified folder with ortools.

  ```bash
  python src/alt_ortools.py
  ```

## Dependencies
- Python 3.x
- Z3 Solver
- PyQt5 (for GUI)

## Notes
The use of subprocesses ensures the GUI remains responsive, even when solving multiple instances. The solver can provide multiple solutions by iteratively excluding found solutions from further checks.

---
