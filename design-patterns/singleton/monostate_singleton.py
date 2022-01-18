'''
- 모노스테이트 싱글톤은 이름 그대로 객체가 같은 상태를 공유하는 패턴이다.

'''

# Method 1
class Borg:
   __shared_state = {"1": "2"}
   def __init__(self):
     self.x = 1
     self.__dict__ = self.__shared_state
     pass
   

b = Borg()
b1 = Borg()
b.x = 4

print("Borg Object 'b' : ", b) ## b와 b1은 다른 객체다
print("Borg Object 'b1' : ", b1) 
print("Object State 'b' : ", b.__dict__) # b와 b1은 상태를 공유한다
print("Object State 'b1' : ", b1.__dict__)

print('===============================================================')

# Method 2
class Borg(object):
  _shared_state = {}
  # __new__ 객체 인스턴스 생성
  def __new__(cls, *args, **kwargs):
    obj = super(Borg, cls).__new__(cls, *args, **kwargs)
    obj.__dict__ = cls._shared_state
    return obj


b = Borg()
b1 = Borg()
b.x = 4

print("Borg Object 'b' : ", b) ## b와 b1은 다른 객체다
print("Borg Object 'b1' : ", b1) 
print("Object State 'b' : ", b.__dict__) # b와 b1은 상태를 공유한다
print("Object State 'b1' : ", b1.__dict__)