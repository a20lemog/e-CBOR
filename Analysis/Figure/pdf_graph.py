import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from itertools import accumulate





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


plt.plot(x_a, y_a, 'r--')
plt.plot(x_aaaa, y_aaaa,'b--')
plt.plot(x_cname, y_cname, 'g--')
plt.plot(x_soa, y_soa, 'k--')

# Annotate the plot
plt.legend(('A', 'AAAA', 'CNAME','SOA'), loc='upper right')
_ = plt.xlabel('Length_name_ref(L)')
_ = plt.ylabel('PDF')

# Display the plot
plt.show()
plt.savefig("query.pdf")