from abc import ABC
class canvasElement(ABC):
    def __str__(self):
        return self.__name__


class ROI(canvasElement):
    def __init__(self,shape):
        self.shape = shape
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

    def setStart(self,x,y):
        self.x1 = x
        self.y1 = y

    def setEnd(self,x,y):
        self.x2 = x
        self.y2 = y

    @property
    def start(self):
        return self.x1,self.y1

    @property
    def end(self):
        return self.x2,self.y2

class DrawnLines(canvasElement):
    def __init__(self,x,y,thickness):
        self.x = x
        self.y = y
        self.thickness = thickness
    
    @property
    def coords(self):
        return self.x,self.y