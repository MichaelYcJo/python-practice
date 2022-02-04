"""
StockTrade 클래스는 Receiver 객체를 나타낸다. 
ConcreteCommand 객체가 생성한 주문을 처리하는 메서드를 정의한다. 
Receiver에 정의된 buy()와 sell() 메소드는 BuyStockOrder와 SellStockOrder 클래스를 통해 주식을 매수/매도 할때 호출한다. 
"""

class StockTrade:
    def buy(self):
        print('주식 매수')
    
    def sell(self):
        print('주식 매도')