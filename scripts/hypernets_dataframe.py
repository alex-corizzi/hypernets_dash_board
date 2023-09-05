#!/usr/bin/python3.8

from sys import exit
from datetime import datetime, date
from argparse import ArgumentParser, ArgumentTypeError
from pandas import DataFrame, read_csv, to_datetime


def valid_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as s:
        msg = "not a valid date: {0!r}".format(s)
        raise ArgumentTypeError(msg)


def basic_parser_configuration(parser):

    parser.add_argument("-f", "--filename", type=str,
                        help="Select CSV input data file.", required=True)

    parser.add_argument("-a", "--after", type=valid_date,
                        help="Data slicer (inclusive) 'after' YYYY-MM-DD")

    parser.add_argument("-b", "--before", type=valid_date,
                        help="Data slicer (inclusive) 'before' YYYY-MM-DD.")

    # TODO : change it to site name instead
    parser.add_argument("-t", "--title", type=str, default="XXYY",
                        help="Tilte for the plot.")

    parser.add_argument("-o", "--output", type=str,
                        help="Specify output name.")

    return parser


# ------------------------------------------------------------------------------

class HypernetsDataFrame(DataFrame):

    def __init__(self, filename, after=None, before=None):

        super().__init__(read_csv(filename, sep=';'))

        self['sequence_name'] = \
            self['sequence_name'].apply(lambda x: x.strip())

        self['date'] = to_datetime(self['start'], unit='s').dt.date
        self['start'] = to_datetime(self['start'], unit='s').dt.time
        self['stop'] = to_datetime(self['stop'], unit='s').dt.time

        self.sort_values(['date', 'start'], ascending=[False, True],
                         inplace=True)

        # Date selection
        if after is not None:
            after = to_datetime(after)
            print(f"Data selection 'After': {after}")
            mask = ~(self['date'] >= after.date())
            self.drop(self[mask].index, inplace=True)

        if before is not None:
            before = to_datetime(before)
            print(f"Data selection 'Before': {before}")
            mask = ~(self['date'] <= before.date())
            self.drop(self[mask].index, inplace=True)

        if len(self) == 0:
            print("Error: empty DataFrame!"
                  "(bad date selection or not fresh enough data)")
            exit(1)

        self.reset_index(inplace=True, drop=True)

        self['light'] = \
            self['light'].apply(lambda x: float(x.replace('lx', '')))

        self['temperature'] = \
            self['temperature'].apply(lambda x: float(x.replace("'C", "")))

        self['humidity'] = \
            self['humidity'].apply(lambda x: float(x.replace("% RH", "")))

        self['pressure'] = \
            self['pressure'].apply(lambda x: float(x.replace("mbar", "")))

        self['tooDarkExcept'] = self['tooDarkExcept'].apply(lambda x: int(x))

        self['serialExcept'] = self['serialExcept'].apply(lambda x: int(x))

        self['duration'] = self.apply(
                lambda x: self.compute_duration(x.start, x.stop), axis=1)

    def get_dataframe_light(self, group_by_hour=False):

        # Pre-process for 'envelop' light DataFrame
        if group_by_hour is True:
            df_light = self[["light", "start"]].sort_values(by="start")
            df_light["start"] = df_light["start"]\
                .apply(lambda x: datetime.combine(date.today(), x))

            df_light["start"] = df_light["start"].dt.floor("05T")
            df_light = df_light.groupby("start").agg(["mean", "std"])

        else:
            df_light = self[["light", "date"]].groupby("date")\
                    .agg(["mean", "std"])

        df_light["mean_min"] = \
            df_light["light"]["mean"] - df_light["light"]["std"]

        df_light["mean_min"] = df_light["mean_min"].apply(lambda x: max(0, x))

        return df_light

    @staticmethod
    def compute_duration(start, stop):
        return (stop.hour * 3600 + stop.minute * 60 + stop.second)\
             - (start.hour * 3600 + start.minute * 60 + start.second)


if __name__ == '__main__':

    parser = ArgumentParser()
    parser = basic_parser_configuration(parser)
    args = parser.parse_args()

    df = HypernetsDataFrame(args.filename, args.after, args.before)

    print(df)
