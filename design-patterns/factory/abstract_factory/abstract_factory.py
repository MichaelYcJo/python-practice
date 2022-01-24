'''
클래스를 직접 호출하지 않고 관련된 객체를 생성하는 인터페이스를 제공하는 것이다. 
팩토리 메서드가 인스턴스 생성을 서브 클래스에게 맡기는 반면
추상 팩토리 메서드는 관련된 객체의 집합을 생성한다.
'''

from abc import ABC, ABCMeta, abstractclassmethod

class Pizzafactory(metaclass=ABCMeta):
    
    @abstractclassmethod
    def createVegPizza(self):
        pass
    
    @abstractclassmethod
    def createNonVegPizza(self):
        pass


class IndianPizzaFactory(Pizzafactory):
    
    def createVegPizza(self):
        return DeluxVeggiePizza()
    
    def createNonVegPizza(self):
        return ChickenPizza()


class USPizzaFactory(Pizzafactory):
    
    def createVegPizza(self):
        return MexicanVegPizza()
    
    def createNonVegPizza(self):
        return HamPizza()
    

class VegaPizza(metaclass=ABCMeta):
    @abstractclassmethod
    def prepare(self):
        pass

class NonVegPizza(metaclass=ABCMeta):
    @abstractclassmethod
    def serve(self):
        pass

class DeluxVeggiePizza(VegaPizza):
    def prepare(self):
        print("Prepare ", type(self).__name__)

class ChickenPizza(NonVegPizza):
    def serve(self):
        print("Serve ", type(self).__name__)
    

class MexicanVegPizza(VegaPizza):
    def prepare(self):
        print("Prepare ", type(self).__name__)

class HamPizza(NonVegPizza):
    def serve(self, VegPizza):
        print(type(self).__name__, "is served with Ham on", 
        type(VegPizza).__name__)
        

class PizzaStore:
    def __init__(self):
        pass
    
    def makePizzas(self):
        for factory in [IndianPizzaFactory(), USPizzaFactory()]:
            self.factory = factory
            self.NonVegPizza = self.factory.createNonVegPizza()
            self.VegPizza = self.factory.createVegPizza()
            self.VegPizza.prepare()
            self.NonVegPizza.serve(self.VegPizza)
            
pizza = PizzaStore()
pizza.makePizzas()
