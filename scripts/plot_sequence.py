#!/usr/bin/python3.8

from netCDF4 import Dataset

from os.path import basename, join, isdir, exists

from glob import glob
from datetime import datetime

from argparse import ArgumentParser

from numpy import where
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


class ProductPlotter(object):

    def __init__(self, path_to_file, output_dir, wl_start=0, wl_stop=None):

        self.output_dir = output_dir
        self.filename = path_to_file

        # Note: NetCDF is not designed to do inheritance
        self.nc = Dataset(path_to_file, 'r')

        cond_start = self.nc["wavelength"][:] >= wl_start

        if wl_stop is not None:
            cond_stop = self.nc["wavelength"][:] <= wl_stop
        else:
            cond_stop = True

        self._mask = cond_start & cond_stop

    def generate_plots(self):

        fig, axs = plt.subplots(2, 2, sharex='col', constrained_layout=True)

        # Plot the 3 'all' measures from L1C product
        for ax, desc in zip(axs.reshape(-1),
                            ["irradiance", "upwelling_radiance", "downwelling_radiance"]):  # noqa
            self.plot_product(self.nc, self._mask, desc, ax)

        # Plot the reflectance (averaged) from L2A product
        data = Dataset(self.filename.replace("L1C_ALL", "L2A_REF"))
        self.plot_product(data, self._mask, "reflectance", axs[1, 1])

        # Global settings of the plot
        axs[1, 0].set_xlabel("Wavelength (nm)")
        axs[1, 1].set_xlabel("Wavelength (nm)")
        fig.set_size_inches(18.5, 10.5)

        acq_dt = datetime.fromtimestamp(int(self.nc["acquisition_time"][0]))
        plt.suptitle(f"{acq_dt.strftime('%d-%b %Y - %H:%M:%S')}", fontsize=18)

        # Save plot
        output_name = basename(self.filename)[:17] + basename(self.filename)[25:-3] + ".png"  # noqa
        # makedirs(self.output_dir, exist_ok=True)
        plt.savefig(join(self.output_dir, output_name))
        plt.close(fig)

    @staticmethod
    def plot_product(data, mask, desc, ax):
        ax.plot(data["wavelength"][mask],
                data[desc][mask], linewidth=0.5)
        ax.title.set_text(desc)
        ax.set_ylabel(data[desc].units)

    def __del__(self):
        self.nc.close()


if __name__ == '__main__':

    def valid_dir(path):
        if isdir(path):
            return path
        else:
            raise NotADirectoryError(path)

    def valid_file(path):
        if exists(path):
            return path
        else:
            raise FileNotFoundError(path)

    parser = ArgumentParser()

    input_type = parser.add_mutually_exclusive_group(required=True)

    input_type.add_argument("-i", "--input-dir", type=valid_dir,
                            help="Select a folder to perform all plots.")

    input_type.add_argument("-f", "--input-file", type=valid_file,
                            help="Select a L1C netcdf file.")

    parser.add_argument("-o", "--output-dir", type=valid_dir,
                        help="Specify the output directory", default="./"),

    parser.add_argument("-a", "--start-wl", type=int,
                        help="Data slicer (inclusive) starting wavelength"
                        " to plot", default=0)

    parser.add_argument("-b", "--stop-wl", type=int,
                        help="Data slicer (inclusive) stopping wavelength"
                        " to plot", default=None)

    args = parser.parse_args()

    if args.input_file:
        pp = ProductPlotter(args.input_file, args.output_dir, args.start_wl, args.stop_wl)  # noqa
        pp.generate_plots()

    elif args.input_dir:
        for filename in sorted(glob(join(args.input_dir, "**/*L1C*"), recursive=True)):  # noqa
            print(filename)
            pp = ProductPlotter(filename, args.output_dir, args.start_wl, args.stop_wl)  # noqa
            pp.generate_plots()
