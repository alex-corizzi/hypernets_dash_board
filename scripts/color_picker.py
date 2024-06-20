
import seaborn as sns


def color_parser_configuration(parser):
    parser.add_argument("-c", "--color", type=str, help="Choose the color picker.",
                        choices=ColorPicker.color_modes.keys(), default="water")


    parser.add_argument("-p", "--palette", type=str,
                        help="Choose the color palette.",
                        choices=["deep", "muted", "pastel", "bright", "dark",
                             "colorblind"], default="deep")
    return parser


class ColorPicker(object):

    color_modes = {"water": [(10, 6), (1, 0), (4, 0)],
                   "water_bsbe": [(26, 9)],
                   "water_wruk": [(18, 10)],
                   "land_gfz": [(58, 3)],
                   "land_npl":  [(54, 3)],
                   "land_coni": [(56, 5)],
                   "land_gona": [(92, 5)],
                   "land_tartu": [(58, 5), (4, 0)],
                   "land_lobe": [(60, 30), (58, 29)]}

    def __init__(self, color_mode, palette):
        self.colors = [sns.color_palette(palette)[2],
                       sns.color_palette(palette)[8],
                       sns.color_palette(palette)[0],
                       sns.color_palette(palette)[3]]

        self.dict_legend = {self.colors[0]: 'All spectra; All pictures',
                            self.colors[2]: 'All spectra; Some pictures',
                            self.colors[1]: 'All spectra; No picture',
                            self.colors[3]: 'Missing some spectra'}

        self.expected = ColorPicker.color_modes[color_mode]

    def pickup(self, nb_spe, nb_img):

        if (nb_spe, nb_img) in self.expected:
            color = self.colors[0]
        elif nb_spe in [item[0] for item in self.expected] and nb_img == 0:
            color = self.colors[1]
        elif nb_spe in [item[0] for item in self.expected]:
            color = self.colors[2]
        else:
            color = self.colors[3]
        return color
