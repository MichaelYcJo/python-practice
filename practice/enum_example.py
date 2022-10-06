from enum import Enum


class Rainbow(Enum):
    Red = 0
    Orange = 1
    Yellow = 2
    Green = 3
    Blue = 4
    Navy = 5
    Purple = 6

rainbow = Rainbow

print(rainbow['Blue'])  # 4
print(rainbow.Blue.name ) #Blue
print(rainbow.Blue.value) # 4
print()


import enum

# auto 를 사용하면 1부터 시작한다
class Rainbow(enum.Enum):
    Red = enum.auto()
    Orange = enum.auto()
    Yellow = enum.auto()
    Green = enum.auto()
    Blue = enum.auto()
    Navy = enum.auto()
    Purple = enum.auto()

rainbow = Rainbow

print(rainbow['Blue'])  # 4
print(rainbow.Blue.name ) #Blue
print(rainbow.Blue.value) # 5
print()
