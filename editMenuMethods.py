from math import fabs

from decorators import timer
from canvasElements import ROI, DrawnLines
from shape import Shape


def callbackRoi(env,event,shape):
    newRoi = ROI(shape)
    newRoi.setStart(event.x,event.y)
    env.canvasElemList.append(newRoi)
    #print ("clicked at", event.x, event.y)
    if shape == Shape.RECTANGLE:
        env.activeROI = event.widget.create_rectangle(event.x,event.y,event.x,event.y, outline='black',width=3)
    elif shape == Shape.CIRCLE:
        env.activeROI = event.widget.create_oval(event.x,event.y,event.x,event.y, outline='black',width=3)
 
def onMoveRoi(env,event):
    movingRoi = env.canvasElemList[-1]
    movingRoi.x2,movingRoi.y2 = (event.x, event.y)
    # expand rectangle as you drag the mouse
    if movingRoi.shape == Shape.CIRCLE:
        xDiff = movingRoi.x2-movingRoi.x1
        yDiff = movingRoi.y1-movingRoi.y2
        if fabs(xDiff)>fabs(yDiff):
            if  yDiff < 0:
                movingRoi.x2 = movingRoi.x1 + yDiff if xDiff < 0 else movingRoi.x1 - yDiff
            else:
                movingRoi.x2 = movingRoi.x1 - yDiff if xDiff < 0 else movingRoi.x1 + yDiff
        else:
            if  xDiff < 0:
                movingRoi.y2 = movingRoi.y1 - xDiff if yDiff < 0 else movingRoi.y1 + xDiff
            else:
                movingRoi.y2 = movingRoi.y1 + xDiff if yDiff < 0 else movingRoi.y1 - xDiff
    event.widget.coords(env.activeROI,
                        movingRoi.x1,
                        movingRoi.y1,
                        movingRoi.x2,
                        movingRoi.y2)

@timer
def releaseRoi(env,event):
    # Deleta imagem desenhada na ROI
    event.widget.delete(env.activeROI)
    # Desconsidera o zoom para aplicar a ROI
    roi =  env.canvasElemList[-1]
    roi.x1,roi.y1,roi.x2,roi.y2 = map(
        lambda c: int(c/env.imgObj.activeZoom),
        (roi.x1,roi.y1,roi.x2,roi.y2))
    env.imgObj.replaceROI(env.canvasElemList)
    # Deleta imagem atual do exame
    event.widget.delete("all")
    event.widget.unbind("<ButtonPress-1>")
    event.widget.unbind("<B1-Motion>")
    event.widget.unbind("<ButtonRelease-1>")
    env.updateImage()
    

def startDraw(event,env,thickness):
    x1, y1 = map(lambda x: x + 4.5*thickness,(event.x,event.y))
    x2, y2 = map(lambda x: x - 4.5*thickness,(event.x,event.y))
    event.widget.create_oval(x1,y1,x2,y2, outline='black',fill='black',width=1)
    d = DrawnLines(event.x,event.y,thickness)
    env.canvasElemList.append([d])

def onMoveDraw(event,env,thickness):
    coords = [x.coords for x in env.canvasElemList[-1][-5:]]
    event.widget.create_line(event.x,event.y,list(sum(coords, ())),width=10*thickness,smooth=True)
    #doDraw((event.x,event.y),event.widget,thickness,env)
    d = DrawnLines(event.x,event.y,thickness)
    env.canvasElemList[-1].append(d)

def releaseDraw(event,env):
    pass

def zoom(event,env,zoomIn):
    env.applyZoom(zoomIn)
    env.updateImage()