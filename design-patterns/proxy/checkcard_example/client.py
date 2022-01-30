from proxy import DebitCard

class You:
 
    def __init__(self):
        print("You: Lets buy some shoes")
        self.debitCard = DebitCard()
        self.isPurchased = None
    
    def make_payment(self):
        self.isPurchased = self.debitCard.do_pay()
        
    def __del__(self):
        if self.isPurchased:
            print("You: It is Mine ")
        else:
            print("You::I should earn more: (")
        
