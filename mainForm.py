import tkinter as tk
from tkinter.constants import END, NONE
from PIL import ImageTk,Image
from sys import exit as closeThread
from threading import Thread
from tkinter import BaseWidget, ttk
from typing import ByteString
from ttkthemes import ThemedTk
import dicomHandler as dcmHandler
import editMenuMethods as edit
from enumInterface import Buttons as btns
from enumInterface import Labels as lbls
from enumInterface import Texts as txt
from enumInterface import TopMenuLabels as lblsTop
from environment import Environment
from errorHandler import LOGTYPE, printLog
from shape import Shape
from os import path

class MainForm():
    
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
        self.root.mainloop()

    def setForm(self):
        """
        Basicamente chama os metodos de construção do form,
        separado por estrutura (menus, abas, etc)
        """
        self.setRoot()
        self.setMainFrame()
        self.setEditMenu()
        self.setPlotScales()

        self.setNotebook()
        self.setTopMenu()

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
        #self.editMenu.columnconfigure(0,weight=1)
        ttk.Button(self.editMenu,text=btns.RECTANGLE,command=lambda: self.cbRoi(Shape.RECTANGLE)).grid(row=1,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.CIRCLE,command=lambda: self.cbRoi(Shape.CIRCLE)).grid(row=2,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.DRAW,command=lambda: self.cbDraw()).grid(row=3,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.TAG,command=lambda: self.cbTag()).grid(row=5,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.ZOOM_IN,command=lambda: self.cbZoom(True)).grid(row=6,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.ZOOM_OUT,command=lambda: self.cbZoom(False)).grid(row=7,column=0,sticky=tk.NW)
        ttk.Scale(self.editMenu,orient=tk.HORIZONTAL,variable=self.drawThickness).grid(row=4,column=0,columnspan=4,sticky=tk.NW)
        self.drawColorsMenu = ttk.Frame(self.editMenu)
        self.drawColorsMenu.grid(row=8,column=1,sticky=tk.NW)
        tk.Button(self.drawColorsMenu,bg=btns.BLUE,command=lambda: self.setColor('blue')).grid(row=0,column=0,sticky=tk.NW)
        tk.Button(self.drawColorsMenu,bg=btns.RED,command=lambda: self.setColor('red')).grid(row=0,column=1,sticky=tk.NW)
        tk.Button(self.drawColorsMenu,bg=btns.YELLOW,command=lambda: self.setColor('yellow')).grid(row=0,column=2,sticky=tk.NW)
        tk.Button(self.drawColorsMenu,bg=btns.GREEN,command=lambda: self.setColor('green')).grid(row=0,column=3,sticky=tk.NW)
        tk.Button(self.drawColorsMenu,bg=btns.BLACK,command=lambda: self.setColor('black')).grid(row=0,column=4,sticky=tk.NW)
        self.drawColorsMenu.grid_remove()

    def setPlotScales(self):
        self.scalesMenu = ttk.Frame(self.editMenu)
        self.scalesMenu.grid(row=10,column=0,columnspan=4,sticky=tk.SW)
        # Setting values for the scales (Max Min and Red Scale)
        self.scalesColor = tk.LabelFrame(self.scalesMenu)
        self.scaleMaxValueColor = tk.IntVar(self.scalesMenu)
        self.scaleMinValueColor = tk.IntVar(self.scalesMenu)
        self.scaleRedValue = tk.IntVar(self.scalesMenu)
        self.scaleMaxValueGray = tk.IntVar(self.scalesMenu)
        self.scaleMinValueGray = tk.IntVar(self.scalesMenu)
        self.scaleRedValue = tk.IntVar(self.scalesMenu)
        self.scaleRedValue.set(50)
        # Setting max and min values for both max and min scales, and setting red to keep between them


        self.scaleMaxC = tk.Scale(self.scalesMenu,command=lambda x:self.checkPlotColor())
        self.scaleMaxC.grid(row=0,column=0,sticky='SWE')
        self.scaleMaxC.configure(orient=tk.HORIZONTAL,variable=self.scaleMaxValueColor,label='Max value')
        self.scaleMinC = tk.Scale(self.scalesMenu,command=lambda x:self.checkPlotColor())
        self.scaleMinC.grid(row=1,column=0,sticky='SWE')
        self.scaleMinC.configure(orient=tk.HORIZONTAL,variable=self.scaleMinValueColor,label='Min value')
        self.scaleRed = tk.Scale(self.scalesMenu,command=lambda x:self.checkPlotColor())
        self.scaleRed.configure(orient=tk.HORIZONTAL,variable=self.scaleRedValue,label='Red position')
        self.scaleRed.grid(row=2,column=0,sticky='SWE')
        self.scaleRef = tk.Canvas(master=self.scalesMenu)
        self.scaleRef.grid(row=3,column=0,sticky='SWE')  
        
        self.scaleMaxG = tk.Scale(self.scalesMenu,command=lambda x:self.checkPlotGray())
        self.scaleMaxG.grid(row=4,column=0,sticky='SWE')
        self.scaleMaxG.configure(orient=tk.HORIZONTAL,variable=self.scaleMaxValueGray,label='Upper value')
        self.scaleMaxG.configure(to=255,from_=128)
        self.scaleMinG = tk.Scale(self.scalesMenu,command=lambda x:self.checkPlotGray())
        self.scaleMinG.grid(row=5,column=0,sticky='SWE')
        self.scaleMinG.configure(orient=tk.HORIZONTAL,variable=self.scaleMinValueGray,label='Lower value')
        self.scaleMinG.configure(to=127,from_=0)
        self.scaleGray = tk.Canvas(master=self.scalesMenu)
        self.scaleGray.grid(row=6,column=0,sticky='SWE')
        self.scaleImageGray = self.printScale(f'{path.dirname(__file__)}\\imgs\\scalegray.png','sgray',self.scaleGray)
        self.scaleImage  = self.printScale(f'{path.dirname(__file__)}\\imgs\\scale.png','scolor',self.scaleRef)

    def configureColorScale(self,minRoof=None,maxFloor=None):
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
            minRoof = self.scaleMaxValueColor.get()
        if maxFloor == None:
            maxFloor =self.scaleMinValueColor.get()
        self.scaleMaxC.configure(to=self.plotRoof,from_=maxFloor+20,tickinterval=(self.plotRoof-maxFloor)/10)
        self.scaleMinC.configure(to=minRoof-20,from_=self.plotFloor,tickinterval=(minRoof-self.plotFloor)/10)

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
            ma,mi,re = self.scaleMaxValueColor.get(),self.scaleMinValueColor.get(),self.scaleRedValue.get()
            if (self.envActive.imgObj.maxColor != ma 
                or self.envActive.imgObj.minColor != mi
                or self.envActive.imgObj.redScale != re):
                def changePlotColor(self,ma,mi,re):
                    self.envActive.updateColor(re,mi,ma)
                    self.configureColorScale(ma,mi)
                self.job = self.root.after(500,changePlotColor,self,ma,mi,re)              

    def checkPlotGray(self):
        if self.job:
            self.root.after_cancel(self.job)
        if self.envActive:
            ma,mi = self.scaleMaxValueGray.get(),self.scaleMinValueGray.get()
            if (self.envActive.imgObj.maxColor != ma 
                or self.envActive.imgObj.minColor != mi):
                def changePlotGray(self,ma,mi):
                    self.envActive.updateGray(mi,ma)
                self.job = self.root.after(500,changePlotGray,self,ma,mi)              

    def setColor(self,c):
        if self.envActive:
            self.color = c

    def setNotebook(self):
        self.notebook = ttk.Notebook(self.mainFrame,name=txt.NOTEBOOK)
        self.notebook.grid(row=0,column=1,rowspan=2,sticky=tk.NSEW)
        self.root.update()
        self.notebook.bind("<<NotebookTabChanged>>", self.onEnvChange)

    def setTopMenu(self):
        #self.menubar = tk.Menu(self.root,tearoff=False)
        self.ttkMenubar = ttk.Menubutton(self.root)
        self.menubar = tk.Menu(self.root,tearoff=False)
        self.ttkMenubar['menu'] = self.menubar
        self.fileMenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label=lblsTop.FILE, underline=0, menu=self.fileMenu)
        self.fileMenu.add_command(label=lblsTop.LOADEXAMNORMAL, underline=0,  compound=tk.LEFT,command=self.loadExamNormal)
        self.fileMenu.add_command(label=lblsTop.LOADEXAMBATCH, underline=0,  compound=tk.LEFT,command=self.loadExamBatch)
        self.root.config(menu = self.menubar) 

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
        examDict = dcmHandler.openDicomFiles()
        
        for examID,dicomList in examDict.items():
                self.loader(examID,dicomList)
                # t = Thread(target=self.loader,args=(img,))
                # loaderList.append(t)
                # t.start()

    def loadExamNormal(self):
        """
        Carrega os exames através do handler
        """
        examDict = dcmHandler.openDicomFiles()
        for examID,dicomList in examDict.items():
                self.loader(examID,dicomList)
                # t = Thread(target=self.loader,args=(img,))
                # loaderList.append(t)
                # t.start()
  
    def onEnvChange(self,event):
        self.job = None
        self.envActive = self.envDict[self.notebook.index(self.notebook.select())]
        if self.envActive:
            self.scaleMaxValueColor.set(self.envActive.imgObj.maxColor)
            self.scaleMinValueColor.set(self.envActive.imgObj.minColor)
            self.scaleMaxValueGray.set(self.envActive.imgObj.maxGray)
            self.scaleMinValueGray.set(self.envActive.imgObj.minGray)
            self.scaleRedValue.set(self.envActive.imgObj.redScale)
            self.scalesMenu.grid()
            self.configureColorScale(self.envActive.imgObj.maxColor,self.envActive.imgObj.minColor)
            self.clearCursor()

    def cbRoi(self,shape):
        self.clearCursor()
        if self.envActive:
            self.envActive.resultCanvas.bind("<ButtonPress-1>", lambda event: edit.startRoi(
                env=self.envActive,event=event,shape=shape))
            self.envActive.resultCanvas.bind("<B1-Motion>", lambda event: edit.onMoveRoi(
                env=self.envActive,event=event))
            self.envActive.resultCanvas.bind("<ButtonRelease-1>", lambda event: edit.releaseRoi(
                env=self.envActive,event=event))

    def cbDraw(self):
        self.clearCursor()
        if self.envActive:
            self.drawColorsMenu.grid()
            #cnv =self.envActive.resultCanvas
            self.envActive.resultCanvas.bind("<ButtonPress-1>", lambda event: edit.startDraw(
                event=event,env=self.envActive,thickness=self.drawThickness.get(),color=self.color))
            self.envActive.resultCanvas.bind("<B1-Motion>", lambda event:edit.onMoveDraw(
                event=event,env=self.envActive,thickness=self.drawThickness.get(),color=self.color))
            self.envActive.resultCanvas.bind("<ButtonRelease-1>", lambda event: edit.releaseDraw(
                env=self.envActive,event=event))

    def cbZoom(self,zoomIn):
        self.clearCursor()
        if self.envActive:
            self.envActive.resultCanvas.bind("<ButtonRelease-1>", lambda event: edit.zoom(
                env=self.envActive,zoomIn=zoomIn,event=event))

    def cbTag(self):
        self.clearCursor()
        if self.envActive:
            self.envActive.resultCanvas.bind("<ButtonPress-1>", lambda event: edit.startTag(
                env=self.envActive,event=event))
        
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
            # cnv = self.root.nametowidget(".".join((frmName,txt.EXAMIMAGE,cnvName)))
            self.drawColorsMenu.grid_remove()
            cnv.unbind("<ButtonPress-1>")
            cnv.unbind("<B1-Motion>")
            cnv.unbind("<ButtonRelease-1>")

if __name__ == "__main__":
    main = MainForm()
