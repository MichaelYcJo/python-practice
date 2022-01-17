'''
모듈을 import하는 시점에 실수로 객체를 미리 생성하는 경우가 있다.
게으른초기화는 인스턴스를 꼭 필요할 때 생성하는 특징이 있다.
아래의 코드는 s = Singeton()부분은 __init__함수를 실행하지만 객체는 생성하지 않는다.
대신 Singleton.getInstance()부분에서 객체가 생성된다.
'''

class Singleton:
    __instance = None
    def __init__(self):
        if not Singleton.__instance:
            print("__init__ method called")
        else:
            print("Instance already created:", self.getInstance())
    
    @classmethod
    def getInstance(cls):
        if not cls.__instance:
            cls.__instance = Singleton()
        return cls.__instance

s = Singleton() # 클래스를 초기화 했지만 객체생성은 되지 않음
print("Object created", Singleton.getInstance()) #객체 생성
s1 = Singleton() # 객체가 이미 생성된 상태


'''
언더스코어를 두개(__)붙인 변수는 선언된 클래스 안에서만 해당 이름으로 사용 가능하다. 
위 예제에서는 lazy_instantation_singleton.py안에서만 __instance 변수가 __instance 사용이 가능하고, 
외부 모듈에서는 __instance이름으로 사용이 불가능하다.

외부에서 lazy_instantation_singleton.py의 __instance 변수에 접근하려면 _클래스명__변수명 형식으로 변경해서 사용할 수 있다. 
이러한 작업을 '맹글링(Mangling)'이라고 한다.

'''