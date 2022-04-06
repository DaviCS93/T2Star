from abc import ABC,abstractmethod
from random import Random
class canvasElement(ABC):
    elmIds = []

    def __init__(self):
        self.elmId = ''
        self.canvasId = ''
        while self.elmId == '' or self.elmId in self.elmIds:
            self.elmId = str(Random().random()).split('.')[-1]
        self.elmIds.append(self.elmId)    

    def __str__(self):
        return self.__class__.__name__

    @abstractmethod
    def getInfo(self):
        pass

class ROI(canvasElement):
    def __init__(self,shape):
        super().__init__()
        self.shape = shape
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.definedInfo = False
        self.mean = 0.0
        self.std = 0.0
        self.min = 0.0
        self.max = 0.0
        self.area = 0.0
        self.pix = 0.0
        self.decayImgFile = ""
        self.decayImg = None
        self.imgFile = ""
        self.mse = 0.0
        self.decay = None
        self.time = None
        self.points = []

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
        return f'{self.shape.name}({round(self.x1,0)},{round(self.y1,0)}),({round(self.x2,0)},{round(self.y2,0)})'

class DrawnLines(canvasElement):
    def __init__(self,x,y,thickness,color,zoom):
        super().__init__()
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
        return f'{self.color.upper()}({self.dots[0][0]},{self.dots[0][1]})'

class Tag(canvasElement):
    def __init__(self,x,y,text,index):
        super().__init__()
        self.canvasIndex = index
        self.tagId = ''
        self.x = x
        self.y = y
        self.text = text

    def getInfo(self):
        editedText = ' '.join(self.text.replace('\n',' ').split())
        return f'{self.canvasIndex}-{editedText}({self.x},{self.y})'
     
    
