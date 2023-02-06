import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from itertools import accumulate
import seaborn as sns

plt.rcParams["figure.figsize"] = [4.00, 3.0]
plt.rcParams["figure.autolayout"] = True

def ecdf(data):
    """Compute ECDF for a one-dimensional array of measurements."""
    # Number of data points: n
    
    n = len(data)

    sorted_list = np.sort(data)

    unique_list = []

    for x in sorted_list :
        if x not in unique_list:
            unique_list.append(x)

    unique_sum = []

    for y in unique_list:
        unique_sum.append(sum(sorted_list == y)/n)

    print("HERE",unique_sum)

    return unique_list, unique_sum


# GENERATE EXAMPLE DATA
ecbor_df = pd.read_csv("abcok.csv")

a = ecbor_df['Length_name_ref(L)'][ecbor_df.rrs == 'A']
aaaa = ecbor_df['Length_name_ref(L)'][ecbor_df.rrs == 'AAAA']
cname= ecbor_df['Length_name_ref(L)'][ecbor_df.rrs == 'CNAME']
soa = ecbor_df['Length_name_ref(L)'][ecbor_df.rrs == 'SOA']

# Compute ECDFs
x_a, y_a = ecdf(a)
x_aaaa, y_aaaa = ecdf(aaaa)
x_cname, y_cname = ecdf(cname)
x_soa, y_soa = ecdf(soa)

# Plot all ECDFs on the same plot

linestyles=[":", "-","-"]
x = [x_a, x_aaaa, x_cname, x_soa]
y = y_a

print(x,y)

ax = sns.lineplot(x_a, y_a, marker='o')
ax = sns.lineplot(x_aaaa, y_aaaa, marker='^')
ax = sns.lineplot(x_cname, y_cname, marker='<')
ax = sns.lineplot(x_soa, y_soa, marker='v')

print(len(ax.lines))
for x in range (0, len(ax.lines)):
    ax.lines[x].set_linestyle("--")


# Annotate the plot
plt.legend(('A', 'AAAA', 'CNAME','SOA'), loc='upper right')
_ = plt.xlabel('Name_ref Length')
_ = plt.ylabel('PDF')

# Display the plot
#plt.show()
plt.savefig("cdf2_1.pdf")