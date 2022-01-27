class Hotelier(object):
    def __init__(self):
        print("Arranging the Hotel for Marriage? -- ")
        
    
    def __isAvailable(self):
        print("Is the Hotel free for the event on given day?")
        return True
    
    def bookHotel(self):
        if self.__isAvailable():
            print("Registered the Booking \n\n")
    

class Florist(object):
    def __init__(self) -> None:
        print("Flower Decorations for the Event? -- ")
    
    def setFlowerRequirements(self):
        print("Carnations, Roses and Lilies would be used for Decorations \n\n")


class Caterer(object):
    def __init__(self) -> None:
        print("Food Arrangements for the Event? -- ")
    
    def setCuisine(self):
        print("Chinese & Continental Cuisine to be served \n\n")


class Musician(object):
    def __init__(self) -> None:
       print("Musical Arrangements for the Marriage? -- ")
    
    def setMusicType(self):
        print("Jazz and Classical to be played \n\n")