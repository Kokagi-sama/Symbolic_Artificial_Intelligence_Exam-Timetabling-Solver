from z3 import *

class Constraint:
    """
    Base constraint class providing an interface for adding constraints to the solver.
    
    Attributes:
        required_attributes (list): A list of attribute names that are required for the constraint to apply.
    
    Methods:
        add_to_solver(solver, instance, declarations): Interface method to add constraint logic to the solver.
    """
    required_attributes = []  # Define required attributes for inheriting constraint classes

    def add_to_solver(self, solver, instance, declarations):
        """
        Adds constraint logic to the solver. Must be implemented by subclasses.
        
        Args:
            solver (Solver): The Z3 solver instance to which the constraint will be added.
            instance (Instance): The problem instance containing attributes and data.
            declarations (Declarations): The variable and function declarations used in constraints.
        
        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Must be implemented by subclass.")

# Range Constraints
class RangeConstraint(Constraint):
    """
    Ensures that variables are within their defined ranges, such as student IDs, exam IDs, 
    time slots, rooms, and invigilators.

    Methods:
        add_to_solver(solver, instance, declarations): Adds range constraints to ensure values fall within valid ranges.
    """

    def add_to_solver(self, solver, instance, declarations):
        """
        Adds range constraints to the solver to ensure variable values fall within their specified ranges.

        Args:
            solver (Solver): The Z3 solver instance to which the constraints will be added.
            instance (Instance): The problem instance containing attribute ranges.
            declarations (Declarations): The variable and function declarations for the range constraints.
        """
        
        # Conditionally add each range constraint based on available instance attributes
        
        # Student range constraint, ensuring student IDs are within valid range
        if hasattr(instance, "number_of_students"):
            solver.add(ForAll([declarations.student], 
                              declarations.Student_Range(declarations.student) == 
                              And(declarations.student >= 0, declarations.student < instance.number_of_students)))

        # Exam range constraint, ensuring exam IDs are within valid range
        if hasattr(instance, "number_of_exams"):
            solver.add(ForAll([declarations.exam], 
                              declarations.Exam_Range(declarations.exam) == 
                              And(declarations.exam >= 0, declarations.exam < instance.number_of_exams)))

        # Time slot range constraint, ensuring time slot IDs are within valid range
        if hasattr(instance, "number_of_slots"):
            solver.add(ForAll([declarations.ts], 
                              declarations.TimeSlot_Range(declarations.ts) == 
                              And(declarations.ts >= 0, declarations.ts < instance.number_of_slots)))

        # Room range constraint, ensuring room IDs are within valid range
        if hasattr(instance, "number_of_rooms"):
            solver.add(ForAll([declarations.room], 
                              declarations.Room_Range(declarations.room) == 
                              And(declarations.room >= 0, declarations.room < instance.number_of_rooms)))

        # Invigilator range constraint, ensuring invigilator IDs are within valid range
        if hasattr(instance, "number_of_invigilators"):
            solver.add(ForAll([declarations.invigilator], 
                              declarations.Invigilator_Range(declarations.invigilator) == 
                              And(declarations.invigilator >= 0, declarations.invigilator < instance.number_of_invigilators)))

# Student assignments
class StudentAssignmentsConstraint(Constraint):
    """
    Assigns students to exams based on provided data, ensuring that each student is assigned 
    to the specified exams.

    Attributes:
        required_attributes (list): Specifies that "exams_to_students" is required for this constraint.
    
    Methods:
        add_to_solver(solver, instance, declarations): Adds student-to-exam assignment constraints to the solver.
    """
    required_attributes = ["exams_to_students"]  # Specify that exams_to_students attribute is required

    def add_to_solver(self, solver, instance, declarations):
        """
        Adds student assignment constraints to the solver, mapping each student to their specified exams.

        Args:
            solver (Solver): The Z3 solver instance to which the constraints will be added.
            instance (Instance): The problem instance containing student-to-exam relationships.
            declarations (Declarations): The variable and function declarations used for assignments.
        """
        # Loop through each exam-to-student pair and add a constraint to the solver
        for exam, student in instance.exams_to_students:
            solver.add(declarations.ExamStudent(exam, student))

# First and second constraint
class ExamAssignmentConstraint(Constraint):
    """
    Ensures each exam is assigned to exactly one room and one time slot, without conflicts.
    
    Methods:
        add_to_solver(solver, instance, declarations): Adds assignment constraints for exams to rooms and slots.
    """
    required_attributes = ["number_of_exams", "number_of_rooms", "number_of_slots"]

    def add_to_solver(self, solver, instance, declarations):
        """
        Adds constraints to ensure that each exam is assigned to a unique room and slot.
        
        Args:
            solver (Solver): The Z3 solver instance.
            instance (Instance): The problem instance with data on exams, rooms, and slots.
            declarations (Declarations): The variable and function declarations for the constraints.
        """
        # Enforce each exam to be assigned a unique room and slot with no overlaps
        solver.add(
            ForAll([declarations.exam],
                Implies(
                    declarations.Exam_Range(declarations.exam),
                    Exists([declarations.room, declarations.ts],
                        And(
                            # Ensure room and time slot are within defined ranges
                            declarations.Room_Range(declarations.room),
                            declarations.TimeSlot_Range(declarations.ts),
                            # Assign the exam to a specific room and time slot
                            declarations.ExamTime(declarations.exam) == declarations.ts,
                            declarations.ExamRoom(declarations.exam) == declarations.room,
                            # Ensure no other exams are scheduled in the same room and slot
                            ForAll([declarations.nex],
                                Implies(
                                    declarations.Exam_Range(declarations.nex),
                                    Implies(
                                        And(declarations.ExamRoom(declarations.nex) == declarations.room, 
                                            declarations.ExamTime(declarations.nex) == declarations.ts),
                                        declarations.exam == declarations.nex
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )

class RoomCapacityConstraint(Constraint):
    """
    Ensures that the room capacity is not exceeded for each exam.
    
    Methods:
        add_to_solver(solver, instance, declarations): Adds constraints to keep the student count within room capacity.
    """
    required_attributes = ["number_of_exams", "number_of_rooms", "room_capacities", "student_exam_capacity"]

    def add_to_solver(self, solver, instance, declarations):
        """
        Adds constraints to ensure each exam is assigned to a room that can accommodate all attending students.
        
        Args:
            solver (Solver): The Z3 solver instance.
            instance (Instance): The problem instance with data on room capacities and student counts.
            declarations (Declarations): The variable and function declarations for the constraints.
        """
        # For each exam and room, ensure that the room can hold the number of students attending the exam
        for exam in range(instance.number_of_exams):
            for room in range(instance.number_of_rooms):
                solver.add(Implies(declarations.ExamRoom(exam) == room, 
                                   instance.student_exam_capacity[exam] <= instance.room_capacities[room]))

# Fourth constraint
class NoConsecutiveExamsConstraint(Constraint):
    """
    Prevents students from having exams scheduled in consecutive time slots.
    
    Methods:
        add_to_solver(solver, instance, declarations): Adds constraints to avoid consecutive exams for students.
    """
    required_attributes = ["number_of_students", "number_of_exams", "number_of_slots", "exams_to_students"]

    def add_to_solver(self, solver, instance, declarations):
        """
        Adds constraints to ensure that students do not have exams in consecutive time slots.
        
        Args:
            solver (Solver): The Z3 solver instance.
            instance (Instance): The problem instance with student-exam relationships.
            declarations (Declarations): The variable and function declarations for the constraints.
        """
        solver.add(
            ForAll(
                [declarations.student, declarations.exam, declarations.nex, declarations.ts, declarations.nts],
                Implies(
                    And(
                        # Ensure variables are within valid ranges and exams are distinct
                        declarations.Student_Range(declarations.student),
                        declarations.Exam_Range(declarations.exam),
                        declarations.Exam_Range(declarations.nex),
                        declarations.TimeSlot_Range(declarations.ts),
                        declarations.TimeSlot_Range(declarations.nts),
                        Not(declarations.exam == declarations.nex)
                    ),
                    Implies(
                        And(
                            # Check time slots and student assignment for consecutive exams
                            declarations.ExamTime(declarations.exam) == declarations.ts,
                            declarations.ExamTime(declarations.nex) == declarations.nts,
                            declarations.ExamStudent(declarations.exam, declarations.student),
                            declarations.ExamStudent(declarations.nex, declarations.student)
                        ),
                        # Ensure the exams are not scheduled in consecutive or identical slots
                        And(declarations.ts + 1 != declarations.nts, 
                            declarations.ts - 1 != declarations.nts, 
                            declarations.ts != declarations.nts)
                    )
                )
            )
        )

# Fifth constraint
class InvigilatorMappingConstraint(Constraint):
    """
    Ensures that each exam has exactly one assigned invigilator.
    
    Methods:
        add_to_solver(solver, instance, declarations): Adds constraints for assigning an invigilator to each exam.
    """
    required_attributes = ["number_of_exams", "number_of_invigilators"]

    def add_to_solver(self, solver, instance, declarations):
        """
        Adds constraints to ensure that each exam has one unique invigilator.
        
        Args:
            solver (Solver): The Z3 solver instance.
            instance (Instance): The problem instance with data on exams and invigilators.
            declarations (Declarations): The variable and function declarations for the constraints.
        """
        # Assign exactly one invigilator to each exam, with invigilator IDs in range
        solver.add(ForAll([declarations.exam], Exists([declarations.invigilator], 
            And(
                declarations.Invigilator_Range(declarations.invigilator), 
                declarations.ExamInvigilator(declarations.exam) == declarations.invigilator
            )
        )))

# Sixth Constraint
class NoConsecutiveInvigilatorConstraint(Constraint):
    """
    Prevents the same invigilator from being assigned to consecutive slots for different exams.
    
    Methods:
        add_to_solver(solver, instance, declarations): Adds constraints to avoid consecutive assignments for invigilators.
    """
    required_attributes = ["number_of_exams", "number_of_slots", "number_of_invigilators"]

    def add_to_solver(self, solver, instance, declarations):
        """
        Adds constraints to prevent the same invigilator from being assigned to consecutive time slots for different exams.
        
        Args:
            solver (Solver): The Z3 solver instance.
            instance (Instance): The problem instance with data on exams, slots, and invigilators.
            declarations (Declarations): The variable and function declarations for the constraints.
        """
        solver.add(
            ForAll(
                [declarations.exam, declarations.nex, declarations.ts, declarations.nts, declarations.invigilator],
                Implies(
                    And(
                        # Ensure valid ranges for exams, slots, and invigilators, with distinct exams
                        declarations.Exam_Range(declarations.exam),
                        declarations.Exam_Range(declarations.nex),
                        declarations.TimeSlot_Range(declarations.ts),
                        declarations.TimeSlot_Range(declarations.nts),
                        declarations.Invigilator_Range(declarations.invigilator),
                        Not(declarations.exam == declarations.nex),  # Different exams
                        declarations.ExamInvigilator(declarations.exam) == declarations.invigilator,
                        declarations.ExamInvigilator(declarations.nex) == declarations.invigilator,
                        declarations.ExamTime(declarations.exam) == declarations.ts,
                        declarations.ExamTime(declarations.nex) == declarations.nts
                    ),
                    # Ensure that the invigilator is not assigned to exams in consecutive or identical slots
                    And(
                        declarations.ts != declarations.nts,
                        declarations.ts + 1 != declarations.nts,
                        declarations.ts - 1 != declarations.nts
                    )
                )
            )
        )