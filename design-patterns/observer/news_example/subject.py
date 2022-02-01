class NewsPublisher:
    def __init__(self) -> None:
        self.__subcribers = []
        self.__latesNews = None
    
    def attach(self, subscriber):
        self.__subcribers.append(subscriber)
    
    def detach(self):
        return self.__subcribers.pop()
    
    def subscribers(self):
        return [type(x).__name__ for x in self.__subcribers]
    
    def notifySubscribers(self):
        for sub in self.__subcribers:
            sub.update()
            
    def addNews(self, news):
        self.__latesNews = news

    def getNews(self):
        return "Got news:", self.__latesNews