from subject import Payment
from real_subject import Bank


class DebitCard(Payment):
    
    def __init__(self):
        self.bank = Bank()
    
    def do_pay(self):
        card = input("Enter your card number: ")
        self.bank.setCard(card)
        return self.bank.do_pay()