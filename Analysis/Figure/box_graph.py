import socket

import base64

import os
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
import plotly.express as px



# Set the figure size
plt.rcParams["figure.figsize"] = [8.00, 3.0]
plt.rcParams["figure.autolayout"] = True
#plt.rcParams["font.serif"] = "Times New Roman NN"

# Import a Seaborn dataset
# data = sns.load_dataset('abcok.csv')
data = pd.read_csv("abcok.csv")

# Create a grouped boxplot

palette = sns.color_palette("muted")
box = sns.boxplot(x=data['Length_name_ref(L)'], y=data['Gain(%)'], hue=data['rrs'], palette = palette, linewidth=1)
plt.legend(loc='upper right', title='RRs')

plt.xlabel("Name_ref Length", fontname='Times New Roman NN')
plt.ylabel("% of Gain")
plt.grid()


#plt.show()
plt.savefig("box_1.pdf") 





