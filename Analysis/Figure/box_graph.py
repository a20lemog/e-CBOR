import socket

import base64

import os
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
import plotly.express as px



# Set the figure size
plt.rcParams["figure.figsize"] = [8.00, 3.50]
plt.rcParams["figure.autolayout"] = True

# Import a Seaborn dataset
# data = sns.load_dataset('abcok.csv')
data = pd.read_csv("abcok.csv")

# Create a grouped boxplot
sns.boxplot(x=data['Length_name_ref(L)'], y=data['Gain(%)'], hue=data['RRs:'])

plt.show()
plt.savefig("query.pdf") 





