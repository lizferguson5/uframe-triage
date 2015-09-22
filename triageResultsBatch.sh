#! /bin/bash -x
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

TRIAGE_DEST_ROOT="${HOME}/triage/results";

if [ ! -d "$TRIAGE_DEST_ROOT" ]
then
    echo "Creating triage destination directory: $TRIAGE_DEST_ROOT" >&2;
    mkdir -m 755 $TRIAGE_DEST_ROOT;
    [ "$?" -ne 0 ] && exit 1;
fi

for d in ${TRIAGE_DEST_ROOT}/*
do

    [ ! -d "$d" ] && continue;

    echo '------------------------------------------------------------------------------';
    echo "Inspecting: $d";

    for f in $(ls ${d}/*.parsed.json 2>/dev/null)
    do
	    # Strip off the deployment name to create the output file
	    parsed_base=$(basename $f .parsed.json);
	    echo "Deployment: $parsed_base";

	    DEST_DIR="${TRIAGE_DEST_ROOT}/${parsed_base}";

	    if [ ! -d "$DEST_DIR" ]
	    then
	        echo "Creating destination: $DEST_DIR";
	        mkdir -m 755 $DEST_DIR;
	        [ "$?" -ne 0 ] && continue;
	    fi

	    # Create the list of incompletely parsed files
	    out_file="${DEST_DIR}/${parsed_base}.incomplete.csv";
	    echo "Incomplete: $out_file";

	    inspect_ingest_performance.py \
	        -r \
	        $f > $out_file;

	    # Create list of completely parsed files with number of particles created
	    out_file="${DEST_DIR}/${parsed_base}.complete.csv";
	    echo "Complete: $out_file";

	    inspect_ingest_performance.py \
	        -c \
	        -p \
	        -d \
	        $f > $out_file;

	    # Create list of completely parsed files with parser errors and number of 
	    # particles created and parser name
	    out_file="${DEST_DIR}/${parsed_base}.complete-parser-errors.csv";
	    echo "Complete w/errors: $out_file";

	    inspect_ingest_performance.py \
	        -c \
	        -p \
	        -d \
	        --parser_errors \
	        $f > $out_file;

    done

done
