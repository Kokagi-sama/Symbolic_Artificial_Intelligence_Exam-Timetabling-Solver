from timeit import default_timer as timer  # Import timer for tracking time elapsed
from z3 import *  # Import Z3 solver for constraint satisfaction problems
from constraint_handler import ConstraintHandler  # Import ConstraintHandler for applying constraints
from constraints import (
    RangeConstraint, ExamAssignmentConstraint, RoomCapacityConstraint, 
    NoConsecutiveExamsConstraint, InvigilatorMappingConstraint, 
    NoConsecutiveInvigilatorConstraint, StudentAssignmentsConstraint
)  # Import various constraint classes for scheduling problem
from declarations import Declarations  # Import the Declarations class for defining variables and expressions
from utils import time_difference  # Import utility function for calculating time differences

def solve(instance, include_multiple_solutions=False):
    """
    Solves an instance of the scheduling problem and returns the results in a formatted string.
    
    Args:
        instance (Instance): The instance of the scheduling problem containing attributes such as 
                             number of students, exams, slots, rooms, and relationships.
    
    Returns:
        str: A formatted result string containing details of the first solution and timing information.
    """
    
    result_text = ""  # Initialize result text to accumulate output details
    
    s = Solver()  # Create a Z3 solver instance

    # Initialize declarations based on instance attributes
    declarations = Declarations(instance)

    # List of constraints to apply, using predefined classes for each type of constraint
    constraints = [
        RangeConstraint(),
        StudentAssignmentsConstraint(),
        ExamAssignmentConstraint(),
        RoomCapacityConstraint(),
        NoConsecutiveExamsConstraint(),
        InvigilatorMappingConstraint(),
        NoConsecutiveInvigilatorConstraint()
    ]
    # Initialize constraint manager with selected constraints
    constraint_manager = ConstraintHandler(constraints)

    # Apply constraints to the solver with the current instance and declarations
    constraint_manager.apply_constraints(s, instance, declarations)

    # Loop variables for finding multiple solutions
    model_count = 0  # Track the number of solutions found
    thousand_plus_models = False  # Flag to indicate if model count reaches 1000
    first_instance_timer_end = None  # Timer to capture the end time of the first solution

    # Start the timer for the instance processing
    start_instance = timer()

    # Loop to find all possible solutions or until limit is reached
    while s.check() == sat:  # Check if the solution is satisfiable

        # Get the model for the current solution
        model = s.model()
    
        # If this is the first solution found
        if model_count == 0:  
            result_text += "sat\n"  # Indicate satisfiable status
            
            # Loop through exams to record room, slot, and invigilator assignments in result
            for ex in range(instance.number_of_exams):
                # Retrieve room assignment, if defined
                room = model.evaluate(declarations.ExamRoom(ex)) if hasattr(declarations, "ExamRoom") else "N/A"
                # Retrieve slot assignment, if defined
                slot = model.evaluate(declarations.ExamTime(ex)) if hasattr(declarations, "ExamTime") else "N/A"
                # Retrieve invigilator assignment, if defined
                invigilator = model.evaluate(declarations.ExamInvigilator(ex)) if hasattr(declarations, "ExamInvigilator") else "N/A"
                # Append exam details to the result text
                result_text += f"   Exam: {ex}, Room: {room}, Slot: {slot}, Invigilator: {invigilator}\n"

        # Exclude the current model from future solutions by adding constraints to the solver
        exclusion = Not(And([declarations.ExamRoom(ex) == model.eval(declarations.ExamRoom(ex)) for ex in range(instance.number_of_exams)] +
                            [declarations.ExamTime(ex) == model.eval(declarations.ExamTime(ex)) for ex in range(instance.number_of_exams)]))
        s.add(exclusion)

        # Capture the end time for the first instance if this is the first solution
        if model_count == 0:
            first_instance_timer_end = timer()
            
        # Increment model count
        model_count += 1

        # Stop after finding the first solution if the flag is False
        if not include_multiple_solutions:
            break

        # Stop if the model count reaches 1000
        if model_count >= 1000:
            thousand_plus_models = True  # Set flag to indicate more than 1000 solutions
            break

    # End the total timer for instance processing
    total_end_instance = timer()

    # Calculate time for the first solution if it was captured
    if first_instance_timer_end:
        first_instance_time = time_difference(start_instance, first_instance_timer_end, factor=1000)  # Milliseconds

    else:
        first_instance_time = 0  # Default to 0 if no solution was found

    # Calculate total instance time elapsed
    total_instance_time_elapsed = time_difference(start_instance, total_end_instance, factor=1000)  # Milliseconds

    # Check if no solutions were found
    if model_count == 0:
        result_text += "unsat\n"  # Indicate unsatisfiable status
    
    # Append details of alternate solutions and timing to result text
    result_text += f"Alternate Model(s) / Solution(s): {model_count - 1 if model_count != 0 else model_count} {'+' if thousand_plus_models else ''}\n"
    result_text += f"First Model Instance Time Elapsed: {first_instance_time:.2f} milliseconds\n"
    result_text += f"Total Instance Time Elapsed: {total_instance_time_elapsed:.2f} milliseconds\n"

    # Return the formatted result text
    return result_text