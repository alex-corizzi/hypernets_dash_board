#!/bin/bash

# ----------------------------------------------------------------------------
# Source Config 
# ----------------------------------------------------------------------------
config_file="./update_all.cfg"

if test -f $config_file ; then
      . $config_file
    if [ $? -eq 0 ]; then
        echo "Config Loaded!"
    else
        echo "Invalid or no existing Config file!"
        exit 1
    fi
fi

echo "Output directory is: $html_out"
read -p "Continue? (y/n)" -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 0
fi

if ! test -d $html_out ; then
    echo "$html_out does not exist, creation of the website..."
    mkdir -p $html_out
    cp -r templates/* $html_out
fi
cd $html_out


read -p "Input a Hypernets site ID (four letters): " site_id
read -p "Input a Hypernets site name: " site_name

mkdir $site_id
cd $site_id

# Linking to base
ln -s ../base base 
ln -s ../base/browse.html browse.html
ln -s ../base/sub_index.html index.html
ln -s ../base/map.html map.html

mkdir custom
cd custom

# Blank Image generation to provide a name suggestion
touch ${site_id}_nice_picture.jpg

echo "Enter a location (decimal)"
read -p "Latitude:" lat
read -p "Longitude:" lon

cat > map.html << EOF
<div id="map" style="width: 80%; height: 300px;  border: 1px solid black; 
                     border-radius: 8px;  position: relative; right:-10%; left:10%;"></div>
<script>
   const map = L.map('map').setView([$lat, $lon],9);

   const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
       maxZoom: 19,
       attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
   }).addTo(map);

    // const marker = L.marker([$lat, $lon]).addTo(map);

   const circle = L.circle([$lat, $lon], {
       color: 'red',
       fillColor: '#f03',
       fillOpacity: 0.5,
       radius: 1000
   }).addTo(map);

</script>
EOF

echo $PWD
exit 0


cat > sub_title.html << EOF
<a href=..>
<h2 class="logo-title" style="font-size:4vw;" > 
    <img class="img-fluid" src="custom/${site_id}_nice_picture.jpg" 
    alt="${site_id}" width=10%> ${site_id^^} </h2> 
</a>
EOF



cat > caoursel.html << EOF
<div class="container mt-3">
    <div id="myCarousel" class="carousel slide" data-ride="carousel">

        <!-- Indicators -->
        <ul class="carousel-indicators">
            <li data-target="#myCarousel" data-slide-to="0" class="active"></li>
            <li data-target="#myCarousel" data-slide-to="1"></li>
        </ul>

        <!-- The slideshow -->
        <div class="carousel-inner">
            <div class="carousel-item active">
                <a href="raw/plot_last.png">
                    <img src="raw/plot_last.png" alt="Last Plot" width="1100" height="500">
                </a>
            </div>

            <div class="carousel-item">
                <a href="raw/duration_last.png">
                    <img src="raw/duration_last.png" alt="Duration Plot" 
                                                     width="1100" height="500">
                </a>
            </div>
        </div>

        <!--
            <div class="carousel-item">
            <img src="images/cam_sky_last.jpg" alt="Sky/Sea" width="1100" height="500">
            </div>

            <div class="carousel-item">
            <img src="images/cam_site_last.jpg" alt="Site" width="1100" height="500">
            </div>
        -->


        <!-- Left and right controls -->
        <a class="carousel-control-prev" href="#myCarousel" data-slide="prev">
            <span class="carousel-control-prev-icon"></span></a>
        <a class="carousel-control-next" href="#myCarousel" data-slide="next">
            <span class="carousel-control-next-icon"></span></a>
    </div>
</div>
EOF

cd -
mkdir raw 
cd raw
touch duration_last.png
touch plot_last.png
cd ../../

cat >> sites_list.html << EOF

<a href="$site_id">
    <figure class="figure">
        <img src="$site_id/custom/${site_id}_nice_picture.jpg"
             class="figure-img img-fluid rounded center"
             alt="${site_id^^} Picture."
             style="max-width: 50%;">
        <figcaption class="figure-caption text-center"> 
        $site_name
        </figcaption>
    </figure>
</a>
EOF
