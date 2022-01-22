from abc import ABCMeta, abstractclassmethod


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
    