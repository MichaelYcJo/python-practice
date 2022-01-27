from sub_system import Hotelier, Florist, Caterer, Musician

class EventManager(object):
    
    def __init__(self):
        print("EventManager :: Let me talk the folks \n")
        
    
    def arrange(self):
        self.hotelier = Hotelier()
        self.hotelier.bookHotel()
        
        self.florist = Florist()
        self.florist.setFlowerRequirements()
        
        self.caterer = Caterer()
        self.caterer.setCuisine()
        
        self.musician = Musician()
        self.musician.setMusicType()