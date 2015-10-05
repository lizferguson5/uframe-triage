#uframe-triage

Set of python modules and scripts for analysis of UFrame ingestion performance

##Introduction/Background

We have developed a set of python scripts and modules for monitoring ingestion of instrument data into the UFrame data server for the [Ocean Observatories Cyberinfrastructure](http://oceanobservatories.org/) project.  The goal of the tools is to decrease the amount of time required to quantify the success of data being ingested into UFrame.

##Contents

- [Triage Process](#triage-process): steps involved for proper analysis of the UFrame data ingestion process
- [Tools](#tools)
- [Typical Usage](#usage): script and module usage

###Triage Process

The following is the current triage plan:

1. Ingest a representative set of data for a designated platform on a test UFrame server.
2. Parse the edex diagnostic logs generated from the ingestion and store the resulting data structure as a [JSON](http://json.org/) object.
3. Query the resulting JSON data structure, using the scripts provided, to provide lists of file completely processed/ingested, completely processed/ingested with one or more parser errors and incompletely processed/ingested files.
4. Interrogate the UFrame web-services API for the ingested platform to provide lists of all streams and parameters available as as a result of the ingestion.

###Tools
The toolbox contains the following top-level scripts:
- parse_edex_decoder-performance.py: parses a number (currently upto 2) edex diagnostic logs to create a data structure mapping the ingested file name to all aspects of ingestion.  The resulting JSON data structure is printed to [standard out](https://en.wikipedia.org/wiki/Standard_streams#Standard_output_.28stdout.29), which is then typically redirected to a text file.
- inspect_ingest_performance.py: load the JSON data structure created from parse_edex_decoder-performanc.py and query the resulting data structure on ingestion performance.

###Usage

<b>Important:</b> The scripts below require a properly configured python environment.  For the servers doing triage ingestion, this installation is found in:

    > /home/asadev/python27
    
Import the correct python environment by sourcing the getenv.sh script:

    > source /home/asadev/python27/getenv.sh
    
Ingestion of a representative platform dataset into UFrame creates a series of log files containing a variety of diagnostic information on the ingestion process.  Given that the sizes of these files can be fairly large (20 - 700Mb), parsing these files on the fly and interrogating the results is prohibitive to actually getting any work done.  Currently, the triage process involves parsing the following 2 edex log files:

- edex-ooi-dataset_decoder*.log: this log file maps a file name queued up for ingestion to the parser used for decoding/parsing.  Each file is assigned a unique [Universally Unique Identifier](https://en.wikipedia.org/wiki/Universally_unique_identifier), which can then be used to link the file to information contained in other edex log files.
- edex-ooi-ingest-performance*.log: this file logs information on the file parsing/ingestion process including the number of resulting data records created from the ingestion provided the files is completely ingested.  In the event that an error occurred during the parsing process, information on the error is provided.

In order to significantly speed up the interrogation/triage process based on the information in these log files, the first step is to parse the log files and create a data structure that can be quickly loaded and interrogated.  This is accomplished using [parse_edex_ingest-performance.py](https://github.com/ooi-integration/uframe-triage/blob/master/parse_edex_decoder-performance.py):

    > parse_edex_ingest-performance.py -p EDEX-OOI-INGEST-PERFORMANCE.log EDEX-OOI-DATASET_DECODER.log > ingest-results.json;

Once the ingest-results.json file has been created, this file is then interrogated using [inspect_ingest_performance.py](https://github.com/ooi-integration/uframe-triage/blob/master/inspect_ingest_performance.py).  This script contains many command line options:

    > inspect_ingest_performance.py -h
    
    usage: inspect_ingest_performance.py [-h] [-c] [-a] [-e] [-p] [-d] [-v] [-r]
                                     [-u] [-i] [-s SUBSITE] [--refdes REFDES]
                                     [-q INGEST_QUEUE] [--format FILE_FORMAT]
                                     edex_json_file
                                     
    Load the specified parsed EDEX dataset decoder json file and print the names
    of all files that were not completely processed.
    
    positional arguments:
    edex_json_file        Name of edex dataset_decoder log file to parse.
    
    optional arguments:
    -h, --help            show this help message and exit
    -c, --complete        Print processed files.
    -a, --all             Print all files queued for ingestion, regardless of
                        result.
    -e, --parser_errors   Print files that threw a parser exception(s).
    -p, --particles       Print created particle diagnostics.
    -d, --parser          Print parser/decoder name.
    -v, --verbose         Print full parsed records.
    -r                    Print reference designators with filenames.
    -u                    Print reference designators only.
    -i                    Print file uuids with filenames
    -s SUBSITE, --subsite SUBSITE
                        Restrict results to the specified subsite (i.e.:
                        GI01SUMO).
    --refdes REFDES       Restrict results to the specified reference designator
                        (i.e.: CE02SHSM-SBD11-01-MOPAK0000).
    -q INGEST_QUEUE, --ingestqueue INGEST_QUEUE
                        Restrict results to the specified ingest queue (i.e.:
                        mopak-o-dcl_telemetered).
    --format FILE_FORMAT  Specify the output format for the parsed records
                        ('json' <Default> or 'csv').

The default behavior is to print the list of files which were incompletely ingested:
  
    > inspect_ingest_performance.py ingest-results.csv
  
You can also print the list of files that were completely ingested:

    > inspect_ingest_performance.py -c ingest-results.csv

Or print the list of files that were completely ingested, but threw one or more parser exceptions during the ingestion process:

    > inspect_ingest_performance.py -c --parser_errors ingest-results.csv

Be default, only the list of files is printed to </b>STDOUT</b>, but much more additional information can be added using the command line switches listed in the help documentation.
