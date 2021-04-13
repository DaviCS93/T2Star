import tkinter as tk
from tkinter import ttk
from errorHandler import LOGTYPE,printLog

import editMenu as edit
from dicomHandler import dicomHandler
from environment import Environment
from shape import Shape
from enumInterface import Buttons as btns
from enumInterface import Labels as lbls
from enumInterface import Texts as txt
from enumInterface import TopMenuLabels as lblsTop
from threading import Thread
from sys import exit as closeThread
class MainForm():
    
    def __init__(self):
        self.envDict = {}
        self.loaderList = []
        self.envActive = None
        self.formStyle()
        self.root.mainloop()

    def formStyle(self):
        #root
        self.root = tk.Tk()
        self.root.rowconfigure(0,weight=1)
        self.root.columnconfigure(0,weight=1)
        self.root.state('zoomed')
    #mainFrame
        self.mainFrame = tk.Frame(self.root,bg="black")
        self.mainFrame.grid(row=0,column=0,sticky=tk.NSEW)
        self.mainFrame.rowconfigure(1,weight=1)
        self.mainFrame.columnconfigure(0,weight=1,uniform="mainframe")
        self.mainFrame.columnconfigure(1,weight=4,uniform="mainframe")
        self.mainFrame.bind(("<Escape>",self.clearCursor))
    #editMenu
        self.editMenu = tk.Frame(self.mainFrame,bg="blue")
        self.editMenu.grid(row=1,column=0,sticky=tk.NSEW)
        self.editMenu.columnconfigure(0,weight=1)
        ttk.Button(self.editMenu,text=btns.RECTANGLE,command=lambda: self.cbRoi(Shape.RECTANGLE)).grid(row=1,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.CIRCLE,command=lambda: self.cbRoi(Shape.CIRCLE)).grid(row=2,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.DRAW,command=lambda: self.cbDraw()).grid(row=3,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.ZOOM_IN,command=lambda: self.cbZoom(True)).grid(row=4,column=0,sticky=tk.NW)
        ttk.Button(self.editMenu,text=btns.ZOOM_OUT,command=lambda: self.cbZoom(False)).grid(row=5,column=0,sticky=tk.NW)
        
    #notebook
        self.notebook = ttk.Notebook(self.mainFrame,name=txt.NOTEBOOK)
        self.notebook.grid(row=1,column=1,sticky=tk.NSEW)
        self.root.update()
        self.notebook.bind("<<NotebookTabChanged>>", self.onEnvChange)
    #topMenu
        self.menubar = tk.Menu(self.root,tearoff=False)
        self.fileMenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label=lblsTop.FILE, underline=0, menu=self.fileMenu)
        self.fileMenu.add_command(label=lblsTop.LOADEXAM, underline=0,  compound=tk.LEFT,command=self.loadExam)
        self.root.config(menu = self.menubar) 
    
    def loader(self,img):
        # img.createFigure()
        img.plotFigure(False)
        self.envActive = Environment(img)
        self.loadImageNotebook(self.envActive)

    def loadExam(self):
        handler = dicomHandler()
        handler.defineListEcho()
        for img in handler.listImg:
                self.loader(img)
                # t = Thread(target=self.loader,args=(img,))
                # loaderList.append(t)
                # t.start()
  
    def onEnvChange(self,event):
        self.envActive = self.envDict[self.notebook.index('current')]
        self.clearCursor()

    def cbRoi(self,shape):
        cnv = self.envActive.resultCanvas
        cnv.bind("<ButtonPress-1>", lambda event: edit.callbackRoi(env=self.envActive,event=event,shape=shape))
        cnv.bind("<B1-Motion>", lambda event: edit.onMoveRoi(env=self.envActive,event=event))
        cnv.bind("<ButtonRelease-1>", lambda event: edit.releaseRoi(env=self.envActive,event=event))

    def cbDraw(self):
        cnv =self.envActive.resultCanvas
        cnv.bind("<ButtonPress-1>", lambda event: edit.callbackDraw(event=event))
        cnv.bind("<B1-Motion>", lambda event: edit.onMoveDraw(event=event))
        cnv.bind("<ButtonRelease-1>", lambda event: edit.releaseDraw(event=event))

    def cbZoom(self,zoom):
        cnv =self.envActive.resultCanvas
        if zoom: # Zoom in
            cnv.bind("<ButtonRelease-1>", lambda event: edit.zoomIn(env=self.envActive,event=event))
        else:
            cnv.bind("<ButtonRelease-1>", lambda event: edit.zoomOut(env=self.envActive,event=event))

    def loadImageNotebook(self,env):
        """
        Create a image in the notebook for the environment. The image is loaded in a tab in
        the notebook
        Input: Environment (env)
        Output: Frame inside the tab where the image is set (frm)
        """
        try:
            # Adicionando a aba
            frm = tk.Frame(self.notebook,bg="red",name=env.examID)
            self.notebook.add(frm,text=env.examID)
            frm.rowconfigure(0,weight=1)
            frm.columnconfigure(0,weight=2,uniform='notebook')
            frm.columnconfigure(1,weight=1,uniform='notebook')
            # Adicionando a janela do exame dentro da aba
            env.examFrame = tk.Frame(frm,bg="green",name=txt.EXAMIMAGE)
            env.examFrame.rowconfigure(0,weight=1)
            env.examFrame.columnconfigure(0,weight=1)
            env.examFrame.grid(row=0,column=0,sticky=tk.NSEW)
            # Adicionando o canvas da imagem do exame, dentro
            # da janela
            env.resultCanvas = tk.Canvas(master=env.examFrame)
            #env.resultCanvas.pack(expand=1, fill=tk.BOTH)
            env.resultCanvas.grid(row=0,column=0)
            env.updateImage()
            self.envDict[len(self.notebook.tabs())-1] = self.envActive
            self.notebook.select(len(self.notebook.tabs())-1)
        except Exception as ex:
            printLog(LOGTYPE.ERROR_LOAD_IMG_NOTEBOOK,ex)

    def clearCursor(self):
        frmName = self.notebook.select()
        frm = self.root.nametowidget(frmName)
        for cnvName in frm.children[txt.EXAMIMAGE].children:
            # Pega o canvas atual
            cnv = self.root.nametowidget(".".join((frmName,txt.EXAMIMAGE,cnvName)))
            cnv.unbind("<ButtonPress-1>")
            cnv.unbind("<B1-Motion>")
            cnv.unbind("<ButtonRelease-1>")

if __name__ == "__main__":
    main = MainForm()