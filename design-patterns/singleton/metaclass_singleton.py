'''
메타클래스는 클래스의 클래스이다. 
즉 클래스는 자신의 메타클래스의 인스턴스이다. 
메타클래스를 사용하면 이미 정의된 파이썬 클래스를 통해 새로운 형식의 클래스를 생성(재정의)할 수 있다.

__call__은 인스턴스가 호출되었을때 실행된다. 
인스턴스 i의 값이 args에 담겨져 프린트되는것을 볼 수 있다.
'''


class MyInt(type):
    def __call__(cls, *args, **kwargs):
        print("**** Here's My int ****", args)
        print("Now do whatever you want with these objects...")
        return type.__call__(cls, *args, **kwargs)
    

class int(metaclass=MyInt):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
i = int(4, 5)


# 메타클래스를 활용하여 싱글톤 패턴을 구현하면 아래와 같다.

'''
_변수명
주로 한 모듈 내부에서만 사용하는 private 클래스/함수/변수/메서드를 선언할 때 사용하는 컨벤션이다.
이 컨벤션으로 선언하게 되면 from module import *시 _로 시작하는 것들은 모두 임포트에서 무시된다. 
그러나, 파이썬은 진정한 의미의 private을 지원하고 있지는 않기 때문에 private을 완전히 강제할 수는 없다. 
'''

class Metasingleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Metasingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger(metaclass=Metasingleton):
    pass


logger1 = Logger()
logger2 = Logger()
print("Logger: ", logger1, logger2)