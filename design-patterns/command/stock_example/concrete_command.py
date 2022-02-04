"""
BuyStockOrder와 SellStockOrder는 Order 인터페이스를 구현하는 구상클래스(Concrete class)이다.
각 클래스는 증권 거래 시스템 객체를 사용해 주식을 매수/매도 한다. 
각 클래스의 execute() 메소드는 주식객체를 통해 주식을 매수/매도한다.
"""


from order import Order

class BuyStockOrder(Order):
    def __init__(self, stock):
        self.stock = stock
    
    def execute(self):
        self.stock.buy()


class SellStockOrder(Order):
    def __init__(self, stock):
        self.stock = stock
    
    def execute(self):
        self.stock.sell()        