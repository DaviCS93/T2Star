import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib as matplot
from matplotlib.colors import ListedColormap

redScale=0.2
    
jet = matplot.cm.get_cmap(name='jet')
jet_arr = jet(np.linspace(0, 1,128))
jet_reverse = matplot.cm.get_cmap(name='jet_r')
jet_reverse_arr = jet_reverse(np.linspace(0, 1, 128))
if redScale >0.5:
    jet_reverse_arr=jet_reverse_arr[1:-1-(int((redScale-0.5)*256)),:] #deletar slice (redScale-0.5)*256
elif redScale <0.5:
    jet_arr=jet_arr[int(1-(int((redScale*(-256)+128)))):len(jet_arr),:] #deletar slice redScale*256
jet_combined_arr = np.concatenate((jet_arr,jet_reverse_arr))
jet_combined = ListedColormap(jet_combined_arr)
gradient = np.linspace(0, 1, 180)
gradient = np.vstack((gradient, gradient))
fig, ax = plt.subplots(nrows=1, figsize=(10, 1))
ax.imshow(gradient, aspect='auto', cmap=jet_combined)
ax.set_axis_off()
plt.savefig("scale",bbox_inches = 'tight', dpi=200)