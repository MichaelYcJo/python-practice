from subject import Payment

class Bank(Payment):
    
    def __init__(self) -> None:
        self.card = None
        self.account = None
    
    def __getAccount(self):
        self.account = self.card # 카드번호와 계좌번호는 같다고 가정
        return self.account
    
    def __hasFunds(self):
        print("Bank:: Checking if Account", self.__getAccount(), "has enough funds")
        return True
    
    def setCard(self, card):
        self.card = card
    
    def do_pay(self):
        if self.__hasFunds():
            print("Bank:: Paying the merchant")
            return True
        else:
            print("Bank:: Sorry, not enough funds!")
            return False
        