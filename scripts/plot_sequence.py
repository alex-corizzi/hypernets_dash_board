#!/usr/bin/python3.8

from netCDF4 import Dataset

from os.path import basename, join, isdir, exists, dirname
from os import listdir


from glob import glob
from datetime import datetime
from argparse import ArgumentParser

import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


class ProductPlotter(object):

    def __init__(self, path_to_file, output_dir, wl_start=0, wl_stop=None):

        self.output_dir = output_dir
        self.path_to_file = path_to_file

        # netCDF4 not designed to do inheritance; composition instead
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
        for n, (ax, desc) in enumerate(zip(axs.reshape(-1),
                                       ["irradiance", "upwelling_radiance",
                                        "downwelling_radiance"])):

            print(f"== {n} [{desc} --> {ax}]")
            self.plot_product(self.nc, self._mask, desc, ax)

        # Plot the reflectance (averaged) from L2A product
        try:
            data = Dataset(self.path_to_file.replace("L1C_ALL", "L2A_REF"))
            self.plot_product(data, self._mask, "reflectance", axs[1, 1])
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("One second difference in the processor? (FIXME)")

        # Add images of the radiometer for each geometry
        self.add_images(fig)

        # Global settings of the plot
        axs[1, 0].set_xlabel("Wavelength (nm)")
        axs[1, 1].set_xlabel("Wavelength (nm)")
        fig.set_size_inches(18.5, 10.5)

        # Title generated from the timestamp of the measure
        acq_dt = datetime.fromtimestamp(int(self.nc["acquisition_time"][0]))
        plt.suptitle(f"{acq_dt.strftime('%d-%b %Y - %H:%M:%S')}", fontsize=18)

        # Save plot
        output_name = basename(self.path_to_file)[:17] + basename(self.path_to_file)[25:-3] + ".png"  # noqa

        # makedirs(self.output_dir, exist_ok=True)
        plt.savefig(join(self.output_dir, output_name))
        plt.close(fig)

    @staticmethod
    def plot_product(data, mask, desc, ax):
        ax.plot(data["wavelength"][mask],
                data[desc][mask], linewidth=0.5)
        ax.title.set_text(desc)
        ax.set_ylabel(data[desc].units)

    def add_images(self, fig):

        images_layout = [("003", [.4, .84, .1, .1]),    # Ed
                         ("015", [.4, .74, .1, .1]),
                         ("006", [.4, .38, .1, .1]),  # Ld
                         ("012", [.4, .28, .1, .1]),
                         ("009", [.905, .84, .1, .1]),    # Lu
                         ("016", [.905, .38, .1, .1])]  # Sun

        images_dir = dirname(self.path_to_file)+"/image/"

        if not isdir(images_dir):
            return

        pattern_base = basename(self.path_to_file).replace("L1C", "IMG").replace("ALL_", "")[:48] # noqa

        for img_name in listdir(images_dir):
            for pattern, location in images_layout:
                if f"{pattern_base}_{pattern}" in img_name:
                    im = plt.imread(images_dir + img_name)
                    newax = fig.add_axes(location)
                    newax.imshow(im)
                    newax.axis('off')

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

    # Note: Default values could be 400 ~ 950 nm
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
