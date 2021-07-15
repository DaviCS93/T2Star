from os import remove
from tkinter.constants import X,END
from canvasElements import DrawnLines,ROI,Tag
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
from enumInterface import Texts as txt
from imgObject import imgObject as imgObj
from threading import Thread
from decorators import timer

class Environment:

    def __init__(self,examID,dicomList):
        # ID do exame
        self.examID = examID
        # Obj de imagem relacionado a esse ambiente (aba)
        self.imgObj = imgObj(dicomList)
        # Lista de Rois aplicadas na imagem
        #self.roiList = [] #ROI()
        # Lista de Draws aplicadas na imagem
        #self.drawList = [] 
        self.canvasElemList = []
        # Canvas da imagem (para poder desenhar as roi's)
        self.resultCanvas = None
        # Frame de apresentação da imagem do exame
        self.examFrame = None
        # Imagem printada no final
        # Roi ativa para desenhar a forma + deletar a forma no fim
        self.activeROI = None
        # Taxa de zoom
        self.zoomFactor = 1.2
        self.historyListItems = tk.StringVar()

    @timer
    def updateImage(self):
        # Limpa o canvas (deleta a imagem antiga)
        self.resultCanvas.delete("all")
        # Aplica o zoom sobre uma copia da imagem logo antes de apresentar,
        # para evitar distorções na imagem original
        zoomedImage = self.imgObj.resultImage.resize(
            (int(self.imgObj.resultImage.width*self.imgObj.activeZoom),
            int(self.imgObj.resultImage.height*self.imgObj.activeZoom)))
        # Print final e atualização do canvas
        self.printImage = ImageTk.PhotoImage(image=zoomedImage,size=zoomedImage.size)
        self.resultCanvas.create_image(0,0,anchor=tk.NW,image=self.printImage,tags='printImage')
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

    def createExamViewer(self,frm):
        self.examFrame = ttk.Frame(frm,name=txt.EXAMIMAGE)
        self.examFrame.rowconfigure(0,weight=1)
        self.examFrame.columnconfigure(0,weight=4,uniform='examFrame')
        self.examFrame.columnconfigure(1,weight=2,uniform='examFrame')
        self.examFrame.grid(row=0,column=0,sticky=tk.NSEW)    
        
        self.examBox = tk.LabelFrame(self.examFrame,text=self.examID)
        self.examBox.grid(row=0,column=0,sticky=tk.NSEW)
        self.examBox.rowconfigure(0,weight=1)
        self.examBox.columnconfigure(0,weight=1)
        
        self.sideInfo = ttk.Frame(self.examFrame)
        self.sideInfo.grid(row=0,column=1,sticky=tk.NSEW)
        self.sideInfo.rowconfigure('0 2',weight=1,uniform='sideframe')

        self.resultCanvas = tk.Canvas(master=self.examBox)
        self.resultCanvas.grid(row=0,column=0)

        self.createRoiInfoBox()
        self.createHistoryListBox()
        self.createDecayBox()

    def changeSelectedRoi(self,event):
        selectedRoi = [x for x in self.canvasElemList if x.elmId == self.historyListbox.selection()][0]
        if type(selectedRoi) == ROI:
            self.meanVar = selectedRoi.mean
            self.stdVar = selectedRoi.std
            self.minVar = selectedRoi.min
            self.maxVar = selectedRoi.max
            self.areaVar = selectedRoi.area
            self.pixVar = selectedRoi.pix
        else:
            self.meanVar = ""
            self.stdVar = ""
            self.minVar = ""
            self.maxVar = ""
            self.areaVar = ""
            self.pixVar = ""

    def deleteSelectedRoi(self,event):
        removedRoi = [x for x in self.canvasElemList if x.elmId == self.historyListbox.selection()[0]][0]
        self.historyListbox.delete(self.historyListbox.selection())
        self.canvasElemList.remove(removedRoi)
        self.imgObj.replaceRoi(self.canvasElemList)
        self.updateImage()

    def updateColor(self,redScale,min,max):
        self.imgObj.setColors(max,min,redScale)
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
                self.resultCanvas.create_text(xResized,yResized,font="Arial 12 bold",text=tag.text)
            except:
                print("text came out of the canvas")
                pass

    def addCanvasElement(self,element):
        self.canvasElemList.append(element)
        self.historyListbox.insert('',END,iid=element.elmId,values=(str(element),element.getInfo()))

    def createRoiInfoBox(self): 
        self.roiInfoBox = tk.LabelFrame(self.sideInfo,text='Roi Information')
        self.roiInfoBox.grid(row=1,column=1,sticky=tk.NSEW)
        #Desvio padrão Min Max Area pix
        self.meanLbl = tk.Label(self.roiInfoBox,justify=tk.RIGHT,text="Mean:")
        self.meanLbl.grid(row=0,column=0,sticky=tk.NE,pady=(5,0))
        self.stdLbl = tk.Label(self.roiInfoBox,justify=tk.RIGHT,text="Std:")
        self.stdLbl.grid(row=1,column=0,sticky=tk.NE,pady=(5,0))
        self.minLbl = tk.Label(self.roiInfoBox,justify=tk.RIGHT,text="Min:")
        self.minLbl.grid(row=2,column=0,sticky=tk.NE,pady=(5,0))
        self.maxLbl = tk.Label(self.roiInfoBox,justify=tk.RIGHT,text="Max:")
        self.maxLbl.grid(row=3,column=0,sticky=tk.NE,pady=(5,0))
        self.areaLbl = tk.Label(self.roiInfoBox,justify=tk.RIGHT,text="Area:")
        self.areaLbl.grid(row=4,column=0,sticky=tk.NE,pady=(5,0))
        self.pixLbl = tk.Label(self.roiInfoBox,justify=tk.RIGHT,text="pix:")
        self.pixLbl.grid(row=5,column=0,sticky=tk.NE,pady=(5,5))
        
        self.meanVar = tk.StringVar(self.roiInfoBox)
        self.stdVar = tk.StringVar(self.roiInfoBox)
        self.minVar = tk.StringVar(self.roiInfoBox)
        self.maxVar = tk.StringVar(self.roiInfoBox)
        self.areaVar = tk.StringVar(self.roiInfoBox)
        self.pixVar = tk.StringVar(self.roiInfoBox)

        self.meanInfo = tk.Label(self.roiInfoBox,textvariable=self.meanVar)
        self.meanInfo.grid(row=1,column=1,sticky=tk.NW)
        self.minInfo = tk.Label(self.roiInfoBox,textvariable=self.minVar)
        self.minInfo.grid(row=2,column=1,sticky=tk.NW)
        self.maxInfo = tk.Label(self.roiInfoBox,textvariable=self.maxVar)
        self.maxInfo.grid(row=3,column=1,sticky=tk.NW)
        self.areaInfo = tk.Label(self.roiInfoBox,textvariable=self.areaVar)
        self.areaInfo.grid(row=4,column=1,sticky=tk.NW)
        self.pixInfo = tk.Label(self.roiInfoBox,textvariable=self.pixVar)
        self.pixInfo.grid(row=5,column=1,sticky=tk.NW)

    def createHistoryListBox(self):
        self.itemsBox = tk.LabelFrame(self.sideInfo,text='Edit history')
        self.itemsBox.grid(row=0,column=1,sticky=tk.NSEW)
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
        self.decayBox.grid(row=2,column=1,sticky=tk.NSEW)
        self.decayBox.columnconfigure(2,weight=1)
        self.decayBox.rowconfigure(0,weight=1)
        self.decayCanvas = tk.Canvas(master=self.decayBox)
        self.decayCanvas.grid(row=0,column=0,columnspan=2)
        self.mseLbl = tk.Label(self.decayBox,text="MSE:")
        self.mseLbl.grid(row=1,column=0,sticky=tk.SW)
        self.mseVar = tk.StringVar(self.decayBox)
        self.mseInfo = tk.Label(self.decayBox,textvariable=self.mseVar)
        self.mseInfo.grid(row=1,column=1,sticky=tk.SW,pady=20)
        
