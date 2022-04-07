import os
import time
import pydicom
from tkinter import filedialog as dialog
import tkinter as tk
from imgObject import imgObject
from math import floor,inf
import numpy as np

# Handler responsável por abrir os arquivos dicom
# e extrair as informações + imagens

def openDicomFiles(files,examName,quantity=None):
    """
    docstring
    """
    # Dicionário de exames geral (ExamID - lista de arquivos)
    examFileDict = {}   
    # Lista de exames com o mesmo ID
    if quantity:
        for index,f in enumerate(files):
            key = ''.join((examName,str(floor(index/quantity))))
            dcm = pydicom.dcmread(f)
            if not key in examFileDict.keys():
                examFileDict[key] = [dcm]
            else: 
                examFileDict[key].append(dcm)
    else:
        for f in files:
            dcm = pydicom.dcmread(f)
            if not examName in examFileDict.keys():
                examFileDict[examName] = [dcm]
            else: 
                examFileDict[examName].append(dcm)
    return examFileDict

def exportDicom(env,dir):
    
    #dcm.pixel_array = img
    #img = img*1000
    img = np.array(env.imgObj.imgMatrix,dtype=np.uint16)
    env.imgObj.dicomList[0].PixelData = img.tobytes()
    env.imgObj.dicomList[0].save_as(f"{dir}\\{env.examID}.dcm")