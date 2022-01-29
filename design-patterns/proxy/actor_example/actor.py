# Proxy 클래스

class Actor(object):
    def __init__(self):
        self.isBusy = False
        
    def occupied(self):
        self.isBusy = True
        print(type(self).__name__, "is occupied with current movie") # 다른영화 촬영중

    def available(self):
        print(type(self).__name__, "is free for the movie") # 영화 출연 가능
    
    def getStatus(self):
        return self.isBusy


class Agent(object):
    def __init__(self):
        self.principal = None
    
    def work(self):
        self.actor = Actor()
        if self.actor.getStatus():
            self.actor.occupied()
        else:
            self.actor.available()


if __name__ == '__main__':
    r = Agent()
    r.work()