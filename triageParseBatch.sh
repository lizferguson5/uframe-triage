#! /bin/bash
#
# USAGE:
#

PATH=${PATH}:/bin:${HOME}/uframe-triage;

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
while getopts "hf" option
do
    case "$option" in
        "h")
            echo -e "$USAGE";
            exit 0;
            ;;
        "f")
            FORCE=1;
            ;;
        "?")
            echo -e "$USAGE" >&2;
            exit 1;
            ;;
    esac
done

# Remove option from $@
shift $((OPTIND-1));

TRIAGE_SOURCE_ROOT="${HOME}/triage";
TRIAGE_DEST_ROOT="${TRIAGE_SOURCE_ROOT}/results";

if [ ! -d "$TRIAGE_SOURCE_ROOT" ]
then
    echo "Invalid triage source root directory: $TRIAGE_SOURCE_ROOT" >&2;
    exit 1;
fi

if [ ! -d "$TRIAGE_DEST_ROOT" ]
then
    echo "Creating triage destination directory: $TRIAGE_DEST_ROOT" >&2;
    mkdir -m 755 $TRIAGE_DEST_ROOT;
    [ "$?" -ne 0 ] && exit 1;
fi

for d in ${TRIAGE_SOURCE_ROOT}/*
do

    [ ! -d "$d" ] && continue;

    # Strip off the deployment name to create the output file
    deployment=$(basename $d);
    echo '------------------------------------------------------------------------------';
    echo "Directory: $deployment";

    DEST_DIR="${TRIAGE_DEST_ROOT}/${deployment}";
    if [ ! -d "$DEST_DIR" ]
    then
        echo "Creating destination: $DEST_DIR";
        mkdir -m 755 $DEST_DIR;
        [ "$?" -ne 0 ] && continue;
    fi

    # Create the output file name and see if it already exists
    parsed_log="${DEST_DIR}/${deployment}.parsed.json";
    if [ -f "$parsed_log" ]
    then
        bytes=$(stat -c %s $parsed_log);
        if [ "$bytes" -gt 0 ]
        then
            if [ -n "$FORCE" ]
            then
                echo "Overwriting existing parsed results file: $parsed_log";
            else
                echo "${deployment}: Skipping existing parsed results file";
                continue;
            fi
        fi
    fi

    echo "Checking for EDEX logs: $d";

    # Find the EDEX dataset_decoder logs
    decoder_logs=$(ls $d/edex-ooi-dataset_decoder*.log 2>/dev/null);
    if [ -z "$decoder_logs" ]
    then
        echo "No dataset_decoder logs found";
        continue;
    fi
    for decoder_log in $decoder_logs
    do
        echo "Dataset decoder log: $decoder_log";

        # Pull out the timestamp on the log
        log_name=$(basename $decoder_log .log);
        ts=$(echo $log_name | awk -F- '{print $4}');
#        echo "TS: $ts";

        # Use the timestamp to figure out if we have an EDEX ingest performance log
        particle_log="${d}/edex-ooi-ingest-performance-${ts}.log";
        if [ ! -f "$particle_log" ]
        then
            echo "Missing ingest performance log: $particle_log";
            continue;
        fi

        echo "Ingest performance log: $particle_log";

        echo 'Parsing ingest logs results...';
        ts0=$(date +%s);
        parse_edex_decoder-performance.py \
            -p $particle_log \
            $decoder_log > $parsed_log;
        ts1=$(date +%s);
        deltaT=$(( ts1 - ts0 ));
        echo "${deployment}: parsed in ${deltaT} seconds";

    done

done
