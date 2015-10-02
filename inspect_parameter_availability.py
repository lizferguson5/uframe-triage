#!/usr/bin/env python

import csv
import os
import sys
import argparse
import json

def main(args):
    
    results = validate_platform_streams(args.streams_csv,
        args.master_csv,
        method=args.method)
 
    # Dump the results as a json object   
    if args.file_format == 'json':
        sys.stdout.write(json.dumps(results))
        return 0
    
    # Otherwise, output as csv
    if args.found:
        del(results['missing'])
    elif args.notfound:
        del(results['found'])
            
    stdout_writer = csv.writer(sys.stdout)
    cols = ['reference_designator',
        'stream',
        'parameter',
        'pdID',
        'parser',
        'method',
        'level',
        'found']
    stdout_writer.writerow(cols)
    
    for x in results.keys():
        for s in results[x]:
            row = [s[k] for k in cols]
            stdout_writer.writerow(row)
    
    return 0
    
def validate_platform_streams(parameters_csv, master_csv, method=None):
    
    results = {}
    
    if not os.path.exists(parameters_csv):
        sys.stderr.write('Invalid parameters CSV file: {:s}\n'.format(parameters_csv))
        return results
    if not os.path.exists(master_csv):
        sys.stderr.write('Invalid master CSV file: {:s}\n'.format(master_csv))
        return results

    # Read in the master csv
    mfid = open(master_csv, 'rU')
    m_csv_reader = csv.reader(mfid)
    m_cols = m_csv_reader.next()
    col_indices = range(0,len(m_cols))
    master = []
    for row in m_csv_reader:
        
        master.append({m_cols[i] : row[i] for i in col_indices})
    
    mfid.close()
        
    # Read in the parameters csv
    p_csv_reader = csv.reader(open(parameters_csv, 'rU'))
    p_cols = p_csv_reader.next()
    col_indices = range(0,len(p_cols))
    parameters = []
    for row in p_csv_reader:
        
        parameters.append({p_cols[i] : row[i] for i in col_indices})
        
    if not parameters:
        return results
        
    # Filter out parameters by method
    if method:
        m_parameters = [m for m in master if m['method'].startswith(method)]
        existing_parameters = [p for p in parameters if p['method'].startswith(method)]
    else:
        m_parameters = master
        existing_parameters = parameters
    
    yes = []
    no = []
    
    instruments = list(set([m['instrument'] for m in m_parameters]))
    for instrument in instruments:
        
        platform_streams = [p for p in existing_parameters if p['reference_designator'].find(instrument[:4]) >= 0]
        master_streams = [m for m in m_parameters if m['instrument'].startswith(instrument)]
        
        for stream in master_streams:
            
            #has_stream = [s for s in platform_streams if stream['stream'] == s['stream'] and stream['parameter'] == s['parameter']]
            has_stream = [s for s in platform_streams if stream['parameter'] == s['parameter']]
            
            if has_stream:
                for s in has_stream:
                    stream['reference_designator'] = s['reference_designator']
                    stream['found'] = 1
                    yes.append(stream)
            else:
                stream['reference_designator'] = None
                stream['found'] = 0
                no.append(stream)
                
    results['found'] = yes
    results['missing'] = no
    
    return results
    
if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description=main.__doc__)
    arg_parser.add_argument('-m', '--master',
        dest='master_csv',
        required=True,
        help='Name of the master csv parameter list (REQUIRED)')
    arg_parser.add_argument('-s', '--streams',
        dest='streams_csv',
        required=True,
        help='Name of the csv parameter list to inspect (REQUIRED)')
    arg_parser.add_argument('-t', '--method',
        dest='method',
        default=None,
        help='Specify a stream method (i.e.: telemetered, recovered_host, etc.)')
    arg_parser.add_argument('-f', '--found',
        dest='found',
        action='store_true',
        help='Display only the parameters that were found')
    arg_parser.add_argument('-n', '--notfound',
        dest='notfound',
        action='store_true',
        help='Display only the parameters that were not found')
    arg_parser.add_argument('--format',
        dest='file_format',
        default='csv',
        help='Specify the output format for the parsed records (\'csv\' <Default> or \'json\').')
        
    parsed_args = arg_parser.parse_args()
    
    #print parsed_args
         
    sys.exit(main(parsed_args))