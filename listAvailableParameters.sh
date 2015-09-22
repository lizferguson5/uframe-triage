#! /bin/bash --
#
# USAGE:
#

PATH=${PATH}:/bin:${HOME}/uframe-triage:${HOME}/uframe-webservices;

app=$(basename $0);

# Usage message
USAGE="
NAME
    $app - 

SYNOPSIS
    $app [h]

DESCRIPTION
    -h
        show help message
";

# Default values for options

# Process options
while getopts "h" option
do
    case "$option" in
        "h")
            echo -e "$USAGE";
            exit 0;
            ;;
        "?")
            echo -e "$USAGE" >&2;
            exit 1;
            ;;
    esac
done

# Remove option from $@
shift $((OPTIND-1));

TRIAGE_DEST_ROOT="${HOME}/triage/results";
if [ ! -d "$TRIAGE_DEST_ROOT" ]
then
    echo "Creating results directory: $TRIAGE_DEST_ROOT";
    mkdir -m 755 $TRIAGE_DEST_ROOT;
    [ "$?" -ne 0 ] && continue;
fi

UFRAME_BASE="http://$(hostname)"
echo "URL: $UFRAME_BASE";

arrays=$(get_arrays.py --baseurl $UFRAME_BASE | grep -v 'Available');
for array in $arrays
do
    echo "Array: $array";

    STREAMS_CSV="${TRIAGE_DEST_ROOT}/${array}_streams.csv";

    echo "Writing streams to: $STREAMS_CSV";

    map_uframe_datastreams.py --baseurl $UFRAME_BASE --array $array > $STREAMS_CSV;

done

