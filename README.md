

![Hypernets Logo](hypernets_tools/hypernets/resources/img/logo.png)

### Setup Instructions
```
git clone https://github.com/alex-corizzi/hypernets_dash_board/
git submodule init
git submodule update
ls hypernets_tools/hypernets/hypstar/libhypstar/
cd hypernets_tools/
git submodule init
git submodule update
cd hypernets/hypstar/libhypstar/
```

### HTML Dash Board generation
```
./scripts/generate_site_or_new_location.sh
```



### Segment
```
usage: plot_segment.py [-h] -f FILENAME [-a AFTER] [-b BEFORE] [-t TITLE]
                       [-o OUTPUT]
                       [-c {water,water_bsbe,water_wruk,land_gfz,land_npl,land_coni,land_gona,land_tartu,land_lobe}]
                       [-p {deep,muted,pastel,bright,dark,colorblind}]
                       [-m {grey,black}]

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        Select CSV input data file.
  -a AFTER, --after AFTER
                        Data slicer (inclusive) 'after' YYYY-MM-DD
  -b BEFORE, --before BEFORE
                        Data slicer (inclusive) 'before' YYYY-MM-DD.
  -t TITLE, --title TITLE
                        Tilte for the plot.
  -o OUTPUT, --output OUTPUT
                        Specify output name.
  -c {water,water_bsbe,water_wruk,land_gfz,land_npl,land_coni,land_gona,land_tartu,land_lobe}, --color {water,water_bsbe,water_wruk,land_gfz,land_npl,land_coni,land_gona,land_tartu,land_lobe}
                        Choose the color picker.
  -p {deep,muted,pastel,bright,dark,colorblind}, --palette {deep,muted,pastel,bright,dark,colorblind}
                        Choose the color palette.
  -m {grey,black}, --marker {grey,black}
                        Draw start / end marker on segment
```

### Duration
```
usage: plot_duration.py [-h] -f FILENAME [-a AFTER] [-b BEFORE] [-t TITLE]
                        [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        Select CSV input data file.
  -a AFTER, --after AFTER
                        Data slicer (inclusive) 'after' YYYY-MM-DD
  -b BEFORE, --before BEFORE
                        Data slicer (inclusive) 'before' YYYY-MM-DD.
  -t TITLE, --title TITLE
                        Tilte for the plot.
  -o OUTPUT, --output OUTPUT
                        Specify output name.
```
