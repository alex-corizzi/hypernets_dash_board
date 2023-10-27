#!/bin/bash 
# set -o nounset
# set -euo pipefail

# TODO  Refactor!

# ----------------------------------------------------------------------------
# Source Config 
# ----------------------------------------------------------------------------
config_file="./update_all.cfg"
path_to_dirs=$1

if test -f $config_file ; then
      . $config_file
    if [ $? -eq 0 ]; then
        echo "Config Loaded!"
    else
        echo "Invalid or no existing Config file!"
        exit 1
    fi
fi

# ---------------------------------------------------------------------
# TODO : Let-s define some default values here
# ---------------------------------------------------------------------

name_site=$(echo $path_to_dirs | rev | cut -d'/' -f2 | rev)

path_to_logs="${path_to_dirs%/}/LOGS/"
path_to_data="${path_to_dirs%/}/DATA/"

if [ $write_stdout -eq 0 ]; then
    output="${csv_dir}${name_site}_data.csv"
else
    output=/dev/stdout
fi

if [ "$verbose" -eq 1 ] ; then
    echo "# -------------------------------------------------------"
    echo "# PATH: $path_to_dirs"
    echo "# SITE: $name_site"
    echo "# DATA: $path_to_data"
    echo "# LOGS: $path_to_logs"
    echo "# OUTP: $output"
    echo "# BTWN: $after and $before"
    echo "# -------------------------------------------------------"
fi

    # -------------------------------------------------------------------------
    # Write header + creation of the output file
    echo -n "sequence_name;start;stop;nb_spe;nb_img" > $output

    if [ "$extract_meteo" -eq 1 ] ; then
        echo -n ";temperature;humidity;pressure;light" >> $output
    fi

    if [ "$extract_rain" -eq 1 ] ; then
        echo -n ";rainDetected;rainTotal" >> $output
    fi

    if [ "$extract_yocto_rtc" -eq 1 ] ; then
        echo -n ";yoctoOffset" >> $output
    fi

    if [ "$extract_too_dark" -eq 1 ] ; then
        echo -n ";tooDarkExcept" >> $output
    fi

    if [ "$extract_serial_bug" -eq 1 ] ; then
        echo -n ";serialExcept" >> $output
    fi

    echo >> $output
    # -------------------------------------------------------------------------

    for f in $(find "$path_to_logs" -name ${year_to_process}*sequence*log); do

        D=$(echo "${f: -28: -13}" | cut -d'-' -f1-3)
        T=$(echo "${f: -28: -13}" | cut -d'-' -f4)
        dt_log=$(date -d "$D ${T:0:2}:${T:2:2}" +"%s")


        if [[ ( "$before" -eq 0  ||  "$dt_log" -le "$before" ) &&
            ( "$after" -eq 0  ||  "$dt_log" -ge "$after" ) ]] ; then

        echo "$f ($dt_log) --> process"

    else
        # echo "$f ($dt_log) --> pass"
        continue
        fi

        if [ "$verbose" -eq 1 ] ; then
            echo "# $f"
            echo "# Log DateTime: ${f: -28: -13}"
        fi

        sequenceName=$(grep -m1 "CUR" $f)
        sequenceName=$(echo "$sequenceName" | cut -d'/' -f2 | cut -d ' ' -f1)
        sequenceName=$(echo "SEQ${sequenceName:3}")

        if [[ ! -d "$path_to_data$sequenceName" ]]; then
            if [ "$verbose" -eq 1 ]; then
                echo "# Ignoring $f (no SEQ folder)" 
                echo "# --> Maybe start_sequence=off?"
            fi
            continue
        fi

        startTime_str=$(grep "Started Hypernets" $f)
        if [[ ! $? -eq 0 ]] ; then
            startTime_str=$(cat $f | head -n2 | tail -n1)
            # For MAFR:
            # startTime_str=$(grep 'deep-sleep' $f)
            if [ "$verbose" -eq 1 ]; then
                #     echo "# Ignoring $f (no start line)" 
                #     echo "# --> Incomplete log file?"
                echo "# Using second line for start time :"
                echo "# $startTime_str"
            fi
            # continue
        fi

        stopTime_str=$(grep "hypernets-sequence.service" $f)
        if [[ ! $? -eq 0 ]] ; then
            stopTime_str=$(tail $f -n1)
            if [ "$verbose" -eq 1 ]; then
                #     echo "# Ignoring $f (no stop line)" 
                #     echo "# --> Incomplete log file?"
                echo "# Using last line for stop time :"
                echo "# $stopTime_str"
            fi
            # continue
        fi

        startTime_str=${startTime_str:0:16}
        stopTime_str=${stopTime_str:0:16}

    # FIX: as we don't have the year we add it
    startTime_str="${startTime_str:0:16} ${sequenceName:3:4}"
    stopTime_str="${stopTime_str:0:16} ${sequenceName:3:4}"

    # -------------------------------------------------------
    # (dirty) FIX: for spanish / italian :
    startTime_str=$(echo $startTime_str | sed 's/ene/jan/g')
    startTime_str=$(echo $startTime_str | sed 's/gen/jan/g')
    startTime_str=$(echo $startTime_str | sed 's/abr/apr/g')
    startTime_str=$(echo $startTime_str | sed 's/mag/may/g')
    startTime_str=$(echo $startTime_str | sed 's/giu/jun/g')
    startTime_str=$(echo $startTime_str | sed 's/lug/jul/g')
    startTime_str=$(echo $startTime_str | sed 's/ago/aug/g')
    startTime_str=$(echo $startTime_str | sed 's/set/sep/g')
    startTime_str=$(echo $startTime_str | sed 's/ott/oct/g')
    startTime_str=$(echo $startTime_str | sed 's/dic/dec/g')

    stopTime_str=$(echo $stopTime_str | sed 's/ene/jan/g')
    stopTime_str=$(echo $stopTime_str | sed 's/gen/jan/g')
    stopTime_str=$(echo $stopTime_str | sed 's/abr/apr/g')
    stopTime_str=$(echo $stopTime_str | sed 's/mag/may/g')
    stopTime_str=$(echo $stopTime_str | sed 's/giu/jun/g')
    stopTime_str=$(echo $stopTime_str | sed 's/lug/jul/g')
    stopTime_str=$(echo $stopTime_str | sed 's/ago/aug/g')
    stopTime_str=$(echo $stopTime_str | sed 's/set/sep/g')
    stopTime_str=$(echo $stopTime_str | sed 's/ott/oct/g')
    stopTime_str=$(echo $stopTime_str | sed 's/dic/dec/g')
    # -------------------------------------------------------

    startTime=$(date -ud "$startTime_str" +"%s")
    stopTime=$(date -ud "$stopTime_str" +"%s")

    if [ "$verbose" -eq 1 ] ; then
        echo "# $startTime_str --> $stopTime_str ($sequenceName)"
        start_date=$(date --date "@$startTime" +"%y/%m/%d %H:%M")
        duration=$(echo $stopTime - $startTime | bc)
        echo "# $start_date: $startTime --> $stopTime ($duration s)"
    fi

    number_of_img=$(ls -1 $path_to_data$sequenceName/RADIOMETER/*jpg \
        2> /dev/null | wc -l)

    number_of_spe=$(ls -1 $path_to_data$sequenceName/RADIOMETER/*spe \
        2> /dev/null | wc -l)


    if [ "$verbose" -eq 1 ] ; then
        echo "# Number of images:  $number_of_img"
        echo "# Number of spectra: $number_of_spe"
    fi

    # Process rains sensor data
    if [ "$extract_rain" -eq 1 ] ; then
        rain_file=$(echo $f | sed "s/sequence/rain/g")
        if [ ! -f "$rain_file" ]; then
            if [ "$verbose" -eq 1 ]; then
                echo "# No rain sensor file!"
            fi
            rain='0; 0'
        else
            nb_rain_yes=$(grep -c "Read value 1" $rain_file)
            nb_rain_total=$(grep -c "Read value" $rain_file)

            rain=$(echo "$nb_rain_yes ; $nb_rain_total")
            if [ "$verbose" -eq 1 ]; then
                echo "# Rain sensor value : $rain"
            fi
        fi
    fi

    # Process Yocto RTC
    if [ "$extract_yocto_rtc" -eq 1 ] ; then
        time_file=$(echo $f | sed "s/sequence/time/g")
        if [ ! -f "$time_file" ]; then
            if [ "$verbose" -eq 1 ]; then
                echo "# No Yocto RTC time File!"
            fi
            time='0'
        else
            time=$(grep "Yocto RTC" $time_file)
            if [ $? -eq 0 ] ; then
                rugged_pc_time=$(echo $time | cut -d' ' -f3)
                yocto_rtc_time=$(echo $time | cut -d' ' -f10)

                offset=$(echo $(date -d"$rugged_pc_time" +"%s") - \
                    $(date -d"$yocto_rtc_time" +"%s") | bc)

                if [ "$verbose" -eq 1 ]; then
                    echo "# PC time: $rugged_pc_time Yocto RTC: $yocto_rtc_time,
                    offset=$offset"
                fi
            else
                if [ "$verbose" -eq 1 ]; then
                    echo Unable to retrieve RTC infos.
                fi
                offset=0
            fi
        fi
    fi

    # Print the data line --------------------------------------
    echo -n "$sequenceName ; $startTime ; $stopTime ; $number_of_spe ; $number_of_img" >> $output
    if [ "$extract_meteo" -eq 1 ] ; then
        meteo_file="$path_to_data$sequenceName/meteo.csv"
        if [ ! -f "$meteo_file" ]; then
            meteo="0; 0; 0; 0"
        else
            meteo=$(cat $path_to_data$sequenceName/meteo.csv)

            # FIX for meteo data 
            meteo=$(echo $meteo | sed "s/&#039;C/'C/g")
        fi
        echo -n " ; $meteo" >> $output
    fi

    if [ "$extract_rain" -eq 1 ]; then
        echo -n "; $rain" >> $output
    fi

    if [ "$extract_yocto_rtc" -eq 1 ]; then
        echo -n "; $offset" >> $output
    fi

    if [ "$extract_too_dark" -eq 1 ] ; then
        tooDarkCount=$(grep "too dark" $f -c)
        echo -n " ; $tooDarkCount" >> $output
    fi

    if [ "$extract_serial_bug" -eq 1 ] ; then
        serialException=$(grep "eSerialReadTimeout" $f -c)
        echo -n " ; $serialException" >> $output
    fi
    echo >> $output

    # ------------------------------------------------------------

    if [ "$display_integration_time" -eq 1 ] ; then
        grep -E "Integration time" $f | while read -r line
    do
        echo $line | rev | cut -d' ' -f2 | rev
    done
    fi

    if [ "$debug" -eq 1 ] ; then
        break
    fi
done

if [ "$debug" -eq 1 ] ; then
    exit 0
fi
