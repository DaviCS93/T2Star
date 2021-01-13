import numpy as np
from scipy.signal import medfilt2d
import pydicom
import os
import matplotlib.pyplot as plt
import matplotlib as matplot
import math
import time
from mpl_toolkits.axes_grid1 import Divider, Size
from mpl_toolkits.axes_grid1.mpl_axes import Axes
from matplotlib.colors import ListedColormap

jet = matplot.cm.get_cmap(name='jet')
jet_arr = jet(np.linspace(0, 1, 128))
jet_reverse = matplot.cm.get_cmap(name='jet_r')
jet_reverse_arr = jet_reverse(np.linspace(0, 1, 128))
jet_combined_arr = np.concatenate((jet_arr,jet_reverse_arr))
jet_combined = ListedColormap(jet_combined_arr)

tic = time.perf_counter()
pmFilelist=[]
TE=[]
imageFolder = "C:\\Users\\Feirron\\Downloads\\MAPAS\\Mapas T2 - Melhorias\\Processamento normal\\"
files = os.listdir(imageFolder)
files = [imageFolder + f for f in files]

for f in files:
    ds =pydicom.dcmread(f)
    pmFilelist.append(ds.pixel_array)
    TE.append(ds.EchoTime/1000)   

image = []
image_mean = []
ndados = len(pmFilelist)

for echo in pmFilelist:
    image_mean.append(medfilt2d(
        np.array(echo,dtype=np.float),
        kernel_size=3))

T2 = np.zeros((len(image_mean[0]),len(image_mean[0][0]))) #
T2 = np.reshape(T2,(
    len(image_mean[0])*len(image_mean[0][0]),1)) #
image_mean[0][image_mean[0]<30] = 0 #
analysis = [] #

for index,t in enumerate(TE): 
    analysis.append(np.reshape(image_mean[index],(
        len(image_mean[0])*len(image_mean[0][0]),1))) 

tempArr = analysis[0] # 

for aux in analysis[1:]: #
    tempArr = np.logical_and(tempArr,aux) 

indexes = [ind for ind, x in enumerate(tempArr) if x>0] 
sumTE = -sum(TE) # 
npTE = np.array(TE) #
prodTE = np.matmul(np.transpose(npTE),npTE) #

for index,indexValue in enumerate(indexes):
    finalAnalysis = np.empty((0,len(analysis[0][0])))  

    for i in range(len(pmFilelist)):
        finalAnalysis = np.append(finalAnalysis,analysis[i][indexValue])

    lstFinalAnalysis = np.array(list(map(np.log,finalAnalysis)))
    sumFinalAnalysis = sum(lstFinalAnalysis)
    sumFinalAnalysisTE = np.matmul(-np.transpose(npTE),lstFinalAnalysis)
    A = np.array([[ndados, sumTE],[sumTE, prodTE]])  
    B = np.array([[sumFinalAnalysis],[sumFinalAnalysisTE]])  
    invA =np.linalg.inv(A) 
    P = np.matmul(invA,B)
    T2[indexValue] = (P[1][0])

for i,t in enumerate(T2):
    T2[i] = math.inf if t[0] == 0 else 1000/t[0]

T2Star = np.reshape(T2,(400,400))
fig = plt.figure(figsize=(6, 6))
h = [Size.Fixed(1.0), Size.Fixed(5.)]
v = [Size.Fixed(1.0), Size.Fixed(5.)]
divider = Divider(fig, (0.0, 0.0, 1., 1.), h, v, aspect=False)
ax = Axes(fig, divider.get_position())
ax.set_axes_locator(divider.new_locator(nx=1, ny=1))
fig.add_axes(ax)
plt.pcolor(np.flip(T2Star,0), cmap=jet_combined, vmin=0, vmax=180)
toc = time.perf_counter()
print(f"Executed in {toc - tic:0.4f} seconds")



# toggle_selector.RS = RectangleSelector(ax, line_select_callback,
#                                        drawtype='box', useblit=True,
#                                        button=[1, 3],  # don't use middle button
#                                        minspanx=5, minspany=5,
#                                        spancoords='pixels',
#                                        interactive=True)

# plt.connect('key_press_event', toggle_selector)
plt.show()
