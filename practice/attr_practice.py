
class DirClass:
    # 클래스 attribute
    class_attr = 'I am Class Attribute'

    def __init__(self, name : str):
        # 인스턴스 attribute
        self.id : int = 1
        self.name : str= name



dir_instance = DirClass('test')
print(dir(dir_instance))
print(hasattr(dir_instance, 'address'))
print(getattr(dir_instance, 'address', 'Not Found'))
print(dir_instance.__dict__)
print()

dir_instance.__setattr__('address', "대한민국")

print()
print(dir(dir_instance))
print(hasattr(dir_instance, 'address'))
print(getattr(dir_instance, 'address', 'Not Found'))
print(dir_instance.__dict__)



