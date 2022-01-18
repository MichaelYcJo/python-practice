'''
- 모노스테이트 싱글톤은 이름 그대로 객체가 같은 상태를 공유하는 패턴이다.
- 파이썬은 __dict__ 속성에 클래스 내 모든 객체의 상태를 저장한다. 
  아래의 경우 모든 인스턴스의 __dict__ 를 __shared_state로 설정한다. 
  하나의 객체만 생성하는 싱글톤 패턴과 달리 b와 b1 인스턴스를 초기화하면 두개의 객체가 생성된다. 
  하지만 b.__dict__와 b1.__dict__는 같다. 
  따라서 b.x=4는 b1.x1 역시 4로 바뀌는것을 볼 수 있다.

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