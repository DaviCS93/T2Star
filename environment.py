from tkinter.constants import X
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
        self.examFrame.rowconfigure('0 1 2 3',weight=1,uniform='examFrame')
        self.examFrame.columnconfigure(0,weight=1)
        self.examFrame.grid(row=0,column=0,sticky=tk.NSEW)    
        self.resultCanvas = tk.Canvas(master=self.examFrame)
        self.resultCanvas.grid(row=0,rowspan=4,column=0)  

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