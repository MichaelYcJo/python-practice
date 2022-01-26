from abc import ABCMeta, abstractclassmethod

class VegaPizza(metaclass=ABCMeta):
    @abstractclassmethod
    def prepare(self, VegPizza):
        pass

class NonVegPizza(metaclass=ABCMeta):
    @abstractclassmethod
    def serve(self, VegPizza):
        pass

class DeluxVeggiePizza(VegaPizza):
    def prepare(self):
        print("Prepare ", type(self).__name__)

class ChickenPizza(NonVegPizza):
    def serve(self, VegPizza):
        print("Serve ", type(self).__name__)
    
class MexicanVegPizza(VegaPizza):
    def prepare(self):
        print("Prepare ", type(self).__name__)

class HamPizza(NonVegPizza):
    def serve(self, VegPizza):
        print(type(self).__name__, "is served with Ham on", 
        type(VegPizza).__name__)