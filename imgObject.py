import warnings 
import os
import json
from scipy.signal.ltisys import impulse2
from decorators import timer
import matplotlib.pyplot as plt
import matplotlib as matplot
import numpy as np
import cv2
from matplotlib.colors import ListedColormap
from scipy.signal import medfilt2d
from PIL import Image
from shape import Shape
from canvasElements import ROI,DrawnLines
from math import inf

class imgObject():
    """
    docstring
    """
     
    def __init__(self,dicomList):
        self.imgMatrix = None
        self.imgMSE = None
        self.maxColor = 200
        self.minColor = 40
        self.maxGray = 200
        self.minGray = 0
        self.redScale = 50
        self.listROI = []
        self.listEchoTime = []
        self.color = self.defineJet()
        self.gray = self.defineGray()
        self.figure = plt.figure(figsize=(6, 6),frameon=False)
        self.dicomList = dicomList
        self.grayName = ""
        self.cannyName = ""
        self.colorName = ""
        self.imgEcho = None
        self.imgStar = None
        self.imgCanny = None
        self.resultImage = None
        self.size = dicomList[0].pixel_array.shape
        # Zoom ativo
        self.activeZoom = 1
        for ds in dicomList:
            self.listEchoTime.append(ds.EchoTime/1000) 
        # Cria as imagens no que é carregado os arquivos
        self.createFigure()
        self.plotFigure()

    @timer    
    def defineGray(self):
        """
        docstring
        """
        gray = matplot.cm.get_cmap(name='gray')
        gradient = np.linspace(0, 1, 180)
        gradient = np.vstack((gradient, gradient))
        fig, ax = plt.subplots(nrows=1, figsize=(10, 1))
        ax.imshow(gradient, aspect='auto', cmap=gray)
        ax.set_axis_off()
        plt.savefig(f"{os.path.dirname(__file__)}\\imgs\\scalegray.png",bbox_inches = 'tight', dpi=200)
        plt.close()
        return gray
        
    @timer    
    def defineJet(self):
        """
        docstring
        """
        redScale=self.redScale/100
        jet = matplot.cm.get_cmap(name='jet')
        jet_arr = jet(np.linspace(0, 1,128))
        jet_reverse = matplot.cm.get_cmap(name='jet_r')
        jet_reverse_arr = jet_reverse(np.linspace(0, 1, 128))
        if redScale >0.5:
            jet_reverse_arr=jet_reverse_arr[1:-1-(int((redScale-0.5)*256)),:] #deletar slice (redScale-0.5)*256
        elif redScale <0.5:
            jet_arr=jet_arr[(int((redScale*(-256)+128))):len(jet_arr),:] #deletar slice redScale*256
        jet_combined_arr = np.concatenate((jet_arr,jet_reverse_arr))
        jet_combined = ListedColormap(jet_combined_arr)
        gradient = np.linspace(0, 1, 180)
        gradient = np.vstack((gradient, gradient))
        fig, ax = plt.subplots(nrows=1, figsize=(10, 1))
        ax.imshow(gradient, aspect='auto', cmap=jet_combined)
        ax.set_axis_off()
        plt.savefig(f"{os.path.dirname(__file__)}\\imgs\\scale.png",bbox_inches = 'tight', dpi=200)
        plt.close()
        return jet_combined
        
    @timer 
    def createFigure(self):
        """
        docstring
        """
        #self.imageMean = []   
        self.imageMean = np.zeros((*self.size,len(self.dicomList)))
        #analysis = []
        analysis = np.zeros((*self.size,len(self.dicomList)))
        
        warnings.filterwarnings('ignore')
        # Process the TE to get the values needed for the process later
        echoTimeSum = -sum(self.listEchoTime) 
        self.echoTimeArr = np.array(self.listEchoTime) 
        echoTimeMul = np.matmul(np.transpose(self.echoTimeArr),self.echoTimeArr) 

        # For each dicom, we need to take the image mean, so
        # we can remove noise (salt and pe-pper noise?)
        for index in range(len(self.dicomList)):
            a = medfilt2d(
                np.array(self.dicomList[index].pixel_array,dtype=np.float),
                kernel_size=3)
            self.imageMean[:,:,index] = a

        # Then we define what will be the main matrix for the process (self.imgMatrix)
        # based on the size of the image (they will be the same)
        self.imgMatrix = np.zeros(self.size) 
        self.imgMatrix = np.reshape(self.imgMatrix,(
            self.size[0]*self.size[1],1)) #

        # We reset all values under 30.
        self.imageMean[self.imageMean<30] = 0 #

        # We create a vector to be easier to process
        analysis = np.reshape(self.imageMean,
            (self.size[0]*self.size[1],len(self.dicomList)))

        matLog = np.log(analysis)
        matLog[matLog == -inf] = 0
        arrSum = matLog.sum(axis=1)
        arrLogEchoTime = np.matmul(matLog,-self.echoTimeArr)

        arrB = np.stack((arrSum,arrLogEchoTime))
        A = np.array([[len(self.dicomList), echoTimeSum],[echoTimeSum, echoTimeMul]])  
        invA = np.linalg.inv(A)
        #P = np.apply_along_axis(lambda x:np.matmul(invA,x),0,arrB)
        P = np.matmul(invA,arrB)
        

        self.imgMatrix = np.transpose(P)[:,[1]]
        self.imgMatrix = np.reshape(self.imgMatrix,self.size)
        self.imgMatrix = 1000/self.imgMatrix
        self.imgMatrix[np.isnan(self.imgMatrix)] = inf
        self.imgMatrix[self.imgMatrix == inf] = 255
        self.imgMatrix[self.imgMatrix > 255] = 255
        self.imgMatrix[self.imgMatrix < 0] = 0
        # Reshape T2 for the size needed
        self.s0 = np.reshape(np.transpose(P)[:,[0]],self.size)
        ex = np.exp(-np.reshape(self.echoTimeArr,(self.echoTimeArr.shape[0],1)))
        yTemp = np.matmul(self.imgMatrix,np.exp(self.s0)) #S0(i)*exp(-TE(1:end).*R2(ind(i),1));  
        yTemp = np.reshape(yTemp,(self.size[0]*self.size[1],1))
        yPred = np.matmul(yTemp,np.transpose(ex))
        sse = np.sqrt(analysis-yPred).sum(axis=1)
        self.imgMSE = sse/len(self.dicomList)
        self.imgMSE = np.reshape(self.imgMSE,self.size)
    
    @timer 
    def plotFigure(self):
        # Deletar imagens da pasta antes
        if os.path.isfile(self.colorName):
            map(os.remove,(self.colorName,self.grayName))
        self.colorName = f'{os.path.dirname(__file__)}\\imgs\\color{self.dicomList[0].StudyID}.png'
        self.grayName = f'{os.path.dirname(__file__)}\\imgs\\gray{self.dicomList[0].StudyID}.png'
        #self.exportFigure(self.dicomList[0].pixel_array,self.grayName,cmap=matplot.cm.get_cmap('gray_r'), plt_show=False)
        imgTemp = np.copy(self.imgMatrix)
        imgTemp[imgTemp>self.maxGray] = self.maxGray
        imgTemp[imgTemp<self.minGray] = self.minGray
        self.exportFigure(imgTemp,self.grayName,cmap=self.gray, plt_show=False)
        self.exportFigure(self.imgMatrix, self.colorName,cmap=self.color, vmin=self.minColor, vmax=self.maxColor, plt_show=False)
        # self.imgCanny = cv2.Canny(imgTemp,40,150)
        # self.cannyName = f'{os.path.dirname(__file__)}\\imgs\\canny{self.dicomList[0].StudyID}.png'
        # self.exportFigure(self.imgCanny,self.cannyName,cmap=matplot.cm.get_cmap('gray_r'), plt_show=False)
        self.imgEcho = Image.open(self.grayName)
        self.imgStar = Image.open(self.colorName)
        # self.imgCanny = Image.open(self.cannyName)
        self.resultImage = self.removeTransparency(self.imgEcho)
        # self.resultImage = self.imgCanny
        pass

    @timer 
    def removeTransparency(self,im):
        if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
            alpha = im.convert('RGBA').split()[-1]
            bg = Image.new("RGBA", im.size, (255, 255, 255) + (255,))
            bg.paste(im, mask=alpha)
            return bg
        else:
            return im
    
    @timer 
    def setColors(self,max,min,red):
        """
        docstring
        """
        self.maxColor = max
        self.minColor = min
        self.redScale = red
        self.color = self.defineJet()

    @timer 
    def setGray(self,max,min):
        """
        docstring
        """
        self.maxGray = max
        self.minGray = min
        #self.gray = self.defineGray()

    @timer 
    def exportFigure(self, matrix, f_name, cmap, dpi=200, resize_fact=1, plt_show=False, vmin=None, vmax=None):
        """
        Export array as figure in original resolution
        :param arr: array of image to save in original resolution
        :param f_name: name of file where to save figure
        :param resize_fact: resize facter wrt shape of arr, in (0, np.infty)
        :param dpi: dpi of your screen
        :param plt_show: show plot or not
        """
        fig = plt.figure(frameon=False)
        fig.set_size_inches(map(lambda x: x/dpi,self.imgMatrix.shape))
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_facecolor('navy')
        ax.set_axis_off()
        fig.add_axes(ax)
        ax.imshow(matrix,cmap=cmap, vmin=vmin, vmax=vmax)
        plt.savefig(f_name, dpi=(dpi * resize_fact))
        if plt_show:
            plt.show()
        else:
            plt.close()   

    @timer 
    def replaceRoi(self,roiList):
        cvEcho = cv2.imread(self.grayName) # pylint: disable=maybe-no-member
        cvStar = cv2.imread(self.colorName) # pylint: disable=maybe-no-member
        #alpha = cvEcho[:,:,3]
        for roi in roiList:
            if not type(roi) == ROI:
                continue
            mask = np.zeros(self.size, np.uint8)
            if roi.shape == Shape.RECTANGLE:
                mask = cv2.rectangle(mask,roi.start,roi.end,(255, 255, 255), -1) # pylint: disable=maybe-no-member
            elif roi.shape == Shape.CIRCLE:
                #Para o circulo precisamos do centro e do raio
                #Então temos que fazer alguns calculos
                #Para o centro fazemos o canto menos o outro para conseguir o lado
                #Então, dividimos por 2 para ter o centro e somamos o 1 canto
                #para ter o centro do lado em relação ao zero do Roi
                circleCenter = (int(roi.x1+((roi.x2-roi.x1)/2)),int(roi.y1+((roi.y2-roi.y1)/2)))
                #Para o raio, é só usar a mesma logica do centro
                #Só que sem somar o zero do Roi
                radius = abs(int((roi.x2-roi.x1)/2))
                mask = cv2.circle(mask,circleCenter,radius,(255, 255, 255), cv2.FILLED) # pylint: disable=maybe-no-member
            mask_inv = cv2.bitwise_not(mask) # pylint: disable=maybe-no-member
            imgEcho_bg = cv2.bitwise_or(cvEcho, cvEcho, mask = mask_inv) # pylint: disable=maybe-no-member
            imgStar_fg = cv2.bitwise_or(cvStar, cvStar, mask = mask) # pylint: disable=maybe-no-member
            cvEcho = cv2.add(imgEcho_bg,imgStar_fg) # pylint: disable=maybe-no-member
            if not roi.definedInfo: 
                roi.mean,roi.std = cv2.meanStdDev(self.imgMatrix,mask=mask)
                roi.mean,roi.std = round(roi.mean[0][0], 2),round(roi.std[0][0], 2)
                roi.min,roi.max,_,_  = cv2.minMaxLoc(self.imgMatrix,mask)
                roi.area =cv2.countNonZero(mask)
                roi.pix = f'{round(100*roi.area/self.imgMatrix.size,2)}%'

                self.listEchoTime
                analysis = np.ndarray((0,))
                for i in range(len(self.dicomList)):
                    mean = cv2.meanStdDev(self.imageMean[:,:,i],mask=mask)
                    analysis = np.concatenate((analysis,mean[0][0]))
                
                matLog = np.log(analysis)
                arrSum = matLog.sum(axis=0)
                arrLogEchoTime = np.matmul(matLog,-self.echoTimeArr)
                
                echoTimeSum = -sum(self.listEchoTime) 
                self.echoTimeArr = np.array(self.listEchoTime) 
                roi.time = np.arange(self.listEchoTime[0]*1000,self.listEchoTime[-1]*1000,1)
                echoTimeMul = np.matmul(np.transpose(self.echoTimeArr),self.echoTimeArr) 
                arrB = np.stack((arrSum,arrLogEchoTime))
                A = np.array([[len(self.dicomList), echoTimeSum],[echoTimeSum, echoTimeMul]])  
                invA = np.linalg.inv(A)
                P = np.matmul(invA,arrB)
                roi.decay = np.exp(P[0])*np.exp(-roi.time*(P[1]/1000))

                plt.plot(roi.time,roi.decay,c='red')
                plt.scatter(self.echoTimeArr*1000,analysis,s=10)
                fig = plt.gcf()
                fig.set_size_inches(9, 7)
                roi.decayImgFile = f"{os.path.dirname(__file__)}\\imgs\\decay-roi{roi.elmId}.png"
                plt.savefig(roi.decayImgFile, dpi=100 ,bbox_inches = 'tight',pad_inches = 0.1,transparent=True)
                plt.close()
                roi.definedInfo = True
        
                self.resultImage = Image.fromarray(cvEcho)  