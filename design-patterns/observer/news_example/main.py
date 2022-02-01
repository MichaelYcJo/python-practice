from concrete_observer import EmailSubscriber, SMSSubscriber
from subject import NewsPublisher
from concrete_observer import SMSSubscriber, EmailSubscriber, AnyOtherSubscriber

if __name__ == '__main__':
    news_publisher = NewsPublisher()
    for Subscribers in [SMSSubscriber, EmailSubscriber, AnyOtherSubscriber]:
        Subscribers(news_publisher)
        print("\n Subscribers:", news_publisher.subscribers())
    
    news_publisher.addNews("Hello World!")
    news_publisher.notifySubscribers()
    
    
    print("\n Detach:", news_publisher.detach())
    print("\n Subscribers:", news_publisher.subscribers())
    
    news_publisher.addNews("Second News!")
    news_publisher.notifySubscribers()