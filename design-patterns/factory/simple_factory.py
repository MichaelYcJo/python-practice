from abc import ABCMeta, abstractclassmethod

'''
심플 팩토리 패턴
- 인터페이스를 통해 객체를 생성하지만 서브 클래스가 객체생성에 필요한 클래스를 선택한다.
- 팩토리 메소드와 추상팩토리 메소드 패턴을 이해하기위한 기본개념정도
- 여러 종류의 객체를 사용자가 직접 클래스를 호출하지 않고도 생성할 수 있다.
'''

# ABCMeta는 파이썬에서 특정 클래스를 abstrac으로 선언하는 특수 메타클래스이다.
class Animal(metaclass = ABCMeta):
    @abstractclassmethod
    def do_say(self):
        pass

class Dog(Animal):
    def do_say(self):
        print("Dog says: Bow-Wow")


class Cat(Animal):
    def do_say(self):
        print("Cat says: Meow")


## forest factory 정의
class ForestFactory(object):
    def make_sound(self, object_type):
        return eval(object_type)().do_say()


## Client Code

if __name__ == '__main__':
    ff = ForestFactory()
    animal = input("Which animal should make_sound? Dog, Cat ")
    ff.make_sound(animal)
    