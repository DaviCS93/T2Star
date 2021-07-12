import warnings 
import os
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

class imgObject():
    """
    docstring
    """
     
    def __init__(self,dicomList):
        self.imgMatrix = None
        self.maxColor = 200
        self.minColor = 40
        self.redScale = 50
        self.listROI = []
        self.listEchoTime = []
        self.color = self.defineJet()
        self.figure = plt.figure(figsize=(6, 6),frameon=False)
        self.dicomList = dicomList
        self.colorName = ""
        self.grayName = ""
        self.imgEcho = None
        self.imgStar = None
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
            0 > 128
            0.5 > 0
            
            jet_arr=jet_arr[(int((redScale*(-256)+128))):len(jet_arr),:] #deletar slice redScale*256
        jet_combined_arr = np.concatenate((jet_arr,jet_reverse_arr))
        jet_combined = ListedColormap(jet_combined_arr)
        gradient = np.linspace(0, 1, 180)
        gradient = np.vstack((gradient, gradient))
        fig, ax = plt.subplots(nrows=1, figsize=(10, 1))
        ax.imshow(gradient, aspect='auto', cmap=jet_combined)
        ax.set_axis_off()
        plt.savefig(f"{os.path.dirname(__file__)}\\imgs\\scale.png",bbox_inches = 'tight', dpi=200)
        return jet_combined
        
    @timer 
    def createFigure(self):
        """
        docstring
        """
        image_mean = []   
        #analysis = []
        analysis = np.zeros((self.size[0]*self.size[1],len(self.dicomList)))
        
        warnings.filterwarnings('ignore')
        # Process the TE to get the values needed for the process later
        echoTimeSum = -sum(self.listEchoTime) 
        self.echoTimeArr = np.array(self.listEchoTime) 
        echoTimeMul = np.matmul(np.transpose(self.echoTimeArr),self.echoTimeArr) 

        # For each dicom, we need to take the image mean, so
        # we can remove noise (salt and pepper noise?)
        for ds in self.dicomList:
            image_mean.append(medfilt2d(
                np.array(ds.pixel_array,dtype=np.float),
                kernel_size=3))

        # Then we define what will be the main matrix for the process (self.imgMatrix)
        # based on the size of the image (they will be the same)
        self.imgMatrix = np.zeros((len(image_mean[0]),len(image_mean[0][0]))) 
        self.imgMatrix = np.reshape(self.imgMatrix,(
            len(image_mean[0])*len(image_mean[0][0]),1)) #

        # We reset all values under 30.
        image_mean[0][image_mean[0]<30] = 0 #

        # We create a vector to be easier to process
        for index in range(len(self.dicomList)): 
            # analysis =np.append(analysis,np.reshape(image_mean[index],(
            #     len(image_mean[0])*len(image_mean[0][0]),1))) 
            analysis[:,[index]] = np.reshape(image_mean[index],(
                len(image_mean[0])*len(image_mean[0][0]),1))

        matLog = np.log(analysis)
        arrSum = matLog.sum(axis=1)
        arrLogEchoTime = np.matmul(matLog,-self.echoTimeArr)

        arrB = np.stack((arrSum,arrLogEchoTime))
        A = np.array([[len(self.dicomList), echoTimeSum],[echoTimeSum, echoTimeMul]])  
        invA = np.linalg.inv(A)
        #P = np.apply_along_axis(lambda x:np.matmul(invA,x),0,arrB)
        P = np.matmul(invA,arrB)
        
        P[np.isnan(P)] = 0

        self.imgMatrix = np.transpose(P)[:,[1]]
        self.imgMatrix = 1000/self.imgMatrix
        # Reshape T2 for the size needed
        self.imgMatrix = np.reshape(self.imgMatrix,(len(image_mean[0]),len(image_mean[0][0])))
        self.MSE=""
        # self.size = self.imgMatrix.shape
    
    @timer 
    def plotFigure(self,gray=True):
        # Deletar imagens da pasta antes
        if os.path.isfile(self.colorName):
            map(os.remove,(self.colorName,self.grayName))
        self.colorName = f'{os.path.dirname(__file__)}\\imgs\\color{self.dicomList[0].StudyID}.png'
        if gray:
            self.grayName = f'{os.path.dirname(__file__)}\\imgs\\gray{self.dicomList[0].StudyID}.png'
            self.exportFigure(self.dicomList[0],self.grayName,cmap=matplot.cm.get_cmap('gray_r'), plt_show=False)
            self.imgEcho = Image.open(self.grayName)
        self.exportFigure(self.imgMatrix, self.colorName,cmap=self.color, vmin=self.minColor, vmax=self.maxColor, plt_show=False)
        self.imgStar = Image.open(self.colorName)
        self.resultImage = self.removeTransparency(self.imgEcho)
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
        ax.imshow(self.imgMatrix,cmap=cmap, vmin=vmin, vmax=vmax)
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
                circleCenter = (int(roi.x1+(roi.x2-roi.x1)/2),int(roi.y1+(roi.y2-roi.y1)/2))
                #Para o raio, é só usar a mesma logica do centro
                #Só que sem somar o zero do Roi
                radius = int((roi.x2-roi.x1)/2)
                mask = cv2.circle(mask,circleCenter,radius,(255, 255, 255), -1) # pylint: disable=maybe-no-member
            mask_inv = cv2.bitwise_not(mask) # pylint: disable=maybe-no-member
            imgEcho_bg = cv2.bitwise_or(cvEcho, cvEcho, mask = mask_inv) # pylint: disable=maybe-no-member
            imgStar_fg = cv2.bitwise_or(cvStar, cvStar, mask = mask) # pylint: disable=maybe-no-member
            cvEcho = cv2.add(imgEcho_bg,imgStar_fg) # pylint: disable=maybe-no-member
        #cvEcho = np.dstack([cvEcho, alpha])
        self.resultImage = Image.fromarray(cvEcho)  