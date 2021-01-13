import time
import math
import os

import matplotlib.pyplot as plt
import matplotlib as matplot
import pydicom as pd
import numpy as np
from mpl_toolkits.axes_grid1 import Divider, Size
from mpl_toolkits.axes_grid1.mpl_axes import Axes
from matplotlib.colors import ListedColormap
from scipy.signal import medfilt2d


class imgObject():
    """
    docstring
    """
     
    def __init__(self,listDicom):
        self.imgMatrix = None
        self.maxColor = 180
        self.minColor = 0
        self.listROI = []
        self.listEchoTime = []
        self.color = self.defineJet()
        self.figure = plt.figure(figsize=(6, 6),frameon=False)
        self.listDicom = listDicom
        for ds in listDicom:
            self.listEchoTime.append(ds.EchoTime/1000) 
        
    def defineJet(self):
        """
        docstring
        """
        jet = matplot.cm.get_cmap(name='jet')
        jet_arr = jet(np.linspace(0, 1, 128))
        jet_reverse = matplot.cm.get_cmap(name='jet_r')
        jet_reverse_arr = jet_reverse(np.linspace(0, 1, 128))
        jet_combined_arr = np.concatenate((jet_arr,jet_reverse_arr))
        jet_combined = ListedColormap(jet_combined_arr)
        return jet_combined

    def createFigure(self):
        """
        docstring
        """
        image_mean = []   
        analysis = []

        #We start seting the timer to verify performance
        tic = time.perf_counter()

        #For each dicom, we need to take the image mean, so
        #we can remove noise (salt and pepper noise?)
        for ds in self.listDicom:
            image_mean.append(medfilt2d(
                np.array(ds.pixel_array,dtype=np.float),
                kernel_size=3))

        #Then we define what will be the main matrix for the process (self.imgMatrix)
        #based on the size of the image (they will be the same)
        self.imgMatrix = np.zeros((len(image_mean[0]),len(image_mean[0][0]))) 
        self.imgMatrix = np.reshape(self.imgMatrix,(
            len(image_mean[0])*len(image_mean[0][0]),1)) #

        #We reset all values under 30.
        image_mean[0][image_mean[0]<30] = 0 #

        #We create a vector to be easier to process
        for index in range(len(self.listDicom)): 
            analysis.append(np.reshape(image_mean[index],(
                len(image_mean[0])*len(image_mean[0][0]),1))) 

        #Set the first item as fixed, and them compare all 
        #remain itens to get true/false 
        tempArr = analysis[0] 
        for aux in analysis[1:]:
            tempArr = np.logical_and(tempArr,aux)

        #Process the TE to get the values needed for the process later
        echoTimeSum = -sum(self.listEchoTime) 
        echoTimeArr = np.array(self.listEchoTime) 
        echoTimeMul = np.matmul(np.transpose(echoTimeArr),echoTimeArr) 

        #Get all indexes which result are 1 (over 0 in all pixels)
        indexes = [ind for ind, x in enumerate(tempArr) if x>0] 

        #Main process, now all the 
        for index,indexValue in enumerate(indexes):
            validArr = np.empty((0,len(analysis[0][0])))  

            for i in range(len(self.listDicom)):
                validArr = np.append(validArr,analysis[i][indexValue])

            #Get the log for each value, sum and matrix multiply by the echo time 
            validArrLog = np.array(list(map(np.log,validArr)))
            validArrSum = sum(validArrLog)
            validArrLogEchoTime = np.matmul(-np.transpose(echoTimeArr),validArrLog)

            #TODO understand this, i have no idea
            A = np.array([[len(self.listDicom), echoTimeSum],[echoTimeSum, echoTimeMul]])  
            B = np.array([[validArrSum],[validArrLogEchoTime]])  
            invA =np.linalg.inv(A) 
            P = np.matmul(invA,B)
            
            #Anyway, get the result for the matrix in the result array
            self.imgMatrix[indexValue] = (P[1][0])

        for i,t in enumerate(self.imgMatrix):
            self.imgMatrix[i] = math.inf if t[0] == 0 else 1000/t[0]

        #Reshape T2 for the size needed
        self.imgMatrix = np.reshape(self.imgMatrix,(400,400))
        toc = time.perf_counter()
        print(f"Executed in {toc - tic:0.4f} seconds")

    def plotFigure(self,plot):
        colorName = '{0}\imgs\color{1}.png'.format(os.path.dirname(__file__),self.listDicom[0].StudyID)
        grayName = '{0}\imgs\gray{1}.png'.format(os.path.dirname(__file__),self.listDicom[0].StudyID)
        self.exportFigure(colorName,cmap=self.color, vmin=self.minColor, vmax=self.maxColor, plt_show=False)
        self.exportFigure(grayName,cmap=matplot.cm.get_cmap('gray_r'), plt_show=False)
        
    #     ax = plt.Axes(fig, [0., 0., 1., 1.])
    #     ax.set_axis_off()
    #     # self.figure.add_axes(ax)
    #     # fig.savefig('figure.png', dpi=1)
        
    #     # plt.axis('off')
    #     ax.imshow(self.imgMatrix,cmap=matplot.cm.get_cmap('gray_r'))
    #     grayName = '{0}\imgs\gray{1}.png'.format(os.path.dirname(__file__),self.listDicom[0].StudyID)
    #     self.figure.savefig(grayName,bbox_inches='tight')

    #     plt.clf()
    #     ax = plt.Axes(fig, [0., 0., 1., 1.])
    #     ax.set_axis_off()

    #     # plt.axis('off')
    #     ax.imshow(self.imgMatrix, cmap=self.color, vmin=self.minColor, vmax=self.maxColor)
    #     colorName = '{0}\imgs\color{1}.png'.format(os.path.dirname(__file__),self.listDicom[0].StudyID)
    #     self.figure.savefig(colorName,bbox_inches='tight')
        
        if plot:
            plt.show()
    
    def setMaxColor(self,value):
        """
        docstring
        """
        self.maxColor = value

    def setMinColor(self,value):
        """
        docstring
        """
        self.minColor = value

    def saveImg(self):
        """
        docstring
        """
    def exportFigure(self, f_name, cmap, dpi=200, resize_fact=1, plt_show=False, vmin=None, vmax=None):
        """
        Export array as figure in original resolution
        :param arr: array of image to save in original resolution
        :param f_name: name of file where to save figure
        :param resize_fact: resize facter wrt shape of arr, in (0, np.infty)
        :param dpi: dpi of your screen
        :param plt_show: show plot or not
        """
        fig = plt.figure(frameon=False)
        fig.set_size_inches(self.imgMatrix.shape[1]/dpi, self.imgMatrix.shape[0]/dpi)
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        ax.imshow(self.imgMatrix,cmap=cmap, vmin=vmin, vmax=vmax)
        plt.savefig(f_name, dpi=(dpi * resize_fact))
        if plt_show:
            plt.show()
        else:
            plt.close()   



        # h = [Size.Fixed(1.0), Size.Fixed(5.)]
        # v = [Size.Fixed(1.0), Size.Fixed(5.)]
        # divider = Divider(self.figure, (0.0, 0.0, 1., 1.), h, v, aspect=False)
        
        # ax = Axes(self.figure, divider.get_position())
        # ax.set_axes_locator(divider.new_locator(nx=1, ny=1))
        # self.figure.add_axes(ax)