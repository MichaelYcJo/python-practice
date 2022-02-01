'''
Subscribe는 Observer로 모든 COncreteObserver의 추상 기본 클래스이다. 

'''

from abc import ABCMeta, abstractmethod

class Subscriber(metaClass=ABCMeta):
    @abstractmethod
    def update(self, news):
        pass