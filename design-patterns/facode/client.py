from facode import EventManager


class You(object):
    def __init__(self) -> None:
        print("You :: Whoa! Marriage Arrangements?? -- ")
    
    def askEventManager(self):
        print("You :: Let's see, Shall I book the Hotel for you? -- ")
        em = EventManager()
        em.arrange()
    
    def __del__(self):
        print("You :: Thank you for your time. See you soon! -- ")


you = You()
you.askEventManager()