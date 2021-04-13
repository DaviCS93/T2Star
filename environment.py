import tkinter as tk
from PIL import ImageTk
from random import random

class Environment:

    def __init__(self, imgObj):
        # ID do exame TODO
        self.examID = str(random()).split('.')[-1]
        # Obj de imagem relacionado a esse ambiente (aba)
        self.imgObj = imgObj
        # Lista de Rois aplicadas na imagem
        self.roiList = [] #ROI()
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
        self.resultCanvas.update()
    
    def applyZoom(self,zoomIn):
        # zoomIn fica como o check para ver qual tipo de operação
        if zoomIn:
            self.imgObj.activeZoom *= self.zoomFactor
        else:
            self.imgObj.activeZoom /= self.zoomFactor
        self.updateImage()
            