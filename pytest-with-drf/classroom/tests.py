from django.test import TestCase
from classroom.models import Student


class TestStudentModel(TestCase):

    def setUp(self):
            self.student1 = Student.objects.create(
            first_name="John", last_name="Doe", admission_number=12345
        )

    def test_student_can_be_created(self):
        self.assertEqual(self.student1.first_name, "John")

    def test_str_return(self):
        self.assertEqual(str(self.student1), "John")

    def test_grade_fail(self):
        
        student1 = Student.objects.create(
            first_name="John", last_name="Doe", admission_number=1234, average_score=30
        )

        student_result = Student.objects.last()  # getting the last student
        
        self.assertEqual(student_result.get_grade(), "Fail")

    def test_grade_pass(self):

        student1 = Student.objects.create(
            first_name="John", last_name="Doe", admission_number=1234, average_score=60
        )

        student_result = Student.objects.last()  # getting the last student

        self.assertEqual(student_result.get_grade(), "Pass")

    def test_grade_excellent(self):

        student1 = Student.objects.create(
            first_name="John", last_name="Doe", admission_number=1234, average_score=90
        )

        student_result = Student.objects.last()  # getting the last student

        self.assertEqual(student_result.get_grade(), "Excellent")


    def test_add_a_plus_b(self):
        a = 1
        b = 2
        c = a + b

        self.assertEqual(c, 3)