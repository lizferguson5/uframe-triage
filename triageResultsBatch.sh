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

TRIAGE_DEST_ROOT="${HOME}/triage/parsed";

if [ ! -d "$TRIAGE_DEST_ROOT" ]
then
    echo "Invalid triage destination directory: $TRIAGE_DEST_ROOT" >&2;
    exit 1;
fi

for f in ${TRIAGE_DEST_ROOT}/*.parsed.json
do

    [ ! -f "$f" ] && continue;

    echo '------------------------------------------------------------------------------';
    echo "Inspecting: $f";

    # Strip off the deployment name to create the output file
    parsed_base=$(basename $f .parsed.json);
    echo "Deployment: $parsed_base";

    # Create the list of incompletely parsed files
    out_file="${TRIAGE_DEST_ROOT}/${parsed_base}.incomplete.csv";
    echo "Incomplete: $out_file";

    inspect_ingest_performance.py \
        -r \
        $f > $out_file;

    # Create list of completely parsed files with number of particles created
    out_file="${TRIAGE_DEST_ROOT}/${parsed_base}.complete.csv";
    echo "Complete: $out_file";

    inspect_ingest_performance.py \
        -c \
        -p \
        -d \
        $f > $out_file;

    # Create list of completely parsed files with parser errors and number of 
    # particles created and parser name
    out_file="${TRIAGE_DEST_ROOT}/${parsed_base}.complete-parser-errors.csv";
    echo "Complete w/errors: $out_file";

    inspect_ingest_performance.py \
        -c \
        -p \
        -d \
        --parser_errors \
        $f > $out_file;

done
