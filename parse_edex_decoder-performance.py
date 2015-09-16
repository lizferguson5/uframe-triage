#!/usr/bin/env python

import re
import argparse
import sys
import os
import json
import csv

from parsers import *
from mergers import *

def main(args):
    '''Parse the specified edex dataset_decoder log for files regarding ingested files
    , create a data structure containing diagnostic information pertaining to each file
    and print the resulting data structure as a json object.'''
    
    if not os.path.exists(args.edex_log):
        sys.stderr.write('Invalid edex log specified: {:s}\n'.format(args.edex_log))
        return []
        
    files = parse_edex_dataset_decoder_log(args.edex_log)
    
    if not files:
        sys.stderr.write('No records parsed: {:s}\n'.format(args.edex_log))
        sys.stderr.flush()
        
    if args.performance_log:
        p_files = []
        if not os.path.exists(args.performance_log):
            sys.stederr.write('Invalid EDEX performance log specified: {:s}\n'.format(args.performance_log))
            sys.stderr.flush()
        else:
            # Parse the ingest_performance log
            p_files = parse_ingest_performance_log(args.performance_log)
            
        if not files:
            sys.stderr.write('No ingest performance records parsed: {:s}\n'.format(args.performance_log))
            sys.stderr.flush()
        else:
            files = merge_decoder_and_particle_performance(files, p_files)

    return files
    
if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description=main.__doc__)
    arg_parser.add_argument('edex_log',
        help='Name of edex dataset_decoder log file to parse.')
    arg_parser.add_argument('-p', '--performance_log',
        dest='performance_log',
        help='Name of edex ingest_performance log file to parse.')
    arg_parser.add_argument('--format',
        dest='file_format',
        default='json',
        help='Specify the output format for the parsed records (\'json\' <Default> or \'csv\').')
        
    parsed_args = arg_parser.parse_args()
        
    files = main(parsed_args)
    
    if not files:
        sys.exit(1)
    
    if parsed_args.file_format == 'json':
        sys.stdout.write(json.dumps(files, sort_keys=True))
    elif parsed_args.file_format == 'csv':
        stdout_writer = csv.writer(sys.stdout)
        cols = ['reference_designator',
            'ingest_queue',
            'fileName',
            'process_start_time',
            'process_end_time',
            'subsite',
            'node',
            'sensor',
            'deployment',
            'provenance_uuid',
            'parserName',
            'parserVersion',
            'decoder_start_time',
            'decoder_end_time',
            'decode_time',
            'decoder_uuid']
        stdout_writer.writerow(cols)
        
        for f in files:
            row = [f[k] for k in cols]
            stdout_writer.writerow(row)
            
    else:
        sys.stderr.write('no output format')
    
    sys.exit(0)
