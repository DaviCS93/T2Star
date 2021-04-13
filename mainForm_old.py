import tkinter as tk
import os 
import numpy as np
import cv2
from PIL import Image, ImageTk


    @property
    def start(self):
        return (self.x1,self.y1)

    @property
    def end(self):
        return (self.x2,self.y2)

    def returnArea(self):
        return abs((self.x1-self.x2)*(self.y1-self.y2))

class MainForm():
    
    def __init__(self):
        PROJECT_PATH = os.path.dirname(__file__)
        IMG1 = os.path.join(PROJECT_PATH,'imgs','color506272653.png')
        IMG2 = os.path.join(PROJECT_PATH,'imgs','gray506272653.png')
        
        self.roi = ROI()
        self.listExam = []
        self.root = tk.Tk()        
        self.root.rowconfigure(0,weight=1)
        self.root.columnconfigure(0,weight=1)
        self.cnvExam = tk.Canvas(master=self.root,confine=True)
        self.cnvExam.grid()
        self.image = tk.PhotoImage(file = IMG2)
        self.t2star = tk.PhotoImage(file = IMG1)
        self.cnvExam.create_image(2,2,anchor=tk.NW,image=self.image)
        self.cnvExam.configure(height = self.image.height(), width = self.image.width()) 
        self.cnvExam.bind("<ButtonPress-1>", self.callback)
        self.cnvExam.bind("<B1-Motion>", self.onMove)
        self.cnvExam.bind("<ButtonRelease-1>", self.release)
        self.cnvExam.update()
        
        self.root.mainloop()

    def callback(self,event):
        self.roi.setStart(event.x,event.y)
        #print ("clicked at", event.x, event.y)
        self.rect = self.cnvExam.create_rectangle(event.x,event.y,event.x,event.y, outline='black',width=3)
    
    def release(self,event):
        self.roi.setEnd(event.x,event.y)
        #print ("released at", event.x, event.y)
        #print ("area = {0}".format(self.roi.returnArea()))
        self.cnvExam.delete(self.rect)
        self.mask = np.zeros((self.image.height(),self.image.width()), np.uint8)
        self.mask = cv2.rectangle(self.mask,self.roi.start,self.roi.end,(255, 255, 255), -1) 
        self.mask_inv = cv2.bitwise_not(self.mask)
        self.replace()
        #cv2.imshow("test",self.mask)

    def onMove(self,event):
        self.roi.x2,self.roi.y2 = (event.x, event.y)
        # expand rectangle as you drag the mouse
        self.cnvExam.coords(self.rect,
                            self.roi.x1,
                            self.roi.y1,
                            self.roi.x2,
                            self.roi.y2)

    def replace(self):
        PROJECT_PATH = os.path.dirname(__file__)
        IMG1 = os.path.join(PROJECT_PATH,'imgs','gray506272653.png')
        IMG2 = os.path.join(PROJECT_PATH,'imgs','color506272653.png')
        img1 = cv2.imread(IMG1)
        img2 = cv2.imread(IMG2)
        img1_bg = cv2.bitwise_or(img1, img1, mask = self.mask_inv)
        img2_fg = cv2.bitwise_or(img2, img2, mask = self.mask)
        dst = cv2.add(img1_bg,img2_fg)
        self.cnvExam.delete("all")
        self.img = ImageTk.PhotoImage(image=Image.fromarray(dst),size=(self.image.height(),self.image.width()))
        self.cnvExam.create_image(2,2,anchor=tk.NW,image=self.img)
        self.cnvExam.update()
        
        #cv2.imshow("test",dst)

if __name__ == "__main__":
    main = MainForm() 
   