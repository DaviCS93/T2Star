from abc import ABCMeta,abstractmethod
class canvasElement(ABCMeta):
    def __str__(self):
        return self.__name__

    
    @abstractmethod
    def getInfo(self):
        pass


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

    def getInfo(self):
        return f'{self.shape.name}({self.x1},{self.y1}),({self.x2},{self.y2})'

class DrawnLines(canvasElement):
    def __init__(self,x,y,thickness,color,zoom):
        self.dots = [(x,y)]
        self.xLast = x
        self.yLast = y
        self.thickness = thickness
        self.color = color
        self.currentZoom = zoom
    
    @property
    def coords(self):
        return self.xLast,self.yLast
    
    def addCoord(self,x,y):
       self.dots.append((x,y))
         
    def getInfo(self):
        return f'{self.color.upper()}({self.dots[0]},{self.dots[1]})'

class Tag(canvasElement):
    def __init__(self,x,y,text):
        self.x = x
        self.y = y
        self.text = text

    def getInfo(self):
        return f'{self.text}({self.x},{self.y})'
    
    
