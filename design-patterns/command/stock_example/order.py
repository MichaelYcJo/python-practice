"""
Command 객체를 나타낸다.
추상 기본 클래스인 인터페이스이며 Concrete Command는 이를 기반으로 세부로직을 구현한다. 
execute() 메소드는 ConcreteCommand 클래스가 Order 클래스를 실행하는 추상메소드이다.
"""

from abc import ABCMeta, abstractclassmethod

class Order(metaclass=ABCMeta):
    @abstractclassmethod
    def execute(self):
        pass

