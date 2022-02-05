from abc import ABCMeta, abstractclassmethod

class Compiler(metaclass=ABCMeta):
    @abstractclassmethod
    def collectSource(self):
        pass
    
    
    @abstractclassmethod
    def compileToObject(self):
        pass
    
    @abstractclassmethod
    def run(self):
        pass
    
    def compileAndRun(self):
        self.collectSource()
        self.compileToObject()
        self.run()


class iOSCompiler(Compiler):
    def collectSource(self):
        print("Collecting Swift Source Code")
    
    def compileToObject(self):
        print("Compiling Swift code to LLVM bitcode")
    
    def run(self):
        print("Running")
        
iOS = iOSCompiler()
iOS.compileAndRun()