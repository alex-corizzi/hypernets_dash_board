#!/usr/bin/python


from datetime import datetime, date
from argparse import ArgumentParser
from os.path import basename

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

from dateutil.relativedelta import relativedelta
from pandas import to_datetime

from numpy import arange

import seaborn as sns

from color_picker import ColorPicker, color_parser_configuration

from scripts.hypernets_dataframe import HypernetsDataFrame
from scripts.hypernets_dataframe import basic_parser_configuration


parser = ArgumentParser()
parser = basic_parser_configuration(parser)
parser = color_parser_configuration(parser)

parser.add_argument("-m", "--marker", type=str,
                    help="Draw start / end marker on segment",
                    choices=["grey", "black"], default=None)


args = parser.parse_args()


# Make fancy plots -----------------------------------------------------------
sns.set()
sns.set_style('darkgrid')


if args.after is None and args.before is None:
    print("Default data selection (one month ago)")
    args.after = to_datetime(datetime.now() - relativedelta(months=1))


df = HypernetsDataFrame(args.filename, after=args.after, before=args.before)

color_picker = ColorPicker(args.color, args.palette)

# ----------------------------------------------------------------------------
# Plots ----------------------------------------------------------------------
# ----------------------------------------------------------------------------

fig, ((ax1, ax2), (ax3, ax4)),  = \
    plt.subplots(2, 2, sharey='row', sharex='col',
                 gridspec_kw={'width_ratios': [15, 1],
                              'height_ratios': [3, 1]})

for date_index in df['date'].unique():

    day = df[df['date'] == date_index]

    for t1, t2, nb_spe, nb_img, dark_count, serial_count, duration \
    in list(zip(day['start'], day['stop'], day['nb_spe'], # noqa
                day['nb_img'], day['tooDarkExcept'],
                day['serialExcept'], day['duration'])):

        times = [datetime.combine(date.today(), t) for t in [t1, t2]]

        color = color_picker.pickup(nb_spe, nb_img)

        # Quick fix : if duration is less eq than ~ 33s,
        # the segment doesn't appear
        # Note: may depend on linewidth?

        if duration <= 31:
            times = times[0], times[1] + relativedelta(seconds=(33 - duration))

        ax1.plot(times, [date_index, date_index], color=color, linewidth=10,
                 marker="|", markeredgecolor=args.marker)

        if dark_count != 0 or serial_count != 0:
            txt = ""

            if dark_count != 0:
                txt += f"D:{dark_count}"

            if serial_count != 0:
                txt += f" S:{serial_count}"

            ax1.text(times[0], date_index, txt, fontsize=5)

    ax2.text(0, date_index, str(len(day)), va="bottom")

    ax3.plot(day['start'].apply(lambda x: datetime.combine(date.today(), x)),
             day['light'], linewidth=.3)


df_light = df.get_dataframe_light(group_by_hour=True)

ax3.plot(df_light.index, df_light["light"]["mean"], "b", linewidth=1.5)

ax3.fill_between(df_light.index, df_light["mean_min"],
                 df_light["light"]["mean"] + df_light["light"]["std"],
                 color="b", alpha=0.3)

# ----------------------------------------------------------------------------
# Titles + Legend ------------------------------------------------------------
# ----------------------------------------------------------------------------

ax1.xaxis.set_minor_formatter((mdates.DateFormatter("%M")))

ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
ax1.title.set_text(f"{args.title}: Duration of sequences over the last month\n"
                   f"(Update: {datetime.now().ctime()})")

ax1.yaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
ax1.yaxis.set_ticks(arange(*ax1.get_ylim(), 1))
ax1.set_ylabel("Dates")

yticks = ax1.yaxis.get_major_ticks()
yticks[0].label1.set_visible(False)
yticks[1].label1.set_visible(False)

handles = [mpatches.Patch(color=line, label=color_picker.dict_legend[line])
           for line in color_picker.dict_legend]

ax3.legend(handles=handles, loc='upper left')

fig.tight_layout(pad=0)

ax2.axis("off")

ax3.set_xlabel("UTC Time")
ax3.set_ylabel("Light Sensor Values (lx)")

ax4.axis("off")


fig.set_size_inches(18.5, 10.5)

if args.output is None:
    plt.savefig(f"{basename(args.filename)[:4]}_plot.png", dpi=199)
else:
    plt.savefig(args.output, dpi=199)
