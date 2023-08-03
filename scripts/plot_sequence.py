#!/usr/bin/python3.9

# XXX XXX Draft! XXX XXX

from os import scandir
from os.path import join
from argparse import ArgumentParser

from hypernets.reader.spectra import Spectra

import matplotlib.pyplot as plt # noqa
import seaborn as sns

sns.set()


class SequencePlotter(object):
    def __init__(self, dirname: str, display_options: tuple):
        """
        Scan sequence dir and plot by group according to options
        and prefixes / extensions filenames
        """
        list_dir = list(scandir(join(dirname, 'RADIOMETER')))

        for group in display_options.keys():

            print(f"-- Processing group: {group} --")  # noqa

            for entry in list_dir:

                if entry.name[3:6] not in display_options[group][0]:
                    continue

                for spectrum in Spectra(entry.path):
                    print(f"{spectrum.timestamp}")
                    display_options[group][1].plot(spectrum.counts)

                    # XXX QUICKFIX
                    self.current_spectrum = spectrum

                display_options[group][1].title.set_text(group)
                list_dir.remove(entry)

    @staticmethod
    def load_validation_ref():
        from csv import reader
        return [int(x[0]) for x in
                list(reader(open("SEQ20230525T230119_001_1.csv", "r")))]


if __name__ == '__main__':

    parser = ArgumentParser()

    parser.add_argument("-d", "--directory", type=str, required=True,
                        help="Select a Sequence Directory")

    parser.add_argument("-t", "--display-type", type=str, default="water",
                        choices=['water', 'validation'],
                        help="Chose the type of display")

    args = parser.parse_args()

    if args.display_type == "water":
        fig, ((ax1, ax2), (ax3, ax4)),  = \
            plt.subplots(2, 2, sharey='row', sharex='col')

        display_options = {"Ed": (["001", "013"], ax1),
                           "Ld": (["004", "010"], ax2),
                           "Lu": (["007"]       , ax3)} # noqa

        ax1.set_ylabel("DN")
        ax3.set_ylabel("DN")

    elif args.display_type == "validation":
        fig, ((ax1, ax2), (ax3, ax4)),  = \
            plt.subplots(2, 2, sharex='col')

        display_options = {"L (instrument)": (["001"], ax1),
                           "E (insturment)": (["002"], ax2)}

        # XXX QUICKFIX
        ref = SequencePlotter.load_validation_ref()
        ax3.plot(ref)

        ax3.title.set_text("Reference")

        ax1.set_ylabel("DN")
        ax3.set_ylabel("DN")


SP = SequencePlotter(args.directory, display_options)

if args.display_type == "validation":
    # FIXME Percentage
    ax2.plot([(a - b) / abs(a)
             for a, b in zip(SP.current_spectrum.counts, ref)])

    ax2.title.set_text("Error (%)")

    # FIXME Difference
    ax4.plot([a - b for a, b in zip(SP.current_spectrum.counts, ref)])
    ax4.title.set_text("Difference")

# fig.tight_layout(pad=3)
fig.suptitle(f"{args.directory}: {args.display_type}")
fig.show()
