import os
import time
import pydicom
from tkinter import filedialog as dialog
from imgObject import imgObject

# Handler responsável por abrir os arquivos dicom
# e extrair as informações + imagens

def openDicomFiles():
    """
    docstring
    """
    # Dicionário de exames geral (ExamID - lista de arquivos)
    examFileDict = {}   
    # Lista de exames com o mesmo ID
    files = dialog.askopenfilenames()
    for f in files:
        dcm = pydicom.dcmread(f)
        if dcm.StudyID in examFileDict.keys():
            examFileDict[dcm.StudyID].append(dcm)
        else:
            examFileDict[dcm.StudyID] = [dcm]
    return examFileDict


    