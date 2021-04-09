import tkinter as tk
from tkinter import ttk
from errorHandler import LOGTYPE,printLog
import editMenu as edit
from imgHandler import ImgHandler
from environment import Environment,ROI

class MainForm():
    
    def __init__(self):
        self.envList = []
        self.formStyle()
        self.startForm()

    def formStyle(self):
        #root
        self.root = tk.Tk()
        self.root.rowconfigure(0,weight=1)
        self.root.columnconfigure(0,weight=1)

        self.root.geometry('1000x500')

        v1 = tk.StringVar()
        v2 = tk.StringVar()
        v3 = tk.StringVar()

        v1.set("mainFrame")
        v2.set("editMenu")
        v3.set("notebook")

    #mainFrame
        self.mainFrame = tk.Frame(self.root)
        self.mainFrame.grid(row=0,column=0,sticky=tk.NW)
        self.mainFrame.rowconfigure(0,weight=1)
        self.mainFrame.columnconfigure(0,weight=1)
        self.mainFrame.columnconfigure(1,weight=1)
        self.mainFrame.columnconfigure(2,weight=1)
        self.mainFrame.bind(("<Escape>",self.clearCursor))
        self.l1 = tk.Label(self.mainFrame,textvariable=v1, relief=tk.RAISED)
        self.l1.grid(row=0,column=0,sticky=tk.NW)

    #editMenu
        self.editMenu = tk.Frame(self.mainFrame)
        self.editMenu.grid(row=1,column=0,sticky=tk.NW)
        self.editMenu.columnconfigure(0,weight=1)

        self.l2 = tk.Label(self.editMenu,textvariable=v2, relief=tk.RAISED)
        self.l2.grid(row=0,column=0,sticky=tk.NW)
        self.btnRectangle = ttk.Button(self.editMenu,text="RECTANGLE",command=self.cbRectangle)
        self.btnRectangle.grid(row=1,column=0,sticky=tk.NW)

    #notebook
        self.notebook = ttk.Notebook(self.mainFrame)
        self.notebook.grid(row=1,column=1,sticky=tk.NW,columnspan=2)
        test = tk.Frame(self.notebook)
        self.notebook.add(test)
        self.notebook.bind("<<NotebookTabChanged>>", self.onEnvChange)
        self.l3 = tk.Label(test,textvariable=v3, relief=tk.RAISED)
        self.l3.grid()

    #topMenu
        self.menubar = tk.Menu(self.root,tearoff=False)
        
        self.fileMenu = tk.Menu(self.menubar, tearoff=False)

        self.menubar.add_cascade(label='Read', underline=0, menu=self.fileMenu)
        self.fileMenu.add_command(label='Load exam', underline=0,  compound=tk.LEFT,command=self.loadExam)
        self.fileMenu.add_command(label='Last Page', underline=1, compound=tk.LEFT,command=self.dummy)
        self.fileMenu.add_command(label='Next Page', underline=0, compound=tk.LEFT,command=self.dummy)
        self.fileMenu.add_command(label='Previous Page', underline=0,compound=tk.LEFT,command=self.dummy)
        self.root.config(menu = self.menubar) 
    
    def loadExam(self):
        handler = ImgHandler()
        handler.defineListEcho()
        for img in handler.listImg:
                img.createFigure()
                img.plotFigure(False)
                self.envList.append(Environment(self,img))
                

    def dummy(self):
        pass

    def onEnvChange(self,event):
        pass

    def startForm(self):
        self.root.mainloop()

    def cbRectangle(self):
        frmName = self.notebook.select()
        frm = self.root.nametowidget(frmName)
        cnv = frm.children['!canvas']
        cnv.bind("<ButtonPress-1>", lambda event: edit.callbackRectangle(env=self.envList[0],event=event))
        cnv.bind("<B1-Motion>", lambda event: edit.onMove(env=self.envList[0],event=event))
        cnv.bind("<ButtonRelease-1>", lambda event: edit.release(env=self.envList[0],event=event))


    def loadImageNotebook(self,env):
        """
        Create a image in the notebook for the environment. The image is loaded in a tab in
        the notebook
        Input: Environment (env)
        Output: Frame inside the tab where the image is set (frm)
        """
        try:
            frm = tk.Frame(self.notebook)
            frm.children
            self.notebook.add(frm)
            env.resultCanvas = tk.Canvas(master=frm,confine=True)
            env.resultCanvas.grid()
            #2,2 é uma particularidade do tkinter para criação de imagens no canvas
            print("echo")
            print(env.imgObj.imgEcho.height(), env.imgObj.imgEcho.width())
            print("color")
            print(env.imgObj.imgStar.height(), env.imgObj.imgStar.width())
            env.resultCanvas.configure(height = env.imgObj.size[0], width = env.imgObj.size[1]) 
            env.resultCanvas.create_image(2,2,anchor=tk.NW,image=env.imgObj.imgEcho)
            env.resultCanvas.update()
            return frm
        except Exception as ex:
            printLog(LOGTYPE.ERROR_LOAD_IMG_NOTEBOOK,ex)

    def clearCursor(self):
        frm = self.notebook.select()
        for cnv in frm.children:
            cnv.unbind("<ButtonPress-1>")
            cnv.bind("<B1-Motion>")
            cnv.bind("<ButtonRelease-1>")

if __name__ == "__main__":
    main = MainForm()