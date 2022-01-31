'''
Subject는 Observer를 관리한다. 
Observer는 Subject 클래스의 regiser() 메소드를 호출해 자신을 등록한다. 
'''

class Subject:
    def __init__(self) -> None:
        self.__observers = []
        
    def register(self, observer):
        self.__observers.append(observer)
    
    def notifyAll(self, *args, **kwargs):
        for observer in self.__observers:
            observer.notify(self, *args, **kwargs)

'''
옵저버는 Subject를 감시하는 객체를 위한 인터페이스를 제공한다. 
'''
class Observer1:
    def __init__(self, subject) -> None:
        subject.register(self)
    
    def notify(self, subject, *args):
        print(type(self).__name__, ": Got", args, f"from {subject}")

class Observer2:
    def __init__(self, subject) -> None:
        subject.register(self)
    
    def notify(self, subject, *args):
        print(type(self).__name__, ": Got", args, f"from {subject}")


subject = Subject()
observer1 = Observer1(subject)
observer2 = Observer2(subject)
subject.notifyAll('notification')