'''
객체나 클래스를 더 복잡한 자료구조나 모듈로 묶는 행위
컴포지션을 통해 특정 객체는 다른 모듈의 함수를 호출할 수 있다.
상속없이 외부기능 사용이 가능해지는 것이다. 
'''

class A(object):
    def a1(self):
        print("a1")
        

class B(object):
    def b(self):
        print("b")
        A().a1()


objectB = B()
objectB.b()