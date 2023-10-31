#!/usr/bin/python3.8

from os.path import basename
from argparse import ArgumentParser

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

import seaborn as sns

from scripts.hypernets_dataframe import HypernetsDataFrame
from scripts.hypernets_dataframe import basic_parser_configuration

from color_pickup import dict_legend

sns.set()
sns.set_style('darkgrid')

parser = ArgumentParser()
parser = basic_parser_configuration(parser)
args = parser.parse_args()

df = HypernetsDataFrame(args.filename, after=args.after, before=args.before)

df["datetime"] = df.apply(lambda x: datetime.combine(x.date, x.start), axis=1)
df.sort_values('datetime', ascending=True, inplace=True)

print(df)

plt.clf()


handles = [mpatches.Patch(color=line, label=dict_legend[line])
           for line in dict_legend]

nb_spe, nb_img = 58, 3
nb_spe, nb_img = 10, 6

gre = df[(df["nb_spe"] == nb_spe) & (df["nb_img"] == nb_img)]
blu = df[(df["nb_spe"] == nb_spe) & (df["nb_img"] < nb_img)]
yel = df[(df["nb_spe"] == nb_spe) & (df["nb_img"] == 0)]
red = df[(df["nb_spe"] < nb_spe)]


# TODO: color the rest in grey
# blk = df[(
# (df["nb_spe"] == nb_spe) & (df["nb_img"] == nb_img) & \
# (df["nb_spe"] == nb_spe) & (df["nb_img"] < nb_img) & \
# (df["nb_spe"] == nb_spe) & (df["nb_img"] == nb_img) & \
# (df["nb_spe"] < nb_spe))]
# print(blk)

mean_duration = df[["duration", "date"]].groupby("date").agg(["mean"])
# mean_offset = df[["yoctoOffset", "date"]].groupby("date").agg(["mean"])

df_light = df.get_dataframe_light()

fig, (ax1, ax2) = plt.subplots(2, 1, sharex='col')

ax1.plot(red["datetime"], red["duration"], ".r", alpha=.85, markeredgewidth=0)
ax1.plot(yel["datetime"], yel["duration"], ".y", alpha=.85, markeredgewidth=0)
ax1.plot(blu["datetime"], blu["duration"], ".b", alpha=.25, markeredgewidth=0)
ax1.plot(gre["datetime"], gre["duration"], ".g", alpha=.20, markeredgewidth=0)

ax1.plot(mean_duration, "purple")
# ax1.plot(mean_offset, "brown")

ax2.plot(df_light.index, df_light["light"]["mean"], "b", linewidth=1.5)

ax2.fill_between(df_light.index, df_light["mean_min"],
                 df_light["light"]["mean"] + df_light["light"]["std"],
                 color="b", alpha=0.3)

ax1.set_title(f"{basename(args.filename)[:4]}: over last months\n"
              f"(Update: {datetime.now().ctime()})", fontsize=8)

ax1.set_ylabel("Duration (s)", fontsize=8)
ax1.yaxis.tick_right()
ax1.legend(handles=handles, loc='upper right', fontsize=5)
ax1.tick_params(labelsize=6)

ax2.set_ylabel("Light Sensor Values (lx)", fontsize=8)
ax2.yaxis.tick_right()

ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b.%y"))
ax2.tick_params(labelsize=6)
# ax2.invert_yaxis()
ax2.xaxis.tick_top()

if args.output is None:
    fig.savefig(f"{basename(args.filename)[:4]}_duration.png",
                bbox_inches='tight', dpi=199)
else:
    fig.savefig(args.output, bbox_inches='tight', dpi=199)
