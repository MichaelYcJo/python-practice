'''
추상화
클라이언트가 클래스 객체를 생성하고 인터페이스에 의해 정의된 함수를 호출할 수 있는 인터페이스를 제공한다
'''


class Adder:
    def __init__(self):
        self.sum = 0
    def add(self, value):
        self.sum += value

acc = Adder()
for i in range(99):
    acc.add(i)
    
print(acc.sum)