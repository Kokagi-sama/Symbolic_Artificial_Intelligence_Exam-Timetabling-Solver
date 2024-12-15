from ortools.sat.python import cp_model
from pathlib import Path
from timeit import default_timer as timer
import re

class Instance:
    """
    Class to store the problem instance data, including the number of students, exams,
    rooms, slots, and other related attributes.
    """
    def __init__(self):
        self.number_of_students = 0
        self.number_of_exams = 0
        self.number_of_slots = 0
        self.number_of_rooms = 0
        self.number_of_invigilators = 0
        self.room_capacities = []
        self.exams_to_students = []
        self.student_exam_capacity = []

class SolutionCounter(cp_model.CpSolverSolutionCallback):
    """
    Callback class for the CP-SAT solver that tracks and handles solutions found during the search.
    """
    def __init__(self, exam_room, exam_time, exam_invigilator, include_multiple_solutions):
        """
        Initializes the solution counter callback.

        Args:
            exam_room: List of exam-room assignment variables.
            exam_time: List of exam-time assignment variables.
            exam_invigilator: List of invigilator assignment variables.
            include_multiple_solutions: Flag indicating whether to allow finding multiple solutions.
        """
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.exam_room = exam_room
        self.exam_time = exam_time
        self.exam_invigilator = exam_invigilator
        self.soln_count = 0
        self.solutions = []
        self.include_multiple_solutions = include_multiple_solutions
        self.start_time = timer()
        self.first_solution_time = None

    def on_solution_callback(self):
        """
        This function is called every time a solution is found.
        It stores the solution and stops search if the conditions are met.
        """
        self.soln_count += 1

        if self.soln_count == 1:
            self.first_solution_time = timer() - self.start_time

        soln = []
        for e in range(len(self.exam_room)):
            soln.append({
                'room': self.Value(self.exam_room[e]),
                'time': self.Value(self.exam_time[e]),
                'invigilator': self.Value(self.exam_invigilator[e]) if self.exam_invigilator else None
            })
        self.solutions.append(soln)

        if not self.include_multiple_solutions or self.soln_count >= 1000:
            self.StopSearch()

def read_file(filename):
    """
    Reads the problem instance data from a file and returns an Instance object containing
    all relevant information.

    Args:
        filename: Path to the input file.

    Returns:
        An Instance object populated with the data read from the file.
    """
    def read_attribute(name):
        """
        Helper function to read and parse an attribute from the input file.
        
        Args:
            name: The name of the attribute to read (e.g., "Number of students").
        
        Returns:
            The value of the attribute as an integer.
        
        Raises:
            Exception if the attribute value cannot be parsed correctly.
        """
        line = f.readline()
        match = re.match(f'{name}:\\s*(\\d+)$', line)
        if match:
            return int(match.group(1))
        else:
            raise Exception("Could not parse line {line}; expected the {name} attribute")

    instance = Instance()
    with open(filename) as f:
        instance.number_of_students = read_attribute("Number of students")
        instance.number_of_exams = read_attribute("Number of exams")
        instance.number_of_slots = read_attribute("Number of slots")
        instance.number_of_rooms = read_attribute("Number of rooms")
        instance.number_of_invigilators = 1

        for r in range(instance.number_of_rooms):
            instance.room_capacities.append(read_attribute(f"Room {r} capacity"))

        while True:
            l = f.readline()
            if l == "":
                break
            m = re.match('^\\s*(\\d+)\\s+(\\d+)\\s*$', l)
            if m:
                instance.exams_to_students.append((int(m.group(1)), int(m.group(2))))
            else:
                raise Exception(f'Failed to parse this line: {l}')

        for r in range(instance.number_of_exams):
            instance.student_exam_capacity.append(0)

        for r in instance.exams_to_students:
            instance.student_exam_capacity[r[0]] += 1
    return instance

def solve(instance, include_multiple_solutions, include_invigilator_constraints):
    """
    Solves the exam scheduling problem using the CP-SAT solver.

    Args:
        instance: The problem instance containing the number of students, exams, rooms, etc.
        include_multiple_solutions: Flag indicating whether to find multiple solutions.
        include_invigilator_constraints: Flag indicating whether to include invigilator-related constraints.
    """
    model = cp_model.CpModel()

    # Decision Variables
    exam_room = {}
    exam_time = {}
    exam_student = {}
    exam_invigilator = {}

    for e in range(instance.number_of_exams):
        exam_room[e] = model.NewIntVar(0, instance.number_of_rooms - 1, f'exam_room_{e}')
        exam_time[e] = model.NewIntVar(0, instance.number_of_slots - 1, f'exam_time_{e}')
        exam_invigilator[e] = model.NewIntVar(0, instance.number_of_invigilators - 1, f'exam_invigilator_{e}')

    # Create exam-student mapping variables
    for e in range(instance.number_of_exams):
        for s in range(instance.number_of_students):
            exam_student[(e, s)] = model.NewBoolVar(f'exam_{e}_student_{s}')

    # Set student assignments
    for exam, student in instance.exams_to_students:
        model.Add(exam_student[(exam, student)] == 1)

    # First and Second Constraint: Room and time slot assignment and no overlapping exams in rooms
    for t in range(instance.number_of_slots):
        for r in range(instance.number_of_rooms):
            exams_in_room_time = []
            for e in range(instance.number_of_exams):
                is_scheduled = model.NewBoolVar(f'is_scheduled_{e}_{r}_{t}')
                model.Add(exam_room[e] == r).OnlyEnforceIf(is_scheduled)
                model.Add(exam_time[e] == t).OnlyEnforceIf(is_scheduled)
                exams_in_room_time.append(is_scheduled)
            model.Add(sum(exams_in_room_time) <= 1)

    # Third Constraint: Room capacity
    for e in range(instance.number_of_exams):
        for r in range(instance.number_of_rooms):
            room_selected = model.NewBoolVar(f'room_{r}_selected_for_exam_{e}')
            model.Add(exam_room[e] == r).OnlyEnforceIf(room_selected)
            model.Add(exam_room[e] != r).OnlyEnforceIf(room_selected.Not())
            model.Add(instance.student_exam_capacity[e] <= instance.room_capacities[r]).OnlyEnforceIf(room_selected)

    # Fourth Constraint: No consecutive exams for students
    for s in range(instance.number_of_students):
        for e1 in range(instance.number_of_exams):
            for e2 in range(e1 + 1, instance.number_of_exams):
                has_both_exams = model.NewBoolVar(f'has_both_{e1}_{e2}_{s}')
                model.Add(exam_student[(e1, s)] + exam_student[(e2, s)] == 2).OnlyEnforceIf(has_both_exams)
                model.Add(exam_student[(e1, s)] + exam_student[(e2, s)] != 2).OnlyEnforceIf(has_both_exams.Not())
                
                model.Add(exam_time[e1] != exam_time[e2]).OnlyEnforceIf(has_both_exams)
                model.Add(exam_time[e1] != exam_time[e2] + 1).OnlyEnforceIf(has_both_exams)
                model.Add(exam_time[e1] != exam_time[e2] - 1).OnlyEnforceIf(has_both_exams)

    if include_invigilator_constraints:

        # Fifth Constraint: Each exam must have one invigilator
        for e in range(instance.number_of_exams):
            model.Add(exam_invigilator[e] >= 0)
            model.Add(exam_invigilator[e] < instance.number_of_invigilators)

        # Sixth Constraint: No consecutive invigilator assignments
        for e1 in range(instance.number_of_exams):
            for e2 in range(e1 + 1, instance.number_of_exams):
                same_invigilator = model.NewBoolVar(f'same_invigilator_{e1}_{e2}')
                model.Add(exam_invigilator[e1] == exam_invigilator[e2]).OnlyEnforceIf(same_invigilator)
                model.Add(exam_invigilator[e1] != exam_invigilator[e2]).OnlyEnforceIf(same_invigilator.Not())
                
                model.Add(exam_time[e1] != exam_time[e2]).OnlyEnforceIf(same_invigilator)
                model.Add(exam_time[e1] != exam_time[e2] + 1).OnlyEnforceIf(same_invigilator)
                model.Add(exam_time[e1] != exam_time[e2] - 1).OnlyEnforceIf(same_invigilator)

    solver = cp_model.CpSolver()
    result_text = ""
    start_instance = timer()

    solution_printer = SolutionCounter(exam_room, exam_time, exam_invigilator, include_multiple_solutions)
    status = solver.Solve(model, solution_printer)

    if status == cp_model.INFEASIBLE:
        result_text += "unsat\n"
    else:
        result_text += "sat\n"
        first_solution = solution_printer.solutions[0]
        for e in range(instance.number_of_exams):
            result_text += f"   Exam: {e}, Room: {first_solution[e]['room']}, "
            result_text += f"Slot: {first_solution[e]['time']}"
            if include_invigilator_constraints:
                result_text += f", Invigilator: {first_solution[e]['invigilator']}\n"
            else:
                result_text += f", Invigilator: N/A\n"

    thousand_plus = solution_printer.soln_count >= 1000
    alternate_solutions = max(0, solution_printer.soln_count - 1)
    result_text += f"Alternate Model(s) / Solution(s): {alternate_solutions}{' +' if thousand_plus else ''}\n"
    
    if solution_printer.first_solution_time is not None:
        result_text += f"First Model Instance Time Elapsed: {solution_printer.first_solution_time * 1000:.3f} milliseconds\n"

    end_instance = timer()

    total_time = end_instance - start_instance  # Calculate total time using timer
    result_text += f"Total Instance Time Elapsed: {total_time * 1000:.3f} milliseconds\n"

    print(result_text)

if __name__ == "__main__":

    include_multiple_solutions = False
    include_invigilator_constraints = False

    number_of_instances = 0

    while True:
        # Ask the user whether to find multiple solutions or a single solution
        print("Do you want to find multiple solutions for each test instance?")
        print("Enter 'Yes(Y)' for multiple solutions or 'No(N)' for a single solution.")
        include_multiple_solutions_input = input("Your choice (Yes(Y)/No(N)): ").strip().lower()

        if include_multiple_solutions_input not in ['yes', 'no', 'y', 'n']:
            print("Invalid input. Please run the script again and enter 'Yes(Y)' or 'No(N)'.")
            continue

        include_multiple_solutions = include_multiple_solutions_input == 'y' or include_multiple_solutions_input == 'yes'

        break

    while True:
        # Ask the user whether to include invigilator-related constraints
        print("Do you want to include invigilator-related constraints (mapping and no consecutive invigilator)?")
        print("Enter 'Yes(Y)' to include or 'No(N)' to exclude.")
        include_invigilator_constraints_input = input("Your choice (Yes(Y)/No(N)): ").strip().lower()

        if include_invigilator_constraints_input not in ['yes', 'no', 'y', 'n']:
            print("Invalid input. Please run the script again and enter 'Yes(Y)' or 'No(N)'.")
            continue

        include_invigilator_constraints = include_invigilator_constraints_input == 'y' or include_invigilator_constraints_input == 'yes'

        break

    print("――――――――――――――――――――――――\n")

    start = timer()

    # Read through all files in the folder
    tests_dir = Path("test_instances")
    for test in tests_dir.iterdir():
        if test.name != ".idea":
            number_of_instances += 1
            instance = read_file(str(test))
            print(f"{test.name}: ", end="")
            solve(instance, include_multiple_solutions, include_invigilator_constraints)

    end = timer()

    total_time_elapsed = (end-start)  * 1000
    average_time_elapsed = total_time_elapsed / number_of_instances

    print(f'\nInstances Tested: {number_of_instances}')
    print(f'\nTotal Time Elapsed: {total_time_elapsed:.3f} milliseconds')
    print(f'\nAverage Time Elapsed per Instance: {average_time_elapsed:.3f} milliseconds')