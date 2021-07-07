import tkinter as tk
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
        self.envActive = None
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
        self.mainFrame.rowconfigure(1,weight=1)
        self.mainFrame.columnconfigure(0,weight=1,uniform="mainframe")
        self.mainFrame.columnconfigure(1,weight=4,uniform="mainframe")
        self.mainFrame.bind(("<Escape>",self.clearCursor))

    def setEditMenu(self):
        self.drawThickness = tk.DoubleVar(self.root)
        self.color = 'black'
        self.editMenu = ttk.Frame(self.mainFrame)
        self.editMenu.grid(row=1,column=0,sticky=tk.NSEW)
        #self.editMenu.columnconfigure(0,weight=1)
        ttk.Button(self.editMenu,text=btns.RECTANGLE,command=lambda: self.cbRoi(Shape.RECTANGLE)).grid(row=1,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.CIRCLE,command=lambda: self.cbRoi(Shape.CIRCLE)).grid(row=2,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.DRAW,command=lambda: self.cbDraw()).grid(row=3,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.TAG,command=lambda: self.cbTag()).grid(row=4,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.ZOOM_IN,command=lambda: self.cbZoom(True)).grid(row=5,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.ZOOM_OUT,command=lambda: self.cbZoom(False)).grid(row=6,column=0,sticky=tk.NW)
        ttk.Scale(self.editMenu,orient=tk.HORIZONTAL,variable=self.drawThickness).grid(row=3,column=1,sticky=tk.NW)
        self.drawColorsMenu = ttk.Frame(self.editMenu)
        self.drawColorsMenu.grid(row=7,column=1,sticky=tk.NW)
        tk.Button(self.drawColorsMenu,bg=btns.BLUE,command=lambda: self.setColor('blue')).grid(row=6,column=0,sticky=tk.NW)
        tk.Button(self.drawColorsMenu,bg=btns.RED,command=lambda: self.setColor('red')).grid(row=6,column=1,sticky=tk.NW)
        tk.Button(self.drawColorsMenu,bg=btns.YELLOW,command=lambda: self.setColor('yellow')).grid(row=6,column=2,sticky=tk.NW)
        tk.Button(self.drawColorsMenu,bg=btns.GREEN,command=lambda: self.setColor('green')).grid(row=6,column=3,sticky=tk.NW)
        tk.Button(self.drawColorsMenu,bg=btns.BLACK,command=lambda: self.setColor('black')).grid(row=6,column=4,sticky=tk.NW)
        self.drawColorsMenu.grid_remove()

    def setColor(self,c):
        self.color = c

    def setNotebook(self):
        self.notebook = ttk.Notebook(self.mainFrame,name=txt.NOTEBOOK)
        self.notebook.grid(row=1,column=1,sticky=tk.NSEW)
        self.root.update()
        self.notebook.bind("<<NotebookTabChanged>>", self.onEnvChange)

    def setTopMenu(self):
        #self.menubar = tk.Menu(self.root,tearoff=False)
        self.ttkMenubar = ttk.Menubutton(self.root)
        self.menubar = tk.Menu(self.root,tearoff=False)
        self.ttkMenubar['menu'] = self.menubar
        self.fileMenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label=lblsTop.FILE, underline=0, menu=self.fileMenu)
        self.fileMenu.add_command(label=lblsTop.LOADEXAM, underline=0,  compound=tk.LEFT,command=self.loadExam)
        self.root.config(menu = self.menubar) 

    def loader(self,examID,dicomList):
        """
        Alvo da thread para criação de novos ambientes (abas)
        """
        self.envActive = Environment(examID,dicomList)
        self.loadImageNotebook()

    def loadExam(self):
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
        #print(self.notebook.index('current'))
        self.envActive = self.envDict[self.notebook.index(self.notebook.select())]
        self.clearCursor()

    def cbRoi(self,shape):
        self.clearCursor()
        #cnv = self.envActive.resultCanvas
        self.envActive.resultCanvas.bind("<ButtonPress-1>", lambda event: edit.startRoi(
            env=self.envActive,event=event,shape=shape))
        self.envActive.resultCanvas.bind("<B1-Motion>", lambda event: edit.onMoveRoi(
            env=self.envActive,event=event))
        self.envActive.resultCanvas.bind("<ButtonRelease-1>", lambda event: edit.releaseRoi(
            env=self.envActive,event=event))

    def cbDraw(self):
        self.clearCursor()
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
        #cnv =self.envActive.resultCanvas
        self.envActive.resultCanvas.bind("<ButtonRelease-1>", lambda event: edit.zoom(
            env=self.envActive,zoomIn=zoomIn,event=event))

    def cbTag(self):
        self.clearCursor()
        #cnv =self.envActive.resultCanvas
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
        frm.columnconfigure(0,weight=2,uniform='notebook')
        frm.columnconfigure(1,weight=1,uniform='notebook')
        return frm

    def clearCursor(self):
        frmName = self.notebook.select()
        frm = self.root.nametowidget(frmName)
        for cnvName in frm.children[txt.EXAMIMAGE].children:
            # Pega o canvas atual
            cnv = self.root.nametowidget(".".join((frmName,txt.EXAMIMAGE,cnvName)))
            self.drawColorsMenu.grid_remove()
            cnv.unbind("<ButtonPress-1>")
            cnv.unbind("<B1-Motion>")
            cnv.unbind("<ButtonRelease-1>")

if __name__ == "__main__":
    main = MainForm()
