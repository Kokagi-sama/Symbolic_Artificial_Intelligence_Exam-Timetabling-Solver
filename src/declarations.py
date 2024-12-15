from z3 import *  # Import Z3 library for constraint declarations

class Declarations:
    """
    Initializes and defines Z3 declarations for variables and functions required in the scheduling problem.
    Declarations are conditionally created based on the attributes of the given instance.

    Attributes:
        exam (Int): Integer variable for exams.
        room (Int): Integer variable for rooms.
        ts (Int): Integer variable for time slots.
        nex (Int): Integer variable representing the next exam.
        nts (Int): Integer variable representing the next time slot.
        student (Int): Integer variable for students.
        invigilator (Int): Integer variable for invigilators.
        Student_Range (Function, optional): Function defining the range of valid student IDs.
        Exam_Range (Function, optional): Function defining the range of valid exam IDs.
        Room_Range (Function, optional): Function defining the range of valid room IDs.
        TimeSlot_Range (Function, optional): Function defining the range of valid time slots.
        Invigilator_Range (Function, optional): Function defining the range of valid invigilator IDs.
        ExamRoom (Function, optional): Function mapping each exam to a room.
        ExamTime (Function, optional): Function mapping each exam to a time slot.
        ExamStudent (Function, optional): Function indicating student assignment to exams.
        ExamInvigilator (Function, optional): Function mapping each exam to an invigilator.
    
    Methods:
        __init__(instance): Initializes variable and function declarations based on instance attributes.
    """
    
    def __init__(self, instance):
        """
        Initializes the Declarations class with Z3 variables and functions based on instance attributes.
        
        Args:
            instance (Instance): The instance of the scheduling problem, which contains various attributes 
                                 such as number of students, exams, rooms, and specific mappings.
        """
        
        # Basic declarations for general scheduling variables
        self.exam = Int('exam')  # Integer variable for exam IDs
        self.room = Int('room')  # Integer variable for room IDs
        self.ts = Int('ts')  # Integer variable for time slot IDs
        self.nex = Int('nex')  # Integer variable representing the next exam
        self.nts = Int('nts')  # Integer variable representing the next time slot
        self.student = Int('student')  # Integer variable for student IDs
        self.invigilator = Int('invigilator')  # Integer variable for invigilator IDs

        # Conditionally define range functions based on instance attributes
        if hasattr(instance, "number_of_students"):
            # Define function for valid student ID range
            self.Student_Range = Function('Student_Range', IntSort(), BoolSort())
        if hasattr(instance, "number_of_exams"):
            # Define function for valid exam ID range
            self.Exam_Range = Function('Exam_Range', IntSort(), BoolSort())
        if hasattr(instance, "number_of_rooms"):
            # Define function for valid room ID range
            self.Room_Range = Function('Room_Range', IntSort(), BoolSort())
        if hasattr(instance, "number_of_slots"):
            # Define function for valid time slot ID range
            self.TimeSlot_Range = Function('TimeSlot_Range', IntSort(), BoolSort())
        if hasattr(instance, "number_of_invigilators"):
            # Define function for valid invigilator ID range
            self.Invigilator_Range = Function('Invigilator_Range', IntSort(), BoolSort())

        # Conditionally define functions based on multiple attributes
        if hasattr(instance, "room_capacities") and hasattr(instance, "student_exam_capacity"):
            # Define function to map exams to rooms
            self.ExamRoom = Function('ExamRoom', IntSort(), IntSort())
        if hasattr(instance, "number_of_slots"):
            # Define function to map exams to time slots
            self.ExamTime = Function('ExamTime', IntSort(), IntSort())
        if hasattr(instance, "exams_to_students"):
            # Define function to indicate if a student is assigned to an exam
            self.ExamStudent = Function('ExamStudent', IntSort(), IntSort(), BoolSort())
        if hasattr(instance, "number_of_invigilators"):
            # Define function to map exams to invigilators
            self.ExamInvigilator = Function('ExamInvigilator', IntSort(), IntSort())