#!/usr/bin/python3.8

from netCDF4 import Dataset

from sys import exit
from os import listdir
from os.path import basename, join, isdir, exists, dirname

from glob import glob
from datetime import datetime
from argparse import ArgumentParser

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns

plt.rcParams['mathtext.default'] = 'regular'
sns.set()


class ProductPlotter(object):

    def __init__(self, path_to_file, output_dir, wl_start=0, wl_stop=None,
                 title=""):

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
        self.title = title

    def generate_plots(self, pdf=None):

        fig, axs = plt.subplots(3, 2, sharex='col', constrained_layout=True)

        # Plot the 3 'all' measures from L1C product
        products_to_plot = [("irradiance", "$E_d(λ)$"),
                            ("upwelling_radiance", "$L_u(λ)$"),
                            ("downwelling_radiance", "$L_d$(λ)")]

        for n, (ax, (desc, title)) in enumerate(zip([(1, 0), (1, 1), (2, 0)],
                                                products_to_plot)):
            print(f"== {n} [{desc} ({title})--> {ax}]")
            self.plot_product(self.nc, self._mask, desc, axs[ax], title)

        # Plot the averaged reflectances [sc & nosc] from L2A if it exists
        self.plot_reflectances(axs[2, 1])

        # Add images of the radiometer for each geometry
        self.add_images(fig)

        # Global settings of the plot
        axs[0, 0].axis("off")
        axs[0, 1].axis("off")

        axs[2, 1].set_xlabel("Wavelength (nm)")
        fig.set_size_inches(8.3, 5.8)  # format A5
        fig.set_size_inches(11.7, 8.3)  # format A4

        # Title generated from the timestamp of the measure
        acq_dt = datetime.fromtimestamp(int(self.nc["acquisition_time"][0]))
        # if self.title is not None:
        plt.suptitle(f"{self.title} - {acq_dt.strftime('%d-%b %Y - %H:%M:%S')}",  # noqa
                     fontsize=14, weight='bold')

        # Save plot
        output_name = basename(self.path_to_file)[:17] + basename(self.path_to_file)[25:-3] # noqa
        # makedirs(self.output_dir, exist_ok=True)
        if pdf is not None:
            pdf.savefig(fig)
        else:
            plt.savefig(join(self.output_dir, output_name + ".png"))
        plt.close(fig)

    @staticmethod
    def plot_product(data, mask, desc, ax, title=None):
        ax.plot(data["wavelength"][mask],
                data[desc][mask], linewidth=0.5)

        if title is None:
            title = f"{desc}"

        ax.set_title(title, fontsize=13)
        ax.set_ylabel(data[desc].units, fontsize=10)

    def plot_reflectances(self, ax):
        try:
            data = Dataset(self.path_to_file.replace("L1C_ALL", "L2A_REF"))
            self.plot_product(data, self._mask, "reflectance", ax)
            self.plot_product(data, self._mask, "reflectance_nosc", ax, "$ρ_w$(λ)")  # noqa
            ax.legend(["$ρ_w$", "$ρ_{w-nosc}$"], loc='upper right')

        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("One second difference in the processor? (FIXME)")

    def add_images(self, fig):

        im_l, im_b,  im_w, im_h = .12, .82, .1, .1

        images_layout = [("003", [im_l, im_b, im_w, im_h]),           # Ed
                         ("015", [im_l, im_b-1.17*im_h, im_w, im_h]),
                         ("006", [im_l+1.01*im_w, im_b, im_w, im_h]),  # Ld
                         ("012", [im_l+1.01*im_w, im_b-1.17*im_h, im_w, im_h]),
                         ("009", [im_l+2.02*im_w, im_b, im_w, im_h]),  # Lu Sun
                         ("016", [im_l+2.02*im_w, im_b-1.17*im_h, im_w, im_h])]

        images_dir = dirname(self.path_to_file)+"/image/"

        if not isdir(images_dir):
            return

        pattern_base = basename(self.path_to_file).replace("L1C", "IMG").replace("ALL_", "")[:48] # noqa

        for img_name in listdir(images_dir):
            for pattern, location in images_layout:
                if f"{pattern_base}_{pattern}" in img_name:
                    im = plt.imread(images_dir + img_name)
                    ax = fig.add_axes(location)
                    # TODO : test rotation
                    # from matplotlib import transforms
                    #  ax.imshow(im, transform=transforms.Affine2D().
                    #            rotate_deg(90) + ax.transData)
                    ax.imshow(im)
                    ax.set_title(pattern, fontsize=9, pad=2)
                    ax.axis('off')

    def __del__(self):
        self.nc.close()


if __name__ == '__main__':

    def valid_dir(path):
        if isdir(path):
            return path
        else:
            raise NotADirectoryError(path)
            exit(1)

    def valid_file(path):
        if exists(path):
            return path
        else:
            raise FileNotFoundError(path)
            exit(1)

    parser = ArgumentParser()

    input_type = parser.add_mutually_exclusive_group(required=True)

    input_type.add_argument("-i", "--input-dir", type=valid_dir,
                            help="Select a folder to perform all plots.")

    input_type.add_argument("-f", "--input-file", type=valid_file,
                            help="Select a L1C netcdf file.")

    parser.add_argument("-o", "--output-dir", type=valid_dir,
                        help="Specify the output directory", default="./"),

    parser.add_argument("-t", "--title", type=str,
                        help="Set the site name.", default="")

    parser.add_argument("-p", "--pdf", type=str,
                        help="Output a PDF file instead of seperate PNG images.") # noqa

    # Note: Default values could be 400 ~ 950 nm
    parser.add_argument("-a", "--start-wl", type=int,
                        help="Data slicer (inclusive) starting wavelength"
                        " to plot", default=0)

    parser.add_argument("-b", "--stop-wl", type=int,
                        help="Data slicer (inclusive) stopping wavelength"
                        " to plot", default=None)

    args = parser.parse_args()

    if args.input_file:
        pp = ProductPlotter(args.input_file, args.output_dir, args.start_wl,
                            args.stop_wl, args.title)
        pp.generate_plots(pdf=None)

    elif args.input_dir:
        if args.pdf:
            with PdfPages("foo.pdf") as pdf_file:
                for filename in sorted(glob(join(args.input_dir, "**/*L1C*"),
                                       recursive=True)):
                    print(f"Processing {filename}...")
                    pp = ProductPlotter(filename, args.output_dir,
                                        args.start_wl, args.stop_wl)
                    pp.generate_plots(pdf=pdf_file)
        else:
            for filename in sorted(glob(join(args.input_dir, "**/*L1C*"),
                                   recursive=True)):

                print(f"Processing {filename}...")
                pp = ProductPlotter(filename, args.output_dir,
                                    args.start_wl, args.stop_wl)
                pp.generate_plots()
