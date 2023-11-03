#!/usr/bin/python3.8

from netCDF4 import Dataset
from glob import glob
from datetime import datetime
from os.path import basename, join

import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


input_dir = "./nc_data/20/"
output_dir = "./html/monitor/BEFR_last_sequences/"
selection = slice(106, 1229)  # Plot Only 400 ~ 950 nm


def plot_product(data, desc, ax):
    ax.plot(data["wavelength"][selection],
            data[desc][selection], linewidth=0.5)
    ax.title.set_text(desc)
    ax.set_ylabel(data[desc].units)


for filename in sorted(glob(join(input_dir, "**/*L1C*"), recursive=True)):

    print(filename)

    data = Dataset(filename, 'r')
    acq_dt = datetime.fromtimestamp(int(data["acquisition_time"][0]))

    fig, axs = plt.subplots(2, 2, sharex='col', constrained_layout=True)

    # Plot the 3 'all' measures from L1C product
    for ax, desc in zip(axs.reshape(-1), ["irradiance", "upwelling_radiance",
                                          "downwelling_radiance"]):
        plot_product(data, desc, ax)

    # Plot the reflectance (averaged) from L2A product
    data = Dataset(filename.replace("L1C_ALL", "L2A_REF"))
    plot_product(data, "reflectance", axs[1, 1])

    # Global settings of the plot
    axs[1, 0].set_xlabel("Wavelength (nm)")
    axs[1, 1].set_xlabel("Wavelength (nm)")
    fig.set_size_inches(18.5, 10.5)
    plt.suptitle(f"{acq_dt.strftime('%d-%b %Y - %H:%M:%S')}", fontsize=18)

    # Save plot
    output_name = basename(filename)[:17] + basename(filename)[25:-3] + ".png"
    plt.savefig(join(output_dir, output_name))
    plt.close(fig)
