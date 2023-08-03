
colors = ['g', 'y', 'b', 'r']

# colors = [sns.color_palette(args.palette)[2],
#           sns.color_palette(args.palette)[8],
#           sns.color_palette(args.palette)[0],
#           sns.color_palette(args.palette)[3]]

dict_legend = {colors[0]: 'All spectra; All pictures',
               colors[2]: 'All spectra; Some pictures',
               colors[1]: 'All spectra; No picture',
               colors[3]: 'Missing some spectra'}


color_modes = {"water": [(10, 6), (1, 0), (4, 0)],
               "water_bsbe": [(26, 9)],
               "water_wruk": [(18, 10)],
               "land_gfz": [(58, 3)],
               "land_npl":  [(54, 3)],
               "land_coni": [(56, 5)],
               "land_gona": [(92, 5)],
               "land_tartu": [(58, 5), (4, 0)],
               "land_lobe": [(60, 30), (58, 29)]}


def color_pickup(nb_spe, nb_img, color_mode):

    expected = color_modes[color_mode]

    if (nb_spe, nb_img) in expected:
        color = colors[0]
    elif nb_spe in [item[0] for item in expected] and nb_img == 0:
        color = colors[1]
    elif nb_spe in [item[0] for item in expected]:
        color = colors[2]
    else:
        color = colors[3]

    return color
