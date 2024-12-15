import re

def parse_input(filename):
    """
    Parses an input file to extract scheduling information.
    
    Args:
        filename (str): The path to the input file containing scheduling data.
    
    Returns:
        dict: A dictionary containing the following attributes:
            - number_of_students (int): Total number of students.
            - number_of_exams (int): Total number of exams.
            - number_of_slots (int): Number of available time slots.
            - number_of_rooms (int): Number of rooms available.
            - room_capacities (list): List of capacities for each room.
            - exams_to_students (list): List of tuples representing exam-to-student relationships.
    """
    
    # Initialize dictionary to store attributes with default values
    attributes = {
        "number_of_students": None,      # Total number of students
        "number_of_exams": None,         # Total number of exams
        "number_of_slots": None,         # Number of time slots available
        "number_of_rooms": None,         # Number of rooms available
        "room_capacities": [],           # List of capacities for each room
        "exams_to_students": []          # List of tuples linking exams to students
    }

    # Open the file in read mode
    with open(filename) as f:
        # Loop through each line in the file
        for line in f:
            # Remove leading and trailing whitespace from the line
            line = line.strip()
            
            # Match line for the number of students
            if match := re.match(r'Number of students:\s*(\d+)', line):
                # Set the number of students in the attributes dictionary
                attributes["number_of_students"] = int(match.group(1))
            
            # Match line for the number of exams
            elif match := re.match(r'Number of exams:\s*(\d+)', line):
                # Set the number of exams in the attributes dictionary
                attributes["number_of_exams"] = int(match.group(1))
            
            # Match line for the number of slots
            elif match := re.match(r'Number of slots:\s*(\d+)', line):
                # Set the number of slots in the attributes dictionary
                attributes["number_of_slots"] = int(match.group(1))
            
            # Match line for the number of rooms
            elif match := re.match(r'Number of rooms:\s*(\d+)', line):
                # Set the number of rooms in the attributes dictionary
                attributes["number_of_rooms"] = int(match.group(1))
            
            # Match line for room capacity (Room number and capacity)
            elif match := re.match(r'Room (\d+) capacity:\s*(\d+)', line):
                # Append the room capacity to the list in the order they appear
                attributes["room_capacities"].append(int(match.group(2)))
            
            # Match line for exam-to-student relationships (exam and student IDs)
            elif match := re.match(r'(\d+)\s+(\d+)', line):
                # Add the tuple of exam and student IDs to the exams_to_students list
                attributes["exams_to_students"].append((int(match.group(1)), int(match.group(2))))
            
            # Ignore any lines that don't match the expected format

    # Return the attributes dictionary with all parsed data
    return attributes

def time_difference(start_time, end_time, factor=1000):
    """
    Calculates the time difference between two points in time, scaled by a factor.
    
    Args:
        start_time (float): The starting time in seconds.
        end_time (float): The ending time in seconds.
        factor (int, optional): The scaling factor to convert the time difference. Default is 1000.
    
    Returns:
        int: The scaled time difference in milliseconds or as defined by the factor.
    """
    
    # Calculate the time difference, apply scaling, and convert to integer
    return (end_time - start_time) * factor