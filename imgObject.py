import warnings 
import os
from decorators import timer
import matplotlib.pyplot as plt
import matplotlib as matplot
import numpy as np
import cv2
from matplotlib.colors import Normalize,ListedColormap
from scipy.signal import medfilt2d
from PIL import Image
from shape import Shape
from canvasElements import ROI,DrawnLines
from math import inf

class imgObject():
    """
    docstring
    """
     
    def __init__(self,dicomList,examName):
        self.examName = examName
        self.imgMatrix = None
        self.imgMSE = None
        self.maxColor = 200
        self.minColor = 40
        self.maxGray = 200
        self.minGray = 0
        self.listROI = []
        self.listEchoTime = []
        self.figure = plt.figure(figsize=(6, 6),frameon=False)
        self.dicomList = dicomList
        self.grayName = ""
        self.cannyName = ""
        self.colorName = ""
        self.imgEcho = None
        self.imgStar = None
        self.imgCanny = None
        self.resultRoiImage = None
        self.resultColorImage = None
        self.size = dicomList[0].pixel_array.shape
        self.norm = Normalize(vmin=0,vmax=255)
        # Zoom ativo
        self.activeZoom = 1
        for ds in dicomList[1:]:
            self.listEchoTime.append(ds.EchoTime/1000) 
        # Cria as imagens no que é carregado os arquivos
        self.createFigure()
        self.plotFigure()
        
    @timer 
    def createFigure(self):
        """
        docstring
        """  
        #Create 3 matrix of zeros with the same size as the dicom, and z-axis same length as images cound
        #First is for the means, second is for the analysis and third is for the final results
        self.imageMean = np.zeros((*self.size,len(self.dicomList)))
        analysis = np.zeros((*self.size,len(self.dicomList)))
        self.imgMatrix = np.zeros((self.size[0]*self.size[1],1)) 
        warnings.filterwarnings('ignore')

        # Process the TE to get the values needed for the process later
        # We need a negative sum value, an array with all times and a matrix with
        # these two arrays multiplied (1 transpose)
        echoTimeSum = -sum(self.listEchoTime) 
        self.echoTimeArr = np.array(self.listEchoTime) 
        echoTimeMul = np.matmul(np.transpose(self.echoTimeArr),self.echoTimeArr) 

        # For each dicom, we need to take the image mean, so
        # we can remove noise
        for index in range(len(self.dicomList)):
            a = medfilt2d(
                np.array(self.dicomList[index].pixel_array,dtype=np.float))
            self.imageMean[:,:,index] = a

        # We reset all values under 30.
        self.imageMean[self.imageMean[:,:,0]<30] = 0
        analysis = np.zeros((self.size[0]*self.size[1],len(self.listEchoTime))) 

        # We create a vector to be easier to process
        # for each layer in the matrix imageMean we create a vector, converting it from
        # a M,N,L matrix to a M*N,L,1 matrix (setting it for analysis)
        for i in range(1,len(self.dicomList)):
            imageMeanTrans = np.transpose(self.imageMean[:,:,i])
            reshapeResult = np.reshape(imageMeanTrans,(self.size[0]*self.size[1]))
            analysis[:,i-1] = reshapeResult
        
        # Apply the log for the analysis (cap the - infinite to 0, no reason to have negative values)
        matLog = np.log(analysis)
        matLog[matLog == -inf] = 0
        
        # We sum all pixels from different images in the same array
        arrSum = matLog.sum(axis=1)
        
        # Multiply the previous log result with the time echo array
        # we have M*N,L X L,1 = M*N,1
        arrLogEchoTime = np.matmul(matLog,-self.echoTimeArr)

        #
        arrB = np.stack((arrSum,arrLogEchoTime))
        A = np.array([[len(self.listEchoTime), echoTimeSum],[echoTimeSum, echoTimeMul]])  
        invA = np.linalg.inv(A)
        P = np.matmul(invA,arrB)
        self.imgMatrix = np.transpose(P)[:,[1]]
        self.imgMatrix = np.transpose(np.reshape(self.imgMatrix,self.size))
        self.imgMatrix = 1000/self.imgMatrix
        
        # Reshape T2 for the size needed
        self.s0 = np.exp(P[[0],:])
        self.echoTimeArr = np.reshape(self.echoTimeArr,(self.echoTimeArr.shape[0],1))
        mulTimeP = np.matmul(-self.echoTimeArr,P[[1],:])
        exTimeP = np.exp(mulTimeP)
        yPred = np.multiply(exTimeP,self.s0)

        sse = np.square(analysis-np.transpose(yPred)).sum(axis=1)
        self.imgMSE = sse/len(self.dicomList)
        self.imgMSE = np.reshape(self.imgMSE,self.size)
        np.savetxt('imgMSE.txt',self.imgMSE,fmt='%.2f')
        np.savetxt('imgMatrix.txt',self.imgMatrix,fmt='%.2f')

    @timer 
    def plotFigure(self):
        # Deletar imagens da pasta antes-
        if os.path.isfile(self.colorName):
            map(os.remove,(self.colorName,self.grayName))
        self.colorName = f'{os.path.dirname(__file__)}\\imgs\\color{self.examName}.png'
        self.grayName = f'{os.path.dirname(__file__)}\\imgs\\gray{self.examName}.png'
        #self.exportFigure(self.dicomList[0].pixel_array,self.grayName,cmap=matplot.cm.get_cmap('gray_r'), plt_show=False)
        self.exportFigure(self.imgMatrix,self.grayName,cmap='gray',vmax=self.maxGray,vmin=self.minGray,plt_show=False)
        self.exportFigure(self.imgMatrix, self.colorName,cmap='jet',vmax=self.maxColor,vmin=self.minColor, plt_show=False)
        #self.exportFigure(self.imgMatrix, self.colorName,cmap='jet', vmin=self.minColor, vmax=self.maxColor, plt_show=False)
        # self.imgCanny = cv2.Canny(imgTemp,40,150)
        # self.cannyName = f'{os.path.dirname(__file__)}\\imgs\\canny{self.dicomList[0].StudyID}.png'
        # self.exportFigure(self.imgCanny,self.cannyName,cmap=matplot.cm.get_cmap('gray_r'), plt_show=False)
        self.imgEcho = Image.open(self.grayName)
        self.imgStar = Image.open(self.colorName)
        # self.imgCanny = Image.open(self.cannyName)
        self.resultColorImage = self.removeTransparency(self.imgStar)
        self.resultRoiImage = self.removeTransparency(self.imgEcho)  
        # self.resultImage = self.imgCanny

    @timer
    def getDicomImage(self,matrix):
        imgPath = f'{os.path.dirname(__file__)}\\imgs\\dicom{self.examName}.png'
        self.exportFigure(matrix,imgPath,cmap='gray',vmax=255,vmin=0,plt_show=False)
        return Image.open(imgPath)

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
    def setColors(self,max,min):
        """
        docstring
        """
        self.maxColor = max
        self.minColor = min

    @timer 
    def setGray(self,max,min):
        """
        docstring
        """
        self.maxGray = max
        self.minGray = min

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
        ax.imshow(matrix,cmap=cmap,norm=self.norm,vmin=vmin, vmax=vmax)#,
        #ax.imshow(matrix,cmap=cmap)
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
            if roi.shape == Shape.FREE:
                points = np.array(roi.points,np.int32)
                mask = cv2.fillPoly(mask,[points],(255, 255, 255)) # pylint: disable=maybe-no-member
            if roi.shape == Shape.RECTANGLE:
                mask = cv2.rectangle(mask,roi.start,roi.end,(255, 255, 255), -1) # pylint: disable=maybe-no-member
            if roi.shape == Shape.CIRCLE:
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
            # cvEcho2 = cvEcho
            cvEcho = cv2.add(imgEcho_bg,imgStar_fg) # pylint: disable=maybe-no-member
            if not roi.definedInfo: 
                roi.mean,roi.std = cv2.meanStdDev(self.imgMatrix,mask=mask)
                roi.mean,roi.std = round(roi.mean[0][0], 2),round(roi.std[0][0], 2)
                minn,maxx,minLoc,maxLoc  = cv2.minMaxLoc(self.imgMatrix,mask)
                roi.min = round(minn,2)
                roi.max = round(maxx,2)
                roi.area =cv2.countNonZero(mask)
                roi.pix = f'{round(100*roi.area/self.imgMatrix.size,2)}%'
                roi.mse = np.sqrt(cv2.meanStdDev(self.imgMSE,mask=mask)[0][0][0])
                roi.mse = round(roi.mse,2)
                analysis = np.ndarray((0,))
                for i in range(1,len(self.dicomList)):
                    mean = cv2.meanStdDev(self.imageMean[:,:,i],mask=mask)
                    analysis = np.concatenate((analysis,mean[0][0]))
                self.echoTimeArr = np.array(self.listEchoTime) 
                
                matLog = np.log(analysis)
                arrSum = matLog.sum(axis=0)
                arrLogEchoTime = np.matmul(matLog,-self.echoTimeArr)
                echoTimeSum = -sum(self.listEchoTime) 
                roi.time = np.arange(self.listEchoTime[0]*1000,self.listEchoTime[-1]*1000,1)
                echoTimeMul = np.matmul(np.transpose(self.echoTimeArr),self.echoTimeArr) 
                arrB = np.stack((arrSum,arrLogEchoTime))
                A = np.array([[len(self.listEchoTime), echoTimeSum],[echoTimeSum, echoTimeMul]])  
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
        
        self.resultRoiImage = Image.fromarray(cvEcho)  

    @timer
    def saveRoi(self,roi):
        cvEcho = cv2.imread(self.grayName) # pylint: disable=maybe-no-member
        cvStar = cv2.imread(self.colorName) # pylint: disable=maybe-no-member
        mask = np.zeros(self.size, np.uint8)
        if roi.shape == Shape.FREE:
            points = np.array(roi.points,np.int32)
            mask = cv2.fillPoly(mask,[points],(255, 255, 255)) # pylint: disable=maybe-no-member
        if roi.shape == Shape.RECTANGLE:
            mask = cv2.rectangle(mask,roi.start,roi.end,(255, 255, 255), -1) # pylint: disable=maybe-no-member
        if roi.shape == Shape.CIRCLE:
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
        # cvEcho2 = cvEcho
        cvEcho = cv2.add(imgEcho_bg,imgStar_fg) # pylint: disable=maybe-no-member
        name = f'{os.path.dirname(__file__)}\\imgs\\{self.examName}_{roi.elmId}.png'
        cv2.imwrite(name, cvEcho)
        roi.imgFile = name

    @timer
    def printColorScale(self,clock):
        jet = matplot.cm.get_cmap(name='jet_r')
        jet_arr = jet(np.linspace(0, 1,255))
        #jet_arr=jet_arr[self.minColor:self.maxColor,:] #deletar slice (redScale-0.5)*256
        jet_cmap = ListedColormap(jet_arr)
        gradient = np.linspace(0, 1, 255)
        gradient = np.vstack((gradient, gradient))
        fig, ax = plt.subplots(nrows=1, figsize=(10, 1))
        ax.imshow(gradient, aspect='auto', cmap=jet_cmap)
        ax.set_axis_off()
        scale = f"{os.path.dirname(__file__)}\\imgs\\scale{self.examName}.png"
        plt.savefig(scale,bbox_inches = 'tight', dpi=200)
        plt.close()
        if clock:
            return Image.fromarray(cv2.rotate(cv2.imread(scale),rotateCode=cv2.ROTATE_90_COUNTERCLOCKWISE))
        else:
            return Image.fromarray(cv2.rotate(cv2.imread(scale),rotateCode=cv2.ROTATE_90_CLOCKWISE))

if __name__=="__main__":
    img = imgObject(None,"test")
    img.defineGray()
    img.defineJet()