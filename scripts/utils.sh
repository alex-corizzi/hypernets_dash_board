#!/bin/bash - 

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
