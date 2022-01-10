from hypothesis.extra.django import TestCase
from classroom.models import Student, Classroom

from hypothesis import given, strategies as st
from mixer.backend.django import mixer
import pytest


pytestmark = pytest.mark.django_db


class TestStudentModel(TestCase):

    # def setUp(self):
    #         self.student1 = Student.objects.create(
    #         first_name="John", last_name="Doe", admission_number=12345
    #     )

    def test_student_can_be_created(self):
        
        student1 = mixer.blend(Student, first_name="John")
        
        student_result = Student.objects.last()  # getting the last student

        #self.assertEqual(student_result.first_name, "John")
        assert student_result.first_name == "John"

    def test_str_return(self):
        
        student1 = Student.objects.create(
            first_name="John", last_name="Doe", admission_number=1234, average_score=30
        )
        
        student_result = Student.objects.last()  # getting the last student
        
        #self.assertEqual(str(student_result), "John")
        assert str(student_result) == "John"
        

    # @given(st.characters())
    # def test_slugify(self, name):

    #     print(name, "name")

    #     student1 = mixer.blend(Student, first_name=name)
    #     student1.save()

    #     student_result = Student.objects.last()  # getting the last student

    #     assert len(str(student_result.username)) == len(name)


    @given(st.floats(min_value=0, max_value=40))
    def test_grade_fail(self, fail_score):

        print(fail_score, "this is failscore")

        student1 = mixer.blend(Student, average_score=fail_score)

        student_result = Student.objects.last()  # getting the last student

        assert student_result.get_grade() == "Fail"


    @given(st.floats(min_value=40, max_value=70))
    def test_grade_pass(self, pass_grade):

        student1 = mixer.blend(Student, average_score=pass_grade)

        student_result = Student.objects.last()  # getting the last student

        #self.assertEqual(student_result.get_grade(), "Pass")
        assert student_result.get_grade() == "Pass"



    @given(st.floats(min_value=70, max_value=100))
    def test_grade_excellent(self, excellent_grade):

        student1 = mixer.blend(Student, average_score=excellent_grade)

        student_result = Student.objects.last()  # getting the last student

        #self.assertEqual(student_result.get_grade(), "Excellent")
        assert student_result.get_grade() == "Excellent"
    
    
    @given(st.floats(min_value=100))
    def test_grade_error(self, error_grade):

        student1 = mixer.blend(Student, average_score=error_grade)

        student_result = Student.objects.last()  # getting the last student

        #self.assertEqual(student_result.get_grade(), "Excellent")
        assert student_result.get_grade() == "Error"



    def test_add_a_plus_b(self):
        a = 1
        b = 2
        c = a + b

        #self.assertEqual(c, 3)
        assert c == 3
        

class TestClassroomModel:
    def test_classroom_create(self):
        classroom = mixer.blend(Classroom, name="Math")
        
        classroom_result = Classroom.objects.last()  # getting the last classroom
        
        assert str(classroom_result) == "Math"