import tkinter as tk
import os 
import numpy as np
import cv2
from PIL import Image, ImageTk   

def callbackRectangle(env,event):
    env.roi.setStart(event.x,event.y)
    #print ("clicked at", event.x, event.y)
    env.rect = env.resultCanvas.create_rectangle(event.x,event.y,event.x,event.y, outline='black',width=3)

def release(env,event):
    env.roi.setEnd(event.x,event.y)
    #print ("released at", event.x, event.y)
    #print ("area = {0}".format(env.roi.returnArea()))
    env.resultCanvas.delete(env.rect)
    env.mask = np.zeros(env.imgObj.size, np.uint8)
    env.mask = cv2.rectangle(env.mask,env.roi.start,env.roi.end,(255, 255, 255), -1) 
    env.mask_inv = cv2.bitwise_not(env.mask)
    replace(env)
    #cv2.imshow("test",env.mask)

def onMove(env,event):
    env.roi.x2,env.roi.y2 = (event.x, event.y)
    # expand rectangle as you drag the mouse
    env.resultCanvas.coords(env.rect,
                        env.roi.x1,
                        env.roi.y1,
                        env.roi.x2,
                        env.roi.y2)

def replace(env):
    cvEcho = cv2.imread(env.imgObj.grayName)
    cvStar = cv2.imread(env.imgObj.colorName)
    PROJECT_PATH = os.path.dirname(__file__)
    imgEcho_bg = cv2.bitwise_or(cvEcho, cvEcho, mask = env.mask_inv)
    imgStar_fg = cv2.bitwise_or(cvStar, cvStar, mask = env.mask)
    dst = cv2.add(imgEcho_bg,imgStar_fg)
    env.resultCanvas.delete("all")
    env.resultImg = ImageTk.PhotoImage(image=Image.fromarray(dst),size=env.imgObj.size)
    env.resultCanvas.create_image(2,2,anchor=tk.NW,image=env.resultImg)
    env.resultCanvas.update()