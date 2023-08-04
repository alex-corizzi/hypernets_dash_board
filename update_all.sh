#!/bin/bash
# set -o nounset
# set -euo pipefail

# ----------------------------------------------------------------------------
# Source Config 
# ----------------------------------------------------------------------------
config_file="./update_all.cfg"

# ----------------------------------------------------------------------------
printf '%0.1s' "-"{1..80} && echo
date
printf '%0.1s' "-"{1..80} && echo
# ----------------------------------------------------------------------------

if test -f $config_file ; then
      . $config_file
    if [ $? -eq 0 ]; then
        echo "Config Loaded!"
    else
        echo "Invalid or no existing Config file!"
        exit 1
    fi
fi

read_config (){
    process=${site_name}_process

    segment=${site_name}_segment
    segment_args=${site_name}_segment_args

    duration=${site_name}_duration
    duration_args=${site_name}_duration_args

    echo "Site Name: $site_name - process=${!process}"
    echo "Segment : (${!segment}) - ${!segment_args}"
    echo "Duration: (${!duration}) - ${!duration_args}"
}


# ----------------------------------------------------------------------------
# Execute pre-processing script if it is defined
# ----------------------------------------------------------------------------
if [[ -n $pre_process ]] && [[ -f $pre_process ]]; then 
    echo "Pre-processing..."
    # exec $pre_process
    bash $pre_process
    echo "End!"
else
    echo "Note: no pre-processing script is defined."
fi

# ------------------------------------------------------------------------------
# Make Plots
# ------------------------------------------------------------------------------
for f in $(find $csv_dir -name "*csv"); do 

    printf '%0.1s' "-"{1..80}
    echo
    echo "CSV File found: $f"

    site_name=$(basename $f)
    site_name=${site_name::4}

    read_config $site_name

    echo $duration

    # --------------------------------------------------------------------------
    # Process or Not 
    if [[ -n ${!process} ]] && [ "${!process}" = False ] ; then
        echo $process is ${!process} : skip!
        continue
    fi

    # --------------------------------------------------------------------------
    #  Segment Plot
    if [[ -n ${!segment} ]] && [ "${!segment}" = False ] ; then
        echo $segment is ${!segment} : skip!
    else
        echo ./scripts/plot_segment.py -f $f -t $site_name ${!segment_args} ...
        ./scripts/plot_segment.py -f $f -t $site_name ${!segment_args}

        if [ $? -eq 0 ]; then
            mv ${site_name}_plot.png ${plot_out%/}/${site_name}_plot_last.png
        else
            echo "Error!"
        fi
    fi

    # -------------------------------------------------------------------------
    # Duration Plot
    if [[ -n ${!duration} ]] && [ "${!duration}" = False ] ; then
        echo $duration is ${!duration} : skip!
    else
        ./scripts/plot_duration.py -f $f
        if [ $? -eq 0 ]; then
            mv ${site_name}_duration.png ${plot_out%/}/${site_name}_duration.png
        else
            echo "Error!"
        fi
    fi
done

# ----------------------------------------------------------------------------
# Execute post-processing script if it is defined
# ----------------------------------------------------------------------------
if [[ -n $post_process ]] && [[ -f $post_process ]]; then 
    echo "Post-processing..."
    bash $post_process
    # exec $post_process
    echo "End!"
else
    echo "Note: no post-processing script is defined."
fi
