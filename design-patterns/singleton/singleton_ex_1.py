import sqlite3


# 여러 서비스가 한개의 DB를 공유하는 구조이다.

class MetaSingleton(type):
    _instances = {}
    
    #__call__은 인스턴스가 호출되었을때 실행된다. 
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class Database(metaclass=MetaSingleton):
    connection = None
    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect("db sqlite3")
            self.cursorobj = self.connection.cursor()
        return self.cursorobj
    
db1 = Database().connect()
db2 = Database().connect()

print("Database Object DB1 ", db1)
print("Database Object DB2 ", db2)