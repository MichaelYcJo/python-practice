class Singletone(object):
    def __new__(cls):
        # hasattr -> 해당 객체가 명시한 속성을 가지고 있는지 확인하는 함수
        # cls객체가 instance
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singletone, cls).__new__(cls)
        return cls.instance
    
    
s = Singletone()
print("Ojbect created", s)

s1 = Singletone()
print("Ojbect created", s1)