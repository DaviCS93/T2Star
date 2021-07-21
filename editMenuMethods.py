import tkinter as tk
from math import fabs
from decorators import timer
from canvasElements import ROI, DrawnLines, canvasElement,Tag
from shape import Shape

def startRoi(env,event,shape):
    newRoi = ROI(shape)
    newRoi.setStart(event.x,event.y)
    env.addCanvasElement(newRoi)
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
    env.imgObj.replaceRoi(env.canvasElemList)
    # Deleta imagem atual do exame
    event.widget.delete("all")
    event.widget.unbind("<ButtonPress-1>")
    event.widget.unbind("<B1-Motion>")
    event.widget.unbind("<ButtonRelease-1>")
    env.historyListbox.selection_set(env.canvasElemList[-1].elmId)
    env.updateImage()
    
def startDraw(event,env,thickness,color):
    x1, y1 = map(lambda x: x + 4.5*thickness,(event.x,event.y))
    x2, y2 = map(lambda x: x - 4.5*thickness,(event.x,event.y))
    event.widget.create_oval(x1,y1,x2,y2, outline=color,fill=color,width=1)
    d = DrawnLines(event.x,event.y,thickness,color,env.imgObj.activeZoom)
    env.addCanvasElement(d)

def onMoveDraw(event,env,thickness,color):
    coords = [x for x in env.canvasElemList[-1].dots[-2:]]
    xPrev,yPrev=coords[-1][0],coords[-1][1]
    xDiff,yDiff = event.x-xPrev,event.y - yPrev
    #TODO bug em caso de curva acelerada
    if abs(xDiff)>30 or abs(yDiff)>30:
        coords.append((xPrev+(xDiff/2),yPrev+(yDiff/2)))
        env.canvasElemList[-1].addCoord(xPrev+(xDiff/2),yPrev+(yDiff/2))
    flatCoods = list(sum(coords, ()))
    event.widget.create_line(event.x,event.y,flatCoods,fill=color,width=10*thickness,smooth=True)
    #doDraw((event.x,event.y),event.widget,thickness,env)
    env.canvasElemList[-1].addCoord(event.x,event.y)

def releaseDraw(event,env):
    env.updateImage()
    pass
    # event.widget.unbind("<ButtonPress-1>")
    # event.widget.unbind("<B1-Motion>")
    # event.widget.unbind("<ButtonRelease-1>")

def zoom(event,env,zoomIn):
    env.applyZoom(zoomIn)
    env.updateImage()

def startTag(event,env):
    xRel, yRel = event.widget.winfo_rootx()+event.x,event.widget.winfo_rooty()+event.y
    wrapper = tk.Toplevel(event.widget)
    wrapper.geometry("%dx%d+%d+%d" % (100, 100, xRel, yRel))
    wrapper.transient(event.widget)
    wrapper.columnconfigure(0,weight=1,uniform="tagset")
    wrapper.columnconfigure(1,weight=1,uniform="tagset")
    wrapper.rowconfigure(0,weight=1)
    textBox = tk.Text(wrapper)
    textBox.grid(row=0,column=0,columnspan=2,sticky='NWE')
    okBtn = tk.Button(wrapper,text="Ok",command=lambda: releaseTag(wrapper,textBox.get('1.0',tk.END),event.x, event.y,event.widget,env))
    cancelBtn = tk.Button(wrapper,text="Cancel",command=lambda: wrapper.destroy())
    okBtn.grid(row=1,column=0,sticky='SW')
    cancelBtn.grid(row=1,column=1,sticky='SE')
    wrapper.grab_set()
    
def releaseTag(popup,text,x,y,canvas,env):
    canvas.create_text(x,y,font="Arial 12 bold",text=text)
    t = Tag(x,y,text)
    env.addCanvasElement(t)
    popup.destroy()
