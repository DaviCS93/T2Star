from scipy.signal.ltisys import impulse2
from decorators import timer
import matplotlib as matplot
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter.constants import END, NONE
from PIL import ImageTk,Image
from sys import exit as closeThread
from threading import Thread
from tkinter import BaseWidget, ttk,filedialog,simpledialog
from typing import ByteString
from ttkthemes import ThemedTk
import dicomHandler as dcmHandler
import editMenuMethods as edit
from enumInterface import Buttons as btns
from enumInterface import Labels as lbls
from enumInterface import Texts as txt
from enumInterface import TopMenuLabels as lblsTop
from enumInterface import Labelframes as lblsfrm
from environment import Environment
from errorHandler import LOGTYPE, printLog
from pdfHandler import PDF
from shape import Shape
import os
from canvasElements import DrawnLines,ROI,Tag

class MainForm():
    
    #Default for scales
    maxColor = 255
    minColor = 126

    def __init__(self):
        """
        Inicializa as variaveis usadas
        e também carrega o form principal
        """
        # Dicionário de ambientes (aba + exame)
        self.envDict = {}
        # Dicionário de exames
        self.examDict = {}
        # Lista de threads para carregar os exames
        self.loaderList = []
        self.scaleImageGray = None
        self.scaleImage = None
        self.envActive = self.job = None
        self.setForm()
        self.root.protocol("WM_DELETE_WINDOW", self.clearImages)
        self.root.mainloop()

    def setForm(self):
        """
        Basicamente chama os metodos de construção do form,
        separado por estrutura (menus, abas, etc)
        """
        self.setRoot()
        self.defineJet()
        self.defineGray()
        self.setMainFrame()
        self.setEditMenu()
        self.setPlotScales()

        self.setNotebook()

    def setRoot(self):
        self.root = ThemedTk(theme="Adapta")
        self.root.rowconfigure(0,weight=1)
        self.root.columnconfigure(0,weight=1)
        self.root.state('zoomed')
        
    def setMainFrame(self):
        self.mainFrame = ttk.Frame(self.root)
        self.mainFrame.grid(row=0,column=0,sticky=tk.NSEW)
        self.mainFrame.columnconfigure(0,weight=1,uniform="mainframe")
        self.mainFrame.columnconfigure(1,weight=4,uniform="mainframe")
        self.mainFrame.rowconfigure(0,weight=1,uniform="sideframe")
        self.mainFrame.bind(("<Escape>",self.clearCursor))

    def setEditMenu(self):
        self.drawThickness = tk.DoubleVar(self.root)

        self.color = 'black'
        self.editMenu = ttk.Frame(self.mainFrame)
        self.editMenu.grid(row=0,column=0,rowspan=2,sticky=tk.NSEW)
        self.editMenu.columnconfigure(0,weight=1)
        self.importBox = tk.LabelFrame(self.editMenu,text=lblsfrm.IMPORT)
        self.importBox.grid(row=0,column=0,sticky=tk.NSEW)
        self.importBox.rowconfigure(0,weight=1)
        self.importBox.columnconfigure('0 1',weight=1,uniform='editmenu')
        self.exportBox = tk.LabelFrame(self.editMenu,text=lblsfrm.EXPORT)
        self.exportBox.grid(row=1,column=0,sticky=tk.NSEW)
        self.exportBox.rowconfigure(0,weight=1)
        self.exportBox.columnconfigure('0 1',weight=1,uniform='editmenu')
        self.drawBox = tk.LabelFrame(self.editMenu,text=lblsfrm.DRAW)
        self.drawBox.grid(row=2,column=0,sticky=tk.NSEW)
        self.drawBox.rowconfigure(0,weight=1)
        self.drawBox.columnconfigure('0 1',weight=1,uniform='editmenu')
        self.roiBox = tk.LabelFrame(self.editMenu,text=lblsfrm.ROI)
        self.roiBox.grid(row=3,column=0,sticky=tk.NSEW)
        self.roiBox.rowconfigure(0,weight=1)
        self.roiBox.columnconfigure('0 1',weight=1,uniform='editmenu')
        self.zoomBox = tk.LabelFrame(self.editMenu,text=lblsfrm.ZOOM)
        self.zoomBox.grid(row=4,column=0,sticky=tk.NSEW)
        self.zoomBox.rowconfigure(0,weight=1)
        self.zoomBox.columnconfigure('0 1',weight=1,uniform='editmenu')
        self.tagBox = tk.LabelFrame(self.editMenu,text=lblsfrm.TAG)
        self.tagBox.grid(row=5,column=0,sticky=tk.NSEW)
        self.tagBox.rowconfigure(0,weight=1)
        self.tagBox.columnconfigure('0 1',weight=1,uniform='editmenu')
        self.colorBox = tk.LabelFrame(self.editMenu,text=lblsfrm.TAG)
        self.colorBox.grid(row=6,column=0,sticky=tk.NSEW)
        self.colorBox.rowconfigure(0,weight=1)
        self.colorBox.columnconfigure('0 1',weight=1,uniform='editmenu')
        self.scaleColorBox = tk.LabelFrame(self.editMenu,text=lblsfrm.SCALE_COLOR)
        self.scaleColorBox.grid(row=7,column=0,sticky=tk.NSEW)
        self.scaleColorBox.rowconfigure('0 1 2',weight=1)
        self.scaleColorBox.columnconfigure(0,weight=1,uniform='editmenu')
        self.scaleGrayBox = tk.LabelFrame(self.editMenu,text=lblsfrm.SCALE_GRAY)
        self.scaleGrayBox.grid(row=8,column=0,sticky=tk.NSEW)
        self.scaleGrayBox.rowconfigure('0 1',weight=1)
        self.scaleGrayBox.columnconfigure(0,weight=1,uniform='editmenu')

        ttk.Button(self.importBox,text=btns.IMPORT_NORMAL,command=lambda: self.loadExamNormal()).grid(row=0,column=0,padx=3,pady=5,sticky=tk.NSEW)
        ttk.Button(self.importBox,text=btns.IMPORT_BATCH,command=lambda: self.loadExamBatch()).grid(row=0,column=1,padx=3,pady=5,sticky=tk.NSEW)
        
        ttk.Button(self.exportBox,text=btns.EXPORT_DICOM,command=lambda: self.cbExportDicom()).grid(row=0,column=0,padx=3,pady=5,sticky=tk.NSEW)
        ttk.Button(self.exportBox,text=btns.EXPORT_PDF,command=lambda: self.cbExportPdf()).grid(row=0,column=1,padx=3,pady=5,sticky=tk.NSEW)
        
        ttk.Button(self.roiBox,text=btns.RECTANGLE,command=lambda: self.cbRoi(Shape.RECTANGLE)).grid(row=0,column=0,padx=3,pady=5,sticky=tk.NSEW)
        ttk.Button(self.roiBox,text=btns.CIRCLE,command=lambda: self.cbRoi(Shape.CIRCLE)).grid(row=0,column=1,padx=3,pady=5,sticky=tk.NSEW)
        ttk.Button(self.roiBox,text=btns.FREE,command=lambda: self.cbRoi(Shape.FREE)).grid(row=1,column=0,padx=3,pady=5,sticky=tk.NSEW)
        
        ttk.Button(self.drawBox,text=btns.DRAW,command=lambda: self.cbDraw()).grid(row=0,column=0,padx=3,pady=5,sticky=tk.NSEW)
        ttk.Scale(self.drawBox,orient=tk.HORIZONTAL,variable=self.drawThickness).grid(row=0,column=1,padx=3,pady=5,sticky=tk.NSEW)
        self.drawColorsMenu = ttk.Frame(self.drawBox)
        self.drawColorsMenu.grid(row=1,column=0,columnspan=2,padx=3,pady=5,sticky=tk.NSEW)
        self.drawColorsMenu.columnconfigure('0 1 2 3 4',weight=1)
        tk.Button(self.drawColorsMenu,bg=btns.BLUE,command=lambda: self.setColor('blue')).grid(row=0,column=0,padx=3,pady=5,sticky=tk.NSEW)
        tk.Button(self.drawColorsMenu,bg=btns.RED,command=lambda: self.setColor('red')).grid(row=0,column=1,padx=3,pady=5,sticky=tk.NSEW)
        tk.Button(self.drawColorsMenu,bg=btns.YELLOW,command=lambda: self.setColor('yellow')).grid(row=0,column=2,padx=3,pady=5,sticky=tk.NSEW)
        tk.Button(self.drawColorsMenu,bg=btns.GREEN,command=lambda: self.setColor('green')).grid(row=0,column=3,padx=3,pady=5,sticky=tk.NSEW)
        tk.Button(self.drawColorsMenu,bg=btns.BLACK,command=lambda: self.setColor('black')).grid(row=0,column=4,padx=3,pady=5,sticky=tk.NSEW)
        
        ttk.Button(self.tagBox,text=btns.TAG,command=lambda: self.cbTag()).grid(row=0,column=0,padx=3,pady=5,sticky=tk.NSEW)
        
        ttk.Button(self.zoomBox,text=btns.ZOOM_IN,command=lambda: self.cbZoom(True)).grid(row=0,column=0,padx=3,pady=5,sticky=tk.NSEW)
        ttk.Button(self.zoomBox,text=btns.ZOOM_OUT,command=lambda: self.cbZoom(False)).grid(row=0,column=1,padx=3,pady=5,sticky=tk.NSEW)
        
        self.changeColor = ttk.Button(self.colorBox,text=btns.COLOR2GRAY)
        self.changeColor.grid(row=0,column=0,padx=3,pady=5,sticky=tk.NSEW)
        self.changeColor.bind('<Button-1>',self.cbGrayColor)
        
        self.drawColorsMenu.grid_remove()

    def setPlotScales(self):
        # Setting values for the scales (Max Min and Red Scale)
        self.scalesColor = tk.LabelFrame(self.scaleColorBox)
        self.scaleMaxValueColor = tk.IntVar(self.scaleColorBox)
        self.scaleMinValueColor = tk.IntVar(self.scaleColorBox)
        self.scaleMaxValueGray = tk.IntVar(self.scaleGrayBox)
        self.scaleMinValueGray = tk.IntVar(self.scaleGrayBox)
        # self.scaleRedValue = tk.IntVar(self.scaleColorBox)
        # self.scaleRedValue.set(50)
        self.scaleGrayFile = f'{os.path.dirname(__file__)}\\imgs\\fixedscalegray.png','sgray',self.scaleGray
        self.scaleColorFile =f'{os.path.dirname(__file__)}\\imgs\\fixedscale.png','scolor',self.scaleRef
        # Setting max and min values for both max and min scales, and setting red to keep between them
        self.scaleMaxC = tk.Scale(self.scaleColorBox,command=lambda x:self.checkPlotColor())
        self.scaleMaxC.grid(row=0,column=0,padx=3,pady=5,sticky='SWE')
        self.scaleMaxC.configure(orient=tk.HORIZONTAL,variable=self.scaleMaxValueColor,label='Valor máximo')
        self.scaleMinC = tk.Scale(self.scaleColorBox,command=lambda x:self.checkPlotColor())
        self.scaleMinC.grid(row=1,column=0,padx=3,pady=5,sticky='SWE')
        self.scaleMinC.configure(orient=tk.HORIZONTAL,variable=self.scaleMinValueColor,label='Valor mínimo')
        self.scaleRef = tk.Canvas(master=self.scaleColorBox,height=20)
        self.scaleRef.grid(row=3,column=0,padx=3,pady=5,sticky='SWE')  
        
        self.scaleMaxG = tk.Scale(self.scaleGrayBox,command=lambda x:self.checkPlotGray())
        self.scaleMaxG.grid(row=4,column=0,padx=3,pady=5,sticky='SWE')
        self.scaleMaxG.configure(orient=tk.HORIZONTAL,variable=self.scaleMaxValueGray,label='Valor máximo')
        self.scaleMaxG.configure(to=255,from_=128)
        self.scaleMinG = tk.Scale(self.scaleGrayBox,command=lambda x:self.checkPlotGray())
        self.scaleMinG.grid(row=5,column=0,padx=3,pady=5,sticky='SWE')
        self.scaleMinG.configure(orient=tk.HORIZONTAL,variable=self.scaleMinValueGray,label='Valor mínimo')
        self.scaleMinG.configure(to=127,from_=0)
        self.scaleGray = tk.Canvas(master=self.scaleGrayBox,height=20)
        self.scaleGray.grid(row=6,column=0,padx=3,pady=5,sticky='SWE')
        self.scaleImageGray = self.printScale(self.scaleGrayFile)
        self.scaleImage  = self.printScale(self.scaleColorFile)
        self.configureColorScale(self.scaleMaxC,self.scaleMinC)
        self.configureColorScale(self.scaleMaxG,self.scaleMinG)

    def configureColorScale(self,scaleMax,scaleMin,minRoof=None,maxFloor=None):
        '''
        The ideia here is to set maximum and minimum values for the scales following the logic:
        
        |0-----min--------max-----250|\n
        |0---------red------------100|

        min can go from 0 to max\n
        max can go from min to 250\n
        red can go from 0 to 100%
        '''
        self.plotRoof = 250
        self.plotFloor = 0
        if minRoof == None:
            minRoof = self.maxColor
        if maxFloor == None:
            maxFloor = self.minColor
        scaleMax.configure(to=self.plotRoof,from_=maxFloor+20,tickinterval=(self.plotRoof-maxFloor)/12)
        scaleMin.configure(to=minRoof-20,from_=self.plotFloor,tickinterval=(minRoof-self.plotFloor)/12)

    def printScale(self,imgFile,imgType,canvas):
        scale = Image.open(imgFile)
        canvas.update()    
        resizedScale = scale.resize((canvas.master.winfo_width(),20)) 
        img = ImageTk.PhotoImage(image=resizedScale,size=resizedScale.size)
        canvas.create_image(0,0,anchor=tk.NW,image=img,tags=imgType)
        canvas.update()    
        return img        

    def checkPlotColor(self):
        if self.job:
            self.root.after_cancel(self.job)
        if self.envActive:
            ma,mi = self.scaleMaxValueColor.get(),self.scaleMinValueColor.get()
            if (self.envActive.imgObj.maxColor != ma 
                or self.envActive.imgObj.minColor != mi):
                def changePlotColor(self,ma,mi):
                    self.envActive.updateColor(mi,ma)
                    self.configureColorScale(self.scaleMaxC,self.scaleMinC,ma,mi)
                self.job = self.root.after(300,changePlotColor,self,ma,mi)              

    def checkPlotGray(self):
        if self.job:
            self.root.after_cancel(self.job)
        if self.envActive:
            ma,mi = self.scaleMaxValueGray.get(),self.scaleMinValueGray.get()
            if (self.envActive.imgObj.maxColor != ma 
                or self.envActive.imgObj.minColor != mi):
                def changePlotGray(self,ma,mi):
                    self.envActive.updateGray(mi,ma)
                    self.configureColorScale(self.scaleMaxG,self.scaleMinG,ma,mi)
                self.job = self.root.after(300,changePlotGray,self,ma,mi)              

    def setColor(self,c):
        if self.envActive:
            self.color = c

    def setNotebook(self):
        self.notebook = ttk.Notebook(self.mainFrame,name=txt.NOTEBOOK)
        self.notebook.grid(row=0,column=1,rowspan=2,sticky=tk.NSEW)
        self.root.update()

    def loader(self,examID,dicomList):
        """
        Alvo da thread para criação de novos ambientes (abas)
        """
        self.envActive = Environment(examID,dicomList)
        self.loadImageNotebook()

    def loadExamBatch(self):
        """
        Carrega os exames através do handler
        """
        files =  filedialog.askopenfilenames()
        if not files:
            return
        examName = simpledialog.askstring(lbls.NAME_EXAM_WINDOW,lbls.NAME_EXAM_LABEL)
        if not examName:
            return
        batchQty = simpledialog.askinteger(lbls.BATCH_EXAM_WINDOW,lbls.BATCH_EXAM_LABEL,"Type the number of echos for each image")
        if not batchQty:
            return
        examDict = dcmHandler.openDicomFiles(files,examName,batchQty)
        for examID,dicomList in examDict.items():
                self.loader(examID.lower(),dicomList)

    def loadExamNormal(self):
        """
        Carrega os exames através do handler
        """
        files =  filedialog.askopenfilenames()
        if not files:
            return        
        examName = simpledialog.askstring("Name Request","Write an name for the exam")
        if not examName:
            return
        examDict = dcmHandler.openDicomFiles(files,examName)
        for examID,dicomList in examDict.items():
                self.loader(examID.lower(),dicomList)
  
    def onEnvChange(self,event):
        self.job = None
        self.envActive = self.envDict[self.notebook.index(self.notebook.select())]
        self.defineColorBtn()
        if self.envActive:
            self.scaleMaxValueColor.set(self.envActive.imgObj.maxColor)
            self.scaleMinValueColor.set(self.envActive.imgObj.minColor)
            self.scaleMaxValueGray.set(self.envActive.imgObj.maxGray)
            self.scaleMinValueGray.set(self.envActive.imgObj.minGray)
            self.configureColorScale(self.scaleMaxC,self.scaleMinC,self.envActive.imgObj.maxColor,self.envActive.imgObj.minColor)
            self.clearCursor()

    def defineColorBtn(self):
        if self.envActive.showColor:
            self.changeColor.configure(text=btns.COLOR2GRAY)
        else:
            self.changeColor.configure(text=btns.GRAY2COLOR)

    def cbGrayColor(self,event):
        self.clearCursor()
        if self.envActive:
            self.envActive.changeColorGray()
            self.defineColorBtn()

    def cbRoi(self,shape):
        self.clearCursor()
        if self.envActive:
            self.envActive.resultCanvas.tag_bind(
                self.envActive.examCanvasId,"<ButtonPress-1>", lambda event: edit.startRoi(
                env=self.envActive,event=event,shape=shape))
            self.envActive.resultCanvas.tag_bind(
                self.envActive.examCanvasId,"<B1-Motion>", lambda event: edit.onMoveRoi(
                env=self.envActive,event=event))
            self.envActive.resultCanvas.tag_bind(
                self.envActive.examCanvasId,"<ButtonRelease-1>", lambda event: edit.releaseRoi(
                env=self.envActive,event=event))

    def cbDraw(self):
        self.clearCursor()
        if self.envActive:
            self.drawColorsMenu.grid()
            #cnv =self.envActive.resultCanvas
            self.envActive.resultCanvas.tag_bind(
                self.envActive.examCanvasId,"<ButtonPress-1>", lambda event: edit.startDraw(
                event=event,env=self.envActive,thickness=self.drawThickness.get(),color=self.color))
            self.envActive.resultCanvas.tag_bind(
                self.envActive.examCanvasId,"<B1-Motion>", lambda event:edit.onMoveDraw(
                event=event,env=self.envActive,thickness=self.drawThickness.get(),color=self.color))
            self.envActive.resultCanvas.tag_bind(
                self.envActive.examCanvasId,"<ButtonRelease-1>", lambda event: edit.releaseDraw(
                env=self.envActive,event=event))

    def cbZoom(self,zoomIn):
        self.clearCursor()
        if self.envActive:
            self.envActive.resultCanvas.bind(
            "<ButtonRelease-1>", lambda event: edit.zoom(
                env=self.envActive,zoomIn=zoomIn,event=event))

    def cbTag(self):
        self.clearCursor()
        if self.envActive:
            self.envActive.resultCanvas.tag_bind(
                self.envActive.examCanvasId,"<ButtonPress-1>", lambda event: edit.startTag(
                env=self.envActive,event=event))

    def cbExportPdf(self):
        self.clearCursor()
        if self.envActive:
            if self.envActive.showColor:
                self.envActive.changeColorGray()
                self.envActive.saveCanvas()
                self.envActive.changeColorGray()
            else:
                self.envActive.saveCanvas()
            pdf = PDF(f'T2 Map Report - {self.envActive.examID}',orientation='P',unit='mm',format='A4')
            pdf.add_page()
            scale = f"{os.path.dirname(__file__)}\\imgs\\scale{self.envActive.examID}.png"
            pdf.print_base(self.envActive.imgObj.colorName,self.envActive.canvasPic,scale)
            pdf.print_rois([x for x in self.envActive.canvasElemList if type(x) == ROI])
            pdf.print_labels([x for x in self.envActive.canvasElemList if type(x) == Tag],self.envActive.canvasPic)
            dirName = 'Reports'
            if not os.path.exists(dirName):
                os.mkdir(dirName)
            pdf.output(os.path.join(os.path.dirname(__file__),dirName,f'{self.envActive.examID}.pdf'), 'F')
            tk.messagebox.showinfo(title=None, message='PDF exportado!')

    def loadImageNotebook(self):
        """
        Create a image in the notebook for the environment. The image is loaded in a tab in
        the notebook
        Input: Environment (env)
        Output: Frame inside the tab where the image is set (frm)
        """
        try:
            # Cria o frame e o canvas do exame usando o frame
            # definido como tab dentro do notebook
            self.envActive.createExamViewer(self.createTab(self.envActive.examID))
            # self.envDict[len(self.notebook.tabs())-1] = self.envActive
            # self.notebook.select(len(self.notebook.tabs())-1)
            self.envDict[len(self.notebook.children)-1] = self.envActive
            if len(self.notebook.event_info())>0:
                self.notebook.bind("<<NotebookTabChanged>>", self.onEnvChange)
            self.envActive.updateImage()
            self.notebook.select(len(self.notebook.tabs())-1)
            self.root.update()
        except Exception as ex:
            printLog(LOGTYPE.ERROR_LOAD_IMG_NOTEBOOK,ex)

    def createTab(self,exam):
        frm = ttk.Frame(self.notebook,name=exam)
        self.notebook.add(frm,text=exam)
        frm.rowconfigure(0,weight=1)
        frm.columnconfigure(0,weight=1,uniform='notebook')
        return frm

    def clearCursor(self):
        for key in self.envDict:
            # frmName = self.notebook.select()
            # frm = self.root.nametowidget(frmName)
            # for cnvName in frm.children[txt.EXAMIMAGE].children:
            # Pega o canvas atual
            cnv = self.envDict[key].resultCanvas
            tag = self.envDict[key].examCanvasId
            # cnv = self.root.nametowidget(".".join((frmName,txt.EXAMIMAGE,cnvName)))
            self.drawColorsMenu.grid_remove()
            cnv.unbind("<ButtonRelease-1>")
            cnv.tag_unbind(tag,"<ButtonPress-1>")
            cnv.tag_unbind(tag,"<B1-Motion>")
            cnv.tag_unbind(tag,"<ButtonRelease-1>")

    def clearImages(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        for key in self.envDict.keys():  
            self.envDict[key].imgObj .resultImage = None
            self.envDict[key].imgObj = None
            self.envDict[key] = None
        for filename in os.listdir(f"{os.path.dirname(__file__)}\\imgs"):
            if 'fixedscale' not in filename:
                os.remove(f"{os.path.dirname(__file__)}\\imgs\\{filename}")
        self.root.mainloop
        self.root.quit()
        self.root.destroy()

    def cbExportDicom(self):
        if self.envActive:
            dcmHandler.exportDicom(self.envActive.imgObj.imgMatrix,self.envActive.imgObj.dicomList[0])
    
    @timer    
    def defineGray(self):
        """
        docstring
        """
        gray = matplot.cm.get_cmap(name='gray')
        gradient = np.linspace(0, 1, 255)
        gradient = np.vstack((gradient, gradient))
        fig, ax = plt.subplots(nrows=1, figsize=(10, 1))
        ax.imshow(gradient, aspect='auto', cmap=gray)
        ax.set_axis_off()
        plt.savefig(f"{os.path.dirname(__file__)}\\imgs\\fixedscalegray.png",bbox_inches = 'tight', dpi=200)
        plt.close()
        #return gray
        
    @timer    
    def defineJet(self):
        """
        docstring
        """
        jet = matplot.cm.get_cmap(name='jet')
        gradient = np.linspace(0, 1, 255)
        gradient = np.vstack((gradient, gradient))
        fig, ax = plt.subplots(nrows=1, figsize=(10, 1))
        ax.imshow(gradient, aspect='auto', cmap=jet)
        ax.set_axis_off()
        plt.savefig(f"{os.path.dirname(__file__)}\\imgs\\fixedscale.png",bbox_inches = 'tight', dpi=200)
        plt.close()
        #return jet

if __name__ == "__main__":
    main = MainForm()
    pass
