import os
import time
import pydicom
from tkinter import filedialog as dialog
from imgObject import imgObject

#remover - transformar em func
class ImgHandler():
    """
    """
    def __init__(self):
        self.listImg = []
        self.size = [0,0]

    def defineListEcho(self):
        """
        docstring
        """
        ####SEPARAR POR EXAME
        files = dialog.askopenfilenames()
        #imageFolder = "C:\\Users\\Feirron\\Downloads\\MAPAS\\Mapas T2 - Melhorias\\Processamento normal\\"
        #files = os.listdir(imageFolder)
        #files = [imageFolder + f for f in files]
        dl = []
        for f in files:
            dl.append(pydicom.dcmread(f))
            #TODO Ler o dicom e separar para cada exame uma imagem
        self.listImg.append(imgObject(dl))

    def createROI(self):
        """
        docstring
        """
        pass

   
    def deleteROI(self):
        """
        docstring
        """
        pass

if __name__ == "__main__":
    handler = ImgHandler()
    handler.defineListEcho()
    for img in handler.listImg:
        imgObject.plotFigure
        img.createFigure()
        img.plotFigure(False)
        img.saveImg()    
    