#!/bin/bash
# ----------------------------------------------------------------------------
# Run for Local Site
# ----------------------------------------------------------------------------

source ./update_all.cfg

#  Make sure Output CSV folder exists
mkdir -p $csv_dir

for path_to_dirs in ${sites_paths[@]}
do
    ./scripts/sequence_timer_all.sh  $path_to_dirs
done

# ----------------------------------------------------------------------------
# Get the data from NPL / RBINS Servers
# ----------------------------------------------------------------------------
# ./get_data.sh
