from abstract_factory import IndianPizzaFactory, USPizzaFactory


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