"""
- Agent 클래스는 Invoker를 나타낸다.
- Agent는 클라이언트와 StockExchange 객체 사이의 중개자이며 클라이언트의 주문을 처리한다. 
- Agent 에는 큐를 나타내는 __orderQueue 리스트형 데이터 멤버가있다. 
모든 신규주문건은 이 큐에 추가된다. 
placeOrder() 메서드는 주문을 큐에넣고 처리까지 담당한다.
"""

class Agent:
    def __init__(self):
        self.__orderQueue = []
    
    def placeOrder(self, order):
        self.__orderQueue.append(order)
        order.execute()