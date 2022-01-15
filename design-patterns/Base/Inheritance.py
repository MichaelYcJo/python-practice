'''
상속은 클래스의 기능이 부모클래스로부터 파생되는 것을 일컫는다
파이썬은 자바와 다르게 다중상속을 지원한다.
'''

class A:
    def a1(self):
        print("a1")


class B(A):
    def b(self):
        print("b")


b = B()
b.a1()