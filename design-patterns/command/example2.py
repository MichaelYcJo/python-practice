"""
    클라이언트는 특정 연산을 요청한다.
    Invoke는 클라이언트의 요청을 받아 캡슐화해 큐에 넣는다.
    ConcreteCommand 클래스는 이 요청을 책임지고 Receiver에 수행을 맡긴다. 
"""

from abc import ABCMeta, abstractclassmethod

class Command(metaclass=ABCMeta):
    
    def __init__(self, recv):
        self.recv = recv
        
    def execute(self):
        pass
    
class ConcreteCommand(Command):
    
    def __init__(self, recv):
        self.recv = recv
    
    def execute(self):
        return self.recv.action()

class Receiver:
    def action(self):
        print("Receiver Action")
    

class Invoker:
    def command(self, cmd):
        self.cmd = cmd
    
    def execute(self):
        self.cmd.execute()

if __name__ == '__main__':
    recv = Receiver()
    cmd = ConcreteCommand(recv)
    invoker = Invoker()
    invoker.command(cmd)
    invoker.execute()
