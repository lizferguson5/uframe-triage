#!/usr/bin/env python

import csv
import sys
import os
import argparse
import json
from parsers import parse_instrument_availability_csv


def main(args):
    '''Parse a single sheet, exported in csv format, from the Instrument Availability
    spreadsheet and print the results to STDOUT as csv records.'''
    
    if not os.path.exists(args.csv_file):
        sys.stderr.write('Invalid CSV file specified: {:s}\n'.format(args.csv_file))
        return 1
    
    instruments = parse_instrument_availability_csv(args.csv_file)
    
    if args.file_format == 'json':
        sys.stdout.write(json.dumps(instruments))
    elif args.file_format == 'csv':
        stdout_writer = csv.writer(sys.stdout)
        cols = ['instrument',
            'parser',
            'stream',
            'parameter',
            'pdID',
            'method',
            'method_type',
            'level',
            'calc']
        stdout_writer.writerow(cols)
        
        for instrument in instruments:
            
            for parameter in instrument['parameters']:
                
                parameter['instrument'] = instrument['instrument']
                
                stdout_writer.writerow([parameter[key] for key in cols])
            
    return 0
    
if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description=main.__doc__)
    arg_parser.add_argument('csv_file',
        help='Name of exported Instrument Availability CSV file to parse.')
    arg_parser.add_argument('--format',
        dest='file_format',
        default='csv',
        help='Specify the output format for the parsed records (\'csv\' <Default> or \'json\').')
        
    parsed_args = arg_parser.parse_args()
    
    #print parsed_args
         
    sys.exit(main(parsed_args))