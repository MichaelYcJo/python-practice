from abc import ABC, abstractmethod

class AbstractMeal(ABC):
    def prepare_recipe(self):
        self.boil_water()
        self.add_main_ingredient()
        self.cook()
        self.serve()

    def boil_water(self):
        print("Boiling water")

    @abstractmethod
    def add_main_ingredient(self):
        pass

    @abstractmethod
    def cook(self):
        pass

    def serve(self):
        print("Serving the dish")

class Tea(AbstractMeal):
    def add_main_ingredient(self):
        print("Adding tea leaves to boiling water")

    def cook(self):
        print("Steeping the tea")

class Pasta(AbstractMeal):
    def add_main_ingredient(self):
        print("Adding pasta to boiling water")

    def cook(self):
        print("Cooking the pasta")

# 사용 예시
tea = Tea()
tea.prepare_recipe()

print()

pasta = Pasta()
pasta.prepare_recipe()