import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
from enumInterface import Texts as txt
from imgObject import imgObject as imgObj
from threading import Thread


class Environment:

    def __init__(self,examID,dicomList):
        # ID do exame TODO
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
        drawList = [x for x in self.canvasElemList if type(x) == list]
        for draw in drawList:
            coordList = [x.coords for x in draw]
            for index in range(5,len(coordList)):
                #print(index)
                self.resultCanvas.create_line(list(sum(coordList[max(0,index-5):index], ())),width=10*draw[-1].thickness,smooth=True)
        self.resultCanvas.update()
    
    def applyZoom(self,zoomIn):
        # zoomIn fica como o check para ver qual tipo de operação
        if zoomIn:
            self.imgObj.activeZoom *= self.zoomFactor
        else:
            self.imgObj.activeZoom /= self.zoomFactor

    def createExamViewer(self,frm):
        self.examFrame = ttk.Frame(frm,name=txt.EXAMIMAGE)
        self.examFrame.rowconfigure('0 1 2 3',weight=1,uniform='examFrame')
        self.examFrame.columnconfigure(0,weight=1)
        self.examFrame.grid(row=0,column=0,sticky=tk.NSEW)    
        self.resultCanvas = tk.Canvas(master=self.examFrame)
        self.resultCanvas.grid(row=0,rowspan=4,column=0)  
        self.createColorScale()

    def createColorScale(self):
        self.maxColorScale = tk.DoubleVar(self.examFrame)
        self.minColorScale = tk.DoubleVar(self.examFrame)
        self.maxUpScaleStr = tk.StringVar(self.examFrame)
        self.minUpScaleStr = tk.StringVar(self.examFrame)
        self.maxLoScaleStr = tk.StringVar(self.examFrame)
        self.minLoScaleStr = tk.StringVar(self.examFrame)

        self.maxUpScaleStr.set(self.imgObj.maxColor)
        self.minUpScaleStr.set(int(self.imgObj.maxColor/2))
        self.maxLoScaleStr.set(int(self.imgObj.maxColor/2))
        self.minLoScaleStr.set(self.imgObj.minColor)

        self.upperColorScale = ttk.Scale(self.examFrame,orient=tk.VERTICAL,variable=self.maxColorScale).grid(row=0,column=1,rowspan=2,sticky='NSW')
        self.lowerColorScale = ttk.Scale(self.examFrame,orient=tk.VERTICAL,variable=self.minColorScale).grid(row=2,column=1,rowspan=2,sticky='NSW')
        self.maxUpperScaleLabel = ttk.Label(self.examFrame,textvariable=self.maxUpScaleStr).grid(row=0,column=2,sticky=tk.NW)
        self.minUpperScaleLabel = ttk.Label(self.examFrame,textvariable=self.minUpScaleStr).grid(row=1,column=2,sticky=tk.SW)
        self.maxLowerScaleLabel = ttk.Label(self.examFrame,textvariable=self.maxLoScaleStr).grid(row=2,column=2,sticky=tk.NW)
        self.minLowerScaleLabel = ttk.Label(self.examFrame,textvariable=self.minLoScaleStr).grid(row=3,column=2,sticky=tk.SW)
        
        #self.scalesWatcher = Thread(self.updateColor)
        # self.scalesWatcher.start()
    
    def updateColor(self):
        pass