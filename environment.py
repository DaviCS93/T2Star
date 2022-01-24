import re
import os
from tkinter.constants import X,END

from numpy import newaxis
from canvasElements import DrawnLines,ROI,Tag
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk,ImageGrab
from enumInterface import Texts as txt
from imgObject import imgObject as imgObj
from threading import Thread
from decorators import timer
from PIL import ImageTk,Image

class Environment:

    def __init__(self,examID,dicomList):
        self.examCanvasId = ''
        # ID do exame
        self.examID = examID
        # Obj de imagem relacionado a esse ambiente (aba)
        self.imgObj = imgObj(dicomList,examID)
        self.showColor = True
        self.canvasElemList = []
        # Canvas da imagem (para poder desenhar as roi's)
        self.resultCanvas = None
        
        self.dicomExamsCanvas = None
        # Frame de apresentação da imagem do exame
        self.examFrame = None
        # Imagem printada no final
        # Roi ativa para desenhar a forma + deletar a forma no fim
        self.activeROI = None
        # Taxa de zoom
        self.zoomFactor = 1.2
        self.historyListItems = tk.StringVar()
        self.canvasPic = f'imgs/canvas{examID}.png'

    @timer
    def updateImage(self):
        # Limpa o canvas (deleta a imagem antiga)
        self.resultCanvas.delete("all")
        # Aplica o zoom sobre uma copia da imagem logo antes de apresentar,
        # para evitar distorções na imagem original
        resultImage = self.imgObj.resultColorImage if self.showColor else self.imgObj.resultRoiImage
        zoomedImage = resultImage.resize(
            (int(resultImage.width*self.imgObj.activeZoom),
            int(resultImage.height*self.imgObj.activeZoom)))
        # Print final e atualização do canvas
        self.printImage = ImageTk.PhotoImage(image=zoomedImage,size=zoomedImage.size)
        self.examCanvasId = self.resultCanvas.create_image(0,0,anchor=tk.NW,image=self.printImage,tags='printImage')
        self.resultCanvas.configure(width=zoomedImage.width,height=zoomedImage.height)
        self.reDraw()
        self.reTag()
        self.resultCanvas.update()
    
    def applyZoom(self,zoomIn):
        # zoomIn fica como o check para ver qual tipo de operação
        if zoomIn:
            self.imgObj.activeZoom *= self.zoomFactor
        else:
            self.imgObj.activeZoom /= self.zoomFactor
        self.updateCanvasScroll()

    def updateCanvasScroll(self):
        newX = self.imgObj.size[0]*self.imgObj.activeZoom
        newY = self.imgObj.size[1]*self.imgObj.activeZoom
        self.resultCanvas.config(scrollregion=(0,0,newX,newY))
        self.hbar.get()

    def createExamViewer(self,frm):
        self.examFrame = tk.Frame(frm,name=txt.EXAMIMAGE)
        self.examFrame.rowconfigure(0,weight=1)
        self.examFrame.columnconfigure(0,weight=4,uniform='examFrame')
        self.examFrame.columnconfigure(1,weight=2,uniform='examFrame')
        self.examFrame.grid(row=0,column=0,sticky=tk.NSEW)    
        
        self.sideExam = tk.Frame(self.examFrame)
        self.sideExam.grid(row=0,column=0,sticky=tk.NSEW)
        self.sideExam.rowconfigure('0 1',weight=1,uniform='sideExam')
        self.sideExam.columnconfigure(0,weight=2,uniform='sideExam')

        self.examBox = tk.LabelFrame(self.sideExam,text=" ".join((self.examID,'EXAM')))
        self.examBox.grid(row=0,column=0,sticky=tk.NSEW)
        self.examBox.rowconfigure(0,weight=1,uniform='examBox')
        self.examBox.columnconfigure(0,weight=9,uniform='examBox')
        self.examBox.columnconfigure('2 3',weight=1,uniform='examBox')
        
        self.dicomBox = tk.LabelFrame(self.sideExam,text=" ".join((self.examID,'DICOM')))
        self.dicomBox.grid(row=1,column=0,sticky=tk.NSEW)
        self.dicomBox.rowconfigure(0,weight=1,uniform='dicomBox')
        self.dicomBox.columnconfigure(0,weight=18,uniform='dicomBox')
        self.dicomBox.columnconfigure(1,weight=1,uniform='dicomBox')

        self.sideInfo = tk.Frame(self.examFrame)
        self.sideInfo.grid(row=0,column=1,sticky=tk.NSEW)
        self.sideInfo.rowconfigure('0 2',weight=1,uniform='sideframe')
        self.sideInfo.columnconfigure(0,weight=2,uniform='sideframe')

        self.scaleColorValue = tk.Scale(self.examBox, orient=tk.VERTICAL)
        self.scaleColorValue.grid(row=0,column=2,columnspan=2,sticky='NSE')
        self.scaleColorValue.configure(
            from_=self.imgObj.maxColor,
            to=self.imgObj.minColor,
            tickinterval=(self.imgObj.maxColor-self.imgObj.minColor)/12)

        self.scaleColorImage = tk.Canvas(master=self.examBox,width=30)
        self.scaleColorImage.grid(row=0,column=3,sticky='NSE')
        self.updateScaleCanvas(self.showColor)

        self.resultCanvas = tk.Canvas(master=self.examBox,scrollregion=(0,0,self.imgObj.size[0],self.imgObj.size[1]))
        self.resultCanvas.grid(row=0,column=0)

        self.hbar=tk.Scrollbar(self.examBox,orient=tk.HORIZONTAL)
        self.hbar.grid(row=1,column=0,sticky=tk.EW)
        self.hbar.config(command=self.resultCanvas.xview)
        self.vbar=tk.Scrollbar(self.examBox,orient=tk.VERTICAL)
        self.vbar.grid(row=0,column=1,sticky='NSE')
        self.vbar.config(command=self.resultCanvas.yview)
        self.resultCanvas.config(xscrollcommand=self.hbar.set,yscrollcommand=self.vbar.set)
        
        self.dicomExamsCanvas = tk.Canvas(master=self.dicomBox)
        self.dicomExamsCanvas.grid(row=0,column=0)
        
        self.dicomExamsSelector = tk.Frame(master=self.dicomBox)
        self.dicomExamsSelector.grid(row=0,column=1,sticky='NSWE')
        self.dicomExamsSelector.columnconfigure(0,weight=1,uniform='dicomExamsSelector')

        for index,img in enumerate(self.imgObj.dicomList):
            btn = tk.Button(master=self.dicomExamsSelector,command=lambda i=img:self.changeDicom(i.pixel_array))
            btn.grid(row=index,column=0,sticky='NSWE')
            self.dicomExamsSelector.rowconfigure(index,weight=1,uniform='dicomExamsSelector')
        
        self.changeDicom(self.imgObj.dicomList[0].pixel_array)
        self.createRoiInfoBox()
        self.createHistoryListBox()
        self.createDecayBox()

    def changeDicom(self,matrix):
        self.dicomExamsCanvas.delete("all")
        img = self.imgObj.getDicomImage(matrix)
        self.showDicom = ImageTk.PhotoImage(image=img,size=img.size)
        self.examDicomId = self.dicomExamsCanvas.create_image(0,0,anchor=tk.NW,image=self.showDicom,tags='showDicom')
        self.dicomExamsCanvas.configure(width=img.width,height=img.height)
        self.dicomExamsCanvas.update()

    def changeSelectedRoi(self,event):
        #a = [x for x in self.canvasElemList]
        selectedRoi = [x for x in self.canvasElemList if x.elmId == self.historyListbox.selection()[0]][0]
        if type(selectedRoi) == ROI:
            self.meanVar.set(selectedRoi.mean)
            self.stdVar.set(selectedRoi.std)
            self.minVar.set(selectedRoi.min)
            self.maxVar.set(selectedRoi.max)
            self.areaVar.set(selectedRoi.area)
            self.pixVar.set(selectedRoi.pix)
            self.mseVar.set(selectedRoi.mse)
            scale = Image.open(selectedRoi.decayImgFile)
            self.decayCanvas.delete("all")  
            size = (self.decayCanvas.winfo_width(),self.decayCanvas.winfo_height())
            #size[0] = scale.size[0] if size[0] > scale.size[0] else size[0]
            resizedScale = scale.resize(size) 
            selectedRoi.decayImg = ImageTk.PhotoImage(image=resizedScale,size=resizedScale.size)
            self.decayCanvas.create_image(int(self.decayCanvas.winfo_width()/2),0,anchor=tk.N,image=selectedRoi.decayImg)
            self.decayCanvas.update()    
        else:
            self.meanVar .set("")
            self.stdVar .set("")
            self.minVar .set("")
            self.maxVar .set("")
            self.areaVar .set("")
            self.pixVar .set("")
            self.mseVar.set("")
            self.decayCanvas.delete("all")   
        self.examFrame.winfo_toplevel().update_idletasks()

    def deleteSelectedRoi(self,event):
        removedRoi = [x for x in self.canvasElemList if x.elmId == self.historyListbox.focus()][0]
        self.historyListbox.delete(self.historyListbox.selection())
        self.canvasElemList.remove(removedRoi)
        self.imgObj.replaceRoi(self.canvasElemList)
        self.updateImage()

    def updateColor(self,min,max):
        self.imgObj.setColors(max,min)
        self.imgObj.plotFigure()
        self.imgObj.replaceRoi(self.canvasElemList)
        self.scaleColorValue.configure(from_=max,to=min,tickinterval=(max-min)/12)
        self.updateScaleCanvas(self.showColor)
        self.updateImage()

    def updateScaleCanvas(self,clock):
        img = self.imgObj.printColorScale(clock)
        self.scaleColorImage.update()
        img=img.resize((30,500))#self.scaleColorValue.winfo_height()
        self.scaleImg = ImageTk.PhotoImage(image=img,size=img.size)
        self.scaleImgId = self.scaleColorImage.create_image(0,0,anchor=tk.NW,image=self.scaleImg,tags='scaleImg')
        self.scaleColorImage.update()

    def changeColorGray(self):
        self.showColor = not self.showColor
        self.updateImage()
        self.updateScaleCanvas(self.showColor)

    def updateGray(self,min,max):
        self.imgObj.setGray(max,min)
        self.imgObj.plotFigure()
        self.imgObj.replaceRoi(self.canvasElemList)
        self.updateImage()

    def reDraw(self):
        drawList = [x for x in self.canvasElemList if type(x) == DrawnLines]
        for draw in drawList:
            for index in range(2,len(draw.dots)):
                #print(index)
                #Refaz todos os draws (processo rapido) utilizando 2 pontos por cada vez (até o 2 ponto usa todos os disponiveis)
                try:
                    splinePoints = list(sum(draw.dots[max(0,index-3):index], ()))
                    resizedPoints = list(map(lambda x:x*self.imgObj.activeZoom/draw.currentZoom,splinePoints))
                    self.resultCanvas.create_line(resizedPoints,width=10*draw.thickness,fill=draw.color,smooth=True)
                except:
                    print("draw came out of the canvas")
                    pass
    
    def reTag(self):
        tagList = [x for x in self.canvasElemList if type(x) == Tag]
        for tag in tagList:
            try:
                xResized = tag.x*self.imgObj.activeZoom
                yResized = tag.y*self.imgObj.activeZoom
                self.createPin(tag,xResized,yResized)
                #self.resultCanvas.create_text(xResized,yResized,font="Arial 12 bold",text=tag.text)
            except:
                print("text came out of the canvas")
                pass

    def addCanvasElement(self,element):
        self.canvasElemList.append(element)
        self.historyListbox.insert('',END,iid=element.elmId,values=(str(element),element.getInfo()))
        
    def createRoiInfoBox(self): 
        self.roiInfoBox = tk.LabelFrame(self.sideInfo,text='Roi Information')
        self.roiInfoBox.grid(row=1,column=0,sticky=tk.NSEW)
        #Desvio padrão Min Max Area pix
        self.meanLbl = tk.Label(self.roiInfoBox,justify=tk.RIGHT,text="Mean:")
        self.meanLbl.grid(row=0,column=0,sticky=tk.NE,pady=(5,0))
        self.stdLbl = tk.Label(self.roiInfoBox,justify=tk.RIGHT,text="Std:")
        self.stdLbl.grid(row=1,column=0,sticky=tk.NE,pady=(5,0))
        self.minLbl = tk.Label(self.roiInfoBox,justify=tk.RIGHT,text="Min:")
        self.minLbl.grid(row=2,column=0,sticky=tk.NE,pady=(5,0))
        self.maxLbl = tk.Label(self.roiInfoBox,justify=tk.RIGHT,text="Max:")
        self.maxLbl.grid(row=0,column=2,sticky=tk.NE,pady=(5,0))
        self.areaLbl = tk.Label(self.roiInfoBox,justify=tk.RIGHT,text="Area:")
        self.areaLbl.grid(row=1,column=2,sticky=tk.NE,pady=(5,0))
        self.pixLbl = tk.Label(self.roiInfoBox,justify=tk.RIGHT,text="pix:")
        self.pixLbl.grid(row=2,column=2,sticky=tk.NE,pady=(5,5))
        
        self.meanVar = tk.StringVar(self.roiInfoBox)
        self.stdVar = tk.StringVar(self.roiInfoBox)
        self.minVar = tk.StringVar(self.roiInfoBox)
        self.maxVar = tk.StringVar(self.roiInfoBox)
        self.areaVar = tk.StringVar(self.roiInfoBox)
        self.pixVar = tk.StringVar(self.roiInfoBox)

        self.meanInfo = tk.Label(self.roiInfoBox,textvariable=self.meanVar)
        self.meanInfo.grid(row=0,column=1,sticky=tk.NW,pady=(5,0))
        self.stdInfo = tk.Label(self.roiInfoBox,textvariable=self.stdVar)
        self.stdInfo.grid(row=1,column=1,sticky=tk.NW,pady=(5,0))
        self.minInfo = tk.Label(self.roiInfoBox,textvariable=self.minVar)
        self.minInfo.grid(row=2,column=1,sticky=tk.NW,pady=(5,0))
        self.maxInfo = tk.Label(self.roiInfoBox,textvariable=self.maxVar)
        self.maxInfo.grid(row=0,column=3,sticky=tk.NW,pady=(5,0))
        self.areaInfo = tk.Label(self.roiInfoBox,textvariable=self.areaVar)
        self.areaInfo.grid(row=1,column=3,sticky=tk.NW,pady=(5,0))
        self.pixInfo = tk.Label(self.roiInfoBox,textvariable=self.pixVar)
        self.pixInfo.grid(row=2,column=3,sticky=tk.NW,pady=(5,0))

    def createHistoryListBox(self):
        self.itemsBox = tk.LabelFrame(self.sideInfo,text='Edit history')
        self.itemsBox.grid(row=0,column=0,sticky=tk.NSEW)
        self.itemsBox.columnconfigure(0,weight=1)
        self.itemsBox.rowconfigure(0,weight=1)
        self.historyListbox = ttk.Treeview(self.itemsBox,columns=['Name','Info'],selectmode='browse')
        self.historyListbox.bind('<<TreeviewSelect>>',lambda event: self.changeSelectedRoi(event))
        self.historyListbox.event_add('<<DeleteTreeViewItem>>', '<Delete>')
        self.historyListbox.bind('<<DeleteTreeViewItem>>',lambda event: self.deleteSelectedRoi(event))
        self.historyListbox.column('#0',width=0,stretch=False)
        self.historyListbox.column('Name',width=100,stretch=False)
        self.historyListbox.heading('Name', text='Name')
        self.historyListbox.column('Info',stretch=True)
        self.historyListbox.heading('Info', text='Info')
        self.historyListbox.grid(row=0,column=0,sticky=tk.NSEW,pady=(10,0))

    def createDecayBox(self):
        self.decayBox = tk.LabelFrame(self.sideInfo,text='Decay and MSE')
        self.decayBox.grid(row=2,column=0,sticky=tk.NSEW)
        self.decayBox.columnconfigure(1,weight=1)
        self.decayBox.rowconfigure(0,weight=1)
        self.decayCanvas = tk.Canvas(master=self.decayBox)
        self.decayCanvas.grid(row=0,column=0,columnspan=2,sticky=tk.NSEW)
        self.mseLbl = tk.Label(self.decayBox,text="MSE:")
        self.mseLbl.grid(row=1,column=0,sticky=tk.SW,pady=5)
        self.mseVar = tk.StringVar(self.decayBox)
        self.mseInfo = tk.Label(self.decayBox,textvariable=self.mseVar)
        self.mseInfo.grid(row=1,column=1,sticky=tk.SW,pady=5)
        
    def showTag(self,event,tag):
        self.resultCanvas.delete(tag.tagId)
        self.resultCanvas.delete(tag.canvasId)
        tag = [x for x in self.canvasElemList if x.canvasId == tag.canvasId][0]
        
        text = '\n'.join(line.strip() for line in re.findall(r'.{1,30}(?:\s+|$)', tag.text))
        maxLine = max(map(len,text.splitlines()))
        rect = self.resultCanvas.create_rectangle(event.x,event.y,event.x+(maxLine*11),event.y+len(text.splitlines())*23,fill='gray77')
        self.resultCanvas.tag_bind(rect,'<ButtonPress-1>', lambda event:self.updateImage())       
        for i,t in enumerate(text.splitlines()):
            text = self.resultCanvas.create_text(event.x+5,event.y+(25*i),anchor=tk.NW,font="Arial 11",text=t)
            self.resultCanvas.tag_bind(text,'<ButtonPress-1>', lambda event:self.updateImage())       
    
    def saveCanvas(self):
        x=self.resultCanvas.winfo_rootx()#+self.resultCanvas.winfo_x()
        y=self.resultCanvas.winfo_rooty()#+self.resultCanvas.winfo_y()
        x1=x+self.resultCanvas.winfo_width()
        y1=y+self.resultCanvas.winfo_height()
        ImageGrab.grab().crop((x,y,x1,y1)).save(self.canvasPic)

    def createPin(self,tag,x,y):
        # + x and - y to shift the pin to right and up, to match the click with the point of the pin 
        tag.canvasId = self.resultCanvas.create_rectangle(x,y,x+30,y+25,fill='white',tags=tag.elmId)
        xSize = 10 if tag.canvasIndex <10 else 5 
        tag.tagId = self.resultCanvas.create_text(x+xSize,y+3,anchor=tk.NW,font="Arial 11 bold",text=tag.canvasIndex)
        self.resultCanvas.tag_bind(tag.canvasId, '<ButtonPress-1>', lambda event,t=tag:self.showTag(event,t))       
        self.resultCanvas.tag_bind(tag.tagId, '<ButtonPress-1>', lambda event,t=tag:self.showTag(event,t))       
        self.resultCanvas.update()    