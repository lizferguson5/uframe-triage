#!/usr/bin/env python

import argparse
import os
import sys
import json
import csv
from filters import *

def main(args):
    '''Load the specified parsed EDEX dataset decoder json file and print the
    names of all files that were not completely processed.'''
    
    if not os.path.exists(args.edex_json_file):
        sys.stderr.write('Invalid EDEX dataset decoder json file specified.\n')
        sys.stderr.flush()
        return None
        
    # Load the EDEX dataset decoder json file
    fid = open(args.edex_json_file, 'r')
    files = json.load(fid)
    fid.close()
    
    if not files:
        sys.stderr.write('File contains no ingest performance records: {:s}\n'.format(args.edex_dataset_decoder_json_file))
        sys.stderr.flush()
        return records
        
    # Make sure we have the required keys
    required_keys = ['particle_ingest_time',
        'num_particles_ingested']
    k = files[0].keys()
    if len(set(k).intersection(required_keys)) != len(required_keys):
        sys.stderr.write('Ingest performace records missing one or more required keys: {:s}\n'.format(args.edex_dataset_decoder_json_file))
        sys.stderr.flush()
        return files

    if not args.all_files:
        if args.complete:
            
            #print 'Complete'
            
            # Get processed files
            files = find_complete_processed_files(files)
            
        else:
            
            #print 'Incomplete'
            
            # Get incompletely processed files
            files = find_incomplete_processed_files(files)
        
        # Further filter the results if we're looking for files with parser errors  
        if args.parser_errors:
            
            #print 'Parser errors'
            
            files = find_parser_errors(files)
        
    # Filter by subsite
    if args.subsite:
        files = filter_files_by_subsite(files, args.subsite)
        
    # Filter by fully-qualified reference designator
    if args.refdes:
        files = filter_files_by_refdes(files, args.refdes)
        
    # Filter by ingest queue
    if args.ingest_queue:
        files = filter_files_by_ingest_queue(files, args.ingest_queue)
    
    if not files:
        return 0
        
    # Configure output
    if args.file_format == 'json':
        sys.stdout.write(json.dumps(files))
        return 0
        
    if parsed_args.file_format == 'json':
        sys.stdout.write(json.dumps(files, sort_keys=True))
    elif parsed_args.file_format == 'csv':
        stdout_writer = csv.writer(sys.stdout)
        cols = ['fileName',
            'reference_designator',
            'ingest_queue',
            'process_start_time',
            'process_end_time',
            'num_particles_ingested',
            'particle_ingest_time',
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
        stdout_writer = csv.writer(sys.stdout)  
        if args.unique_refdes:
            
            refdes = list_unique_reference_designators(files)
            for r in refdes:
                stdout_writer.writerow(r)
                
        else:
            cols = ['fileName']
            if args.print_refdes:   
                cols.append('reference_designator')
            if args.file_uuid:    
                cols.append('decoder_uuid')
            if args.particles:    
                cols.append('num_particles_ingested')
                cols.append('particle_ingest_time')
            if args.parser:
                cols.append('parserName')
                cols.append('parserVersion')
                          
            stdout_writer.writerow(cols)
            
            for f in files:
                row = [f[k] for k in cols]
                stdout_writer.writerow(row)
            
        #if args.print_refdes and args.file_uuid:
        #    for f in files:
        #        sys.stdout.write('{:s} {:s} {:s}\n'.format(f['fileName'], f['reference_designator'], f['decoder_uuid']))
        #elif args.print_refdes:
        #    for f in files:
        #        sys.stdout.write('{:s} {:s}\n'.format(f['fileName'], f['reference_designator']))
        #elif args.file_uuid:
        #    for f in files:
        #        sys.stdout.write('{:s} {:s}\n'.format(f['fileName'], f['decoder_uuid']))
        #elif args.unique_refdes:
        #    refdes = list_unique_reference_designators(files)
        #    for r in refdes:
        #        sys.stdout.write('{:s}\n'.format(r))
        #else:
        #    for f in files:
        #        sys.stdout.write('{:s}\n'.format(f['fileName']))
        
    return 0
        
    
if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description=main.__doc__)
    arg_parser.add_argument('edex_json_file',
        help='Name of edex dataset_decoder log file to parse.')
    arg_parser.add_argument('-c', '--complete',
        action='store_true',
        default=False,
        help='Print processed files.')  
    arg_parser.add_argument('-a', '--all',
        dest='all_files',
        action='store_true',
        default=False,
        help='Print all files queued for ingestion, regardless of result.')
    arg_parser.add_argument('-e', '--parser_errors',
        dest='parser_errors',
        action='store_true',
        default=False,
        help='Print files that threw a parser exception(s).')
    arg_parser.add_argument('-p', '--particles',
        dest='particles',
        action='store_true',
        help='Print created particle diagnostics.')
    arg_parser.add_argument('-d', '--parser',
        dest='parser',
        action='store_true',
        help='Print parser/decoder name.')
    arg_parser.add_argument('-v', '--verbose',
        dest='verbose',
        action='store_true',
        help='Print full parsed records.')
    arg_parser.add_argument('-r',
        dest='print_refdes',
        action='store_true',
        help='Print reference designators with filenames.\n')
    arg_parser.add_argument('-u',
        dest='unique_refdes',
        action='store_true',
        help='Print reference designators only.\n')
    arg_parser.add_argument('-i',
        dest='file_uuid',
        action='store_true',
        help='Print file uuids with filenames\n')
    arg_parser.add_argument('-s', '--subsite',
        dest='subsite',
        help='Restrict results to the specified subsite (i.e.: GI01SUMO).')
    arg_parser.add_argument('--refdes',
        dest='refdes',
        help='Restrict results to the specified reference designator (i.e.: CE02SHSM-SBD11-01-MOPAK0000).')
    arg_parser.add_argument('-q', '--ingestqueue',
        dest='ingest_queue',
        help='Restrict results to the specified ingest queue (i.e.: mopak-o-dcl_telemetered).')
    arg_parser.add_argument('--format',
        dest='file_format',
        default='stdout',
        help='Specify the output format for the parsed records (\'json\' <Default> or \'csv\').')
        
    parsed_args = arg_parser.parse_args()
    
    #print parsed_args
         
    files = main(parsed_args)