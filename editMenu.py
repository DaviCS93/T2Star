import tkinter as tk
import os 
import numpy as np
import cv2
from math import fabs
from PIL import Image, ImageTk   
from roi import ROI
from shape import Shape

def callbackRoi(env,event,shape):
    newRoi = ROI(shape)
    newRoi.setStart(event.x,event.y)
    env.roiList.append(newRoi)
    #print ("clicked at", event.x, event.y)
    if shape == Shape.RECTANGLE:
        env.activeROI = event.widget.create_rectangle(event.x,event.y,event.x,event.y, outline='black',width=3)
    elif shape == Shape.CIRCLE:
        env.activeROI = event.widget.create_oval(event.x,event.y,event.x,event.y, outline='black',width=3)
 
def onMoveRoi(env,event):
    movingRoi = env.roiList[-1]
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

def releaseRoi(env,event):
    # Deleta imagem desenhada na ROI
    event.widget.delete(env.activeROI)
    # Desconsidera o zoom para aplicar a ROI
    fixROI(env)
    env.imgObj.replace(env.roiList)
    # Deleta imagem atual do exame
    event.widget.delete("all")
    event.widget.unbind("<ButtonPress-1>")
    event.widget.unbind("<B1-Motion>")
    event.widget.unbind("<ButtonRelease-1>")
    env.updateImage()

def callbackDraw(event):
    event.widget.old_coords = event.x, event.y
    
def onMoveDraw(event):
    x, y = event.x, event.y
    x1, y1 = event.widget.old_coords
    event.widget.create_line(x, y, x1, y1)
    event.widget.old_coords = x, y

def releaseDraw(event):
    x, y = event.x, event.y
    x1, y1 = event.widget.old_coords
    event.widget.create_line(x, y, x1, y1)
    event.widget.old_coords = None      

def fixROI(env):
    roi =  env.roiList[-1]
    roi.x1,roi.y1,roi.x2,roi.y2 = map(
        lambda c: int(c/env.imgObj.activeZoom),
        (roi.x1,roi.y1,roi.x2,roi.y2))
    pass

def zoomIn(event,env):
    env.applyZoom(True)

def zoomOut(event,env):
    env.applyZoom(False)