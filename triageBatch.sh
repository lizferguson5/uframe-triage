#! /bin/bash
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

source ${HOME}/python27/getenv.sh;

triageParseBatch.sh;
triageResultsBatch.sh;
listAvailableParameters.sh;
