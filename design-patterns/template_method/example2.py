from abc import ABCMeta, abstractclassmethod

class AbstractClass(metaclass=ABCMeta):
    def __init__(self):
        pass
    
    @abstractclassmethod
    def operation1(self):
        pass
    
    @abstractclassmethod
    def operation2(self):
        pass
    
    def template_method(self):
        print("Definning the Algorith. Operationl follows Operaiont2")
        self.operation2()
        self.operation1()


class ConcreteClass(AbstractClass):
    
    def operation1(self):
        print("My Concrete Operation1")
    
    def operation2(self):
        print("My Concrete Operation2")
    
class Client:
    def main(self):
        self.concrete = ConcreteClass()
        self.concrete.template_method()
    
client = Client()
client.main()