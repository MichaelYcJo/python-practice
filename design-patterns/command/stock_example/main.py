"""
- 클라이언트는 StockTrade클래스를 Receiver로 지정한다. 
- BuyStockORder와 SellStockOrder 클래스(ConcreteCommand)는
StockTrade 객체에 대해 거래를 요청해 주문을 생성한다.
Invoker 객체는 Agent 클래스를 인스턴스화 할때 생성된다. 
Agent 클래스의 PlaceOrder() 메소드는 클라이언트의 요청을 주문한다.
"""

from receiver import StockTrade
from concrete_command import BuyStockOrder, SellStockOrder
from invoker import Agent

#Client 
stock = StockTrade()
buyStock = BuyStockOrder(stock)
sellStock = SellStockOrder(stock)

#Invoker
agent = Agent()
agent.placeOrder(buyStock)
agent.placeOrder(sellStock)