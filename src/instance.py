class Instance:
    """
    Represents an instance of a scheduling problem, initializing required attributes
    from provided data and setting up exam capacities based on student enrollment.

    Attributes:
        number_of_students (int): Total number of students.
        number_of_exams (int): Total number of exams.
        number_of_slots (int): Number of available time slots.
        number_of_rooms (int): Number of rooms available.
        room_capacities (list): List of capacities for each room.
        exams_to_students (list): List of tuples representing exam-to-student relationships.
        number_of_invigilators (int): Number of invigilators.
        student_exam_capacity (list): List indicating the number of students for each exam.
    
    Methods:
        __init__(attributes): Initializes the instance with the provided attributes.
    """
    
    def __init__(self, attributes, include_invigilator_constraints=False):
        """
        Initializes the Instance class with required and additional attributes.

        Args:
            attributes (dict): Dictionary containing the scheduling data, including 
                               number of students, exams, slots, rooms, room capacities,
                               and exam-to-student relationships.
        """
        
        # Retrieve the number of students from the attributes dictionary
        self.number_of_students = attributes.get("number_of_students", 0)
        
        # Retrieve the number of exams from the attributes dictionary
        self.number_of_exams = attributes.get("number_of_exams", 0)
        
        # Retrieve the number of slots from the attributes dictionary
        self.number_of_slots = attributes.get("number_of_slots", 0)
        
        # Retrieve the number of rooms from the attributes dictionary
        self.number_of_rooms = attributes.get("number_of_rooms", 0)
        
        # Retrieve the list of room capacities from the attributes dictionary
        self.room_capacities = attributes.get("room_capacities", [])
        
        # Retrieve the list of exam-to-student relationships from the attributes dictionary
        self.exams_to_students = attributes.get("exams_to_students", [])

        if include_invigilator_constraints:
            # Initialize the number of invigilators
            self.number_of_invigilators = 1
            
        # Initialize a list to track the number of students in each exam
        self.student_exam_capacity = [0] * self.number_of_exams
        
        # Populate the student_exam_capacity list based on exams_to_students data
        for exam, _ in self.exams_to_students:
            # Increment the student count for each exam in the relationship list
            self.student_exam_capacity[exam] += 1