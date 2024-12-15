import sys
from utils import parse_input  
from instance import Instance  
from solver import solve       

def main(test_path):
    """
    Main function to handle parsing, instance creation, and solving.
    
    Args:
        test_path (str): The file path of the test input data.
    
    This function parses the input data from a file, creates an instance of the 
    scheduling problem, and passes it to the solver function. The result is then 
    printed to standard output.
    """
    
    # Parse input file to extract scheduling attributes
    attributes = parse_input(test_path)
    
    # Create an instance of the problem with the parsed attributes
    instance = Instance(attributes, include_invigilator_constraints=include_invigilator_constraints)
    
    # Solve the instance and get the result
    result = solve(instance, include_multiple_solutions=include_multiple_solutions)
    
    # Output the result to stdout
    print(result)

# Entry point for the script
if __name__ == "__main__":
    # Retrieve the test file path from command-line arguments
    test_path = sys.argv[1]
    include_multiple_solutions = sys.argv[2].lower() == "true"
    include_invigilator_constraints = sys.argv[3].lower() == "true"
    
    # Execute the main function with the provided test file path
    main(test_path)