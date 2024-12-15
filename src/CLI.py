
from z3 import *
from pathlib import Path
from timeit import default_timer as timer

from utils import parse_input, time_difference
from instance import Instance
from solver import solve

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    """
    Main entry point for executing scheduling problem solutions for multiple test instances.

    This script iterates over all test files in a specified directory, parses each file to extract
    instance attributes, creates an instance of the scheduling problem, and passes it to the solver.
    The results, including the solution and elapsed time, are printed for each test instance.

    Steps:
        1. Define the directory containing test files (`test_instances`).
        2. Prompt the user to choose whether to find multiple solutions or a single solution.
        3. Prompt the user to choose whether to include invigilator-related constraints.
        4. For each test file:
            a. Parse the file to extract instance attributes.
            b. Create an `Instance` object using the parsed attributes and selected options.
            c. Solve the instance using the `solve` function and output the result.
        5. Track and print the time elapsed for each instance and for the total execution.
        6. Print the total and average time elapsed for all instances after processing.
    """
    # Define the directory containing test instances
    tests_dir = Path("./test_instances")

    include_multiple_solutions = False
    include_invigilator_constraints = False

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

    # Variable for number of instances tested
    number_of_instances = 0

    # Start the total timer and calculate total time elapsed for all instances
    start_total = timer()

    # Iterate over each file in the test instances directory
    for test in tests_dir.iterdir():
        
        # Start a timer for the current instance
        start_instance = timer()
        
        # Process only files (ignore any folders or metadata files like .idea)
        if test.name != ".idea":

            # Increment the number of instances counter
            number_of_instances += 1

            # Parse input file to extract instance attributes
            attributes = parse_input(str(test))
            
            # Create an instance of the scheduling problem with parsed attributes
            instance = Instance(attributes, include_invigilator_constraints=include_invigilator_constraints)
            
            # Output the test file name and solve the instance
            print(f"{test.name}: ", end="")
            result = solve(instance, include_multiple_solutions=include_multiple_solutions)  # Solve the instance and retrieve the result
            
            # Print the result of solving the instance
            print(result)
        
        # End timer for the current instance and calculate elapsed time
        end_instance = timer()
        
        # Separator for readability between test results
        print("――――――――――――――――――――――――")

    # End the total timer and calculate total time elapsed for all instances
    end_total = timer()

    total_time_elapsed = time_difference(start_total, end_total, factor=1000)
    average_time_elapsed = total_time_elapsed / number_of_instances

    # Output the metrics for processing all test instances
    print(f'\nInstances Tested: {number_of_instances}')
    print(f'\nTotal Time Elapsed: {total_time_elapsed:.3f} milliseconds')
    print(f'\nAverage Time Elapsed per Instance: {average_time_elapsed:.3f} milliseconds')