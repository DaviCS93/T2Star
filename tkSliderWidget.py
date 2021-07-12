from tkinter import *
import tkinter
from PIL import Image
from tkinter.ttk import *



class Slider(Frame):
    LINE_COLOR = "#476b6b"
    LINE_WIDTH = 3
    BAR_COLOR_INNER = "#5c8a8a"
    BAR_COLOR_OUTTER = "#c2d6d6"
    BAR_RADIUS = 10
    BAR_RADIUS_INNER = BAR_RADIUS-5
    DIGIT_PRECISION = '.0f' # for showing in the canvas
    def __init__(self, master, width = 80, height = 1000, min_val = 0, max_val = 1, init_lis = None):
        Frame.__init__(self, master, height = height, width = width)
        self.master = master
        if init_lis == None:
            init_lis = [min_val]
        self.init_lis = init_lis
        self.max_val = max_val
        self.min_val = min_val
        self.H = height
        self.W = width
        self.canv_H = self.H
        self.canv_W = self.W
        self.slider_x = self.canv_W*2/5
        self.slider_y = Slider.BAR_RADIUS # x pos of the slider (left side)

        self.bars = []
        self.selected_idy = None # current selection bar index
        for value in self.init_lis:
            pos = (value-min_val)/(max_val-min_val)
            ids = []
            bar = {"Pos":pos, "Ids":ids, "Value":value}
            self.bars.append(bar)


        self.canv = Canvas(self, height = self.canv_H, width = self.canv_W)
        self.canv.pack()
        self.canv.bind("<Motion>", self._mouseMotion)
        self.canv.bind("<B1-Motion>", self._moveBar)

        self.__addTrack(self.slider_x, self.slider_y, self.canv_W-self.slider_x, self.slider_y)
        for bar in self.bars:
            bar["Ids"] = self.__addBar(bar["Pos"])

    def setBackground(self,printImage):
        colorImage  = Image.open(printImage)
        transposed  = colorImage.transpose(Image.ROTATE_90)
        self.saveImage = transposed
        self.canv.create_image(0,0,anchor="NW",image=transposed,tags='transposed')
        self.canv.configure(width=self.canv_W,height=self.canv_H)

    def getValues(self):
        values = [bar["Value"] for bar in self.bars]
        return sorted(values)

    def _mouseMotion(self, event):
        x = event.x; y = event.y
        selection = self.__checkSelection(x,y)
        if selection[0]:
            self.canv.config(cursor = "hand2")
            self.selected_idy = selection[1]
        else:
            self.canv.config(cursor = "")
            self.selected_idy = None

    def _moveBar(self, event):
        x = event.x; y = event.y
        if self.selected_idy == None:
            return False
        pos = self.__calcPos(x)
        idy = self.selected_idy
        self.__moveBar(idy,pos)

    def __addTrack(self, startx, starty, endx, endy):
        id1 = self.canv.create_line(startx, starty, endx, endy, fill = Slider.LINE_COLOR, width = Slider.LINE_WIDTH)
        return id

    def __addBar(self, pos):
        """@ pos: position of the bar, ranged from (0,1)"""
        if pos <0 or pos >1:
            raise Exception("Pos error - Pos: "+str(pos))
        R = Slider.BAR_RADIUS
        r = Slider.BAR_RADIUS_INNER
        L = self.canv_W - 2*self.slider_x
        x = self.slider_x
        y = self.slider_y+pos*L
        id_outer = self.canv.create_oval(x-R,y-R,x+R,y+R, fill = Slider.BAR_COLOR_OUTTER, width = 2, outline = "")
        id_inner = self.canv.create_oval(x-r,y-r,x+r,y+r, fill = Slider.BAR_COLOR_INNER, outline = "")
        x_value = x+Slider.BAR_RADIUS+8
        value = pos*(self.max_val - self.min_val)+self.min_val
        id_value = self.canv.create_text(x_value,y, text = format(value, Slider.DIGIT_PRECISION))
        return [id_outer, id_inner, id_value]

    def __moveBar(self, idy, pos):
        ids = self.bars[idy]["Ids"]
        for id in ids:
            self.canv.delete(id)
        self.bars[idy]["Ids"] = self.__addBar(pos)
        self.bars[idy]["Pos"] = pos
        self.bars[idy]["Value"] = pos*(self.max_val - self.min_val)+self.min_val

    def __calcPos(self, y):
        """calculate position from x coordinate"""
        pos = (y - self.slider_y)/(self.canv_H-2*self.slider_y)
        if pos<0:
            return 0
        elif pos>1:
            return 1
        else:
            return pos

    def __getValue(self, idy):
        """#######Not used function#####"""
        bar = self.bars[idy]
        ids = bar["Ids"]
        y = self.canv.coords(ids[0])[0] + Slider.BAR_RADIUS
        pos = self.__calcPos(y)
        return pos*(self.max_val - self.min_val)+self.min_val

    def __checkSelection(self, x, y):
        """
        To check if the position is inside the bounding rectangle of a Bar
        Return [True, bar_index] or [False, None]
        """
        for idy in range(len(self.bars)):
            id = self.bars[idy]["Ids"][0]
            bbox = self.canv.bbox(id)
            if bbox[0] < y and bbox[2] > y and bbox[1] < y and bbox[3] > x:
                return [True, idy]
        return [False, None]

root = tkinter.Tk()

slider = Slider(root, min_val = -100, max_val = 100, init_lis = [-50,0,75])
slider.pack()
root.title("Slider Widget")
root.mainloop()

print(slider.getValues())