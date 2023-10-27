#!/bin/bash
# ----------------------------------------------------------------------------
# Run for Local Site
# ----------------------------------------------------------------------------

source ./update_all.cfg
source ./scripts/utils.sh

#  Make sure Output CSV folder exists
mkdir -p $csv_dir

for path_to_dirs in ${sites_paths[@]}
do
    site_name=$(basename $path_to_dirs)
    site_name=${site_name::4}
    read_config $site_name

    # Process or Not
    if [[ -n ${!process} ]] && [ "${!process}" = False ] ; then
        echo $process is ${!process} : skip!
        continue
    fi

    ./scripts/sequence_timer_all.sh $path_to_dirs
done

# ----------------------------------------------------------------------------
# Get the data from NPL / RBINS Servers
# ----------------------------------------------------------------------------
# ./get_data.sh
