'''Regular expressions and routines for parsing EDEX logs'''

import re
import sys
import os
import csv

# Matches and captures:
# 1. timestamp
# 2. ingest queue
# 3. filename
start_re = re.compile(r'''(\d{4}\-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{1,})
    \s+
    \[Ingest\.(.*)\]
    \s+FileDecoder:\s+EDEX\s+\-\s+\*{1,}\s+Processing\s+file:\s+
    (.*)$''', re.X)
# Matches and captures:
# 1. timestamp
# 2. ingest queue
# 3. decoder uuid
# 4. filename
decode_start_re = re.compile(r'''(\d{4}\-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{1,})
    \s+
    \[Ingest\.(.*)\]
    \s+FileDecoder:\s+EDEX\s+\-\s+
    <(.*)>
    \s+File:\s+
    (.*)
    \s+has.*$''', re.X)
# Matches and captures
# 1. timestamp
# 2. ingest queue
# 3. subsite 
# 4. node
# 5. sensor
# 6. method
# 7. uuid
# 8. deployment
# 9. fileName
# 10. parserName
# 11. parserVersion
provenance_re = re.compile(r'''(\d{4}\-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{1,})
    \s+
    \[Ingest\.(.*)\]
    \s+FileDecoder:\s+EDEX\s+\-\s+
    Provenance\s+for\s+:\s+.*\s+is\s+Data\s+Provenance\s+
    \[pk=ProvenanceKey\s+
    \[
    subsite=(.*)
    ,\s+
    node=(.*)
    ,\s+
    sensor=(.*)
    ,\s+
    method=(.*)
    ,\s+
    uuid=(.*)
    ,\s+
    deployment=(\d{1,})
    \]
    ,\s+
    fileName=(.*)
    ,\s+
    parserName=(.*)
    ,\s+
    parserVersion=(.*)
    \]$''', re.X)
# Matches and captures:
# 1. timestamp
# 2. ingest queue
# 3. uuid
# 4. parse time
decode_end_re = re.compile(r'''(\d{4}\-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{1,})
    \s+
    \[Ingest\.(.*)\]
    \s+FileDecoder:\s+EDEX\s+\-\s+FileDecoder\s+finished\s+
    (\w{8,}\-\w{4,}\-\w{4,}\-\w{4,}\-\w{12,})
    \s+in\s+
    (\d{1,})''', re.X)
# Matches and captures:
# 1. timestamp
# 2. ingest queue
# 3. filename
finish_re = re.compile(r'''(\d{4}\-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{1,})
    \s+
    \[Ingest\.(.*)\]
    \s+FileDecoder:\s+EDEX\s+\-\s+\*{1,}\s+Finished\s+Processing\s+file:\s+
    (.*)$''', re.X) 
# Matches and captures ERRORS with
# 1. timestamp
# 2. ingest queue
# 3. filename   
exception_re = re.compile(r'''ERROR\s+(\d{4}\-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{1,})
    \s+
    \[Ingest\.(.*)\]
    \s+FileDecoder:\s+EDEX\s+\-\s+Failure\s+in\s+using\s+parser\s+on:\s+
    (.*)$''', re.X)
    
def parse_edex_dataset_decoder_log(edex_log):
    
    files = []
    
    if not os.path.exists(edex_log):
        sys.stderr.write('Invalid EDEX dataset_decoder log: {:s}\n'.format(edex_log))
        return files
        
    fid = open(edex_log, 'r')
    
    for r in fid:
        #print 'Line: {:s}'.format(r)
        
        m = start_re.search(r)
        if m:
            tokens = m.groups()
            files.append({'fileName' : tokens[2],
                'ingest_queue' : tokens[1],
                'process_start_time' : tokens[0].replace(',', '.'),
                'process_end_time' : None,
                'decoder_start_time' : None,
                'decoder_end_time' : None,
                'decoder_uuid' : None,
                'decode_time' : None,
                'subsite' : None,
                'node' : None,
                'sensor' : None,
                'method' : None,
                'provenance_uuid' : None,
                'deployment' : None,
                'parserName' : None,
                'parserVersion' : None})
            continue
        
        m = exception_re.search(r)
        if m:
            tokens = m.groups()
            decoder_id = '{:s}-{:s}'.format(tokens[1], tokens[2])
            all_decoder_ids = ['{:s}-{:s}'.format(f['ingest_queue'], f['fileName']) for f in files]
            if decoder_id in all_decoder_ids:
                i = all_decoder_ids.index(decoder_id)
                files[i]['parser_error'] = True
                files[i]['parser_error_ts'] = tokens[0]
                
            continue
            
        m = decode_start_re.search(r)
        if m:
            tokens = m.groups()
            decoder_id = '{:s}-{:s}'.format(tokens[1], tokens[3])
            all_decoder_ids = ['{:s}-{:s}'.format(f['ingest_queue'], f['fileName']) for f in files]
            if decoder_id in all_decoder_ids:
                i = all_decoder_ids.index(decoder_id)
                files[i]['decoder_start_time'] = tokens[0].replace(',', '.')
                files[i]['decoder_uuid'] = tokens[2]
            
            continue          
            
        m = provenance_re.search(r)
        if m:
            tokens = m.groups()
            provenance_id = '{:s}-{:s}'.format(tokens[1], tokens[8])
            all_provenance_ids = ['{:s}-{:s}'.format(f['ingest_queue'], f['fileName']) for f in files]
            if provenance_id in all_provenance_ids:
                i = all_provenance_ids.index(provenance_id)
                files[i]['subsite'] = tokens[2]
                files[i]['node'] = tokens[3]
                files[i]['sensor'] = tokens[4]
                files[i]['method'] = tokens[5]
                files[i]['provenance_uuid'] = tokens[6]
                files[i]['deployment'] = tokens[7]
                files[i]['parserName'] = tokens[9]
                files[i]['parserVersion'] = tokens[10]
                
            continue
            
        m = decode_end_re.search(r)
        if m:
            tokens = m.groups()
            decoder_id = '{:s}-{:s}'.format(tokens[1], tokens[2])
            all_decoder_ids = ['{:s}-{:s}'.format(f['ingest_queue'], f['decoder_uuid']) for f in files]
            if decoder_id in all_decoder_ids:
                i = all_decoder_ids.index(decoder_id)
                files[i]['decoder_end_time'] = tokens[0].replace(',', '.')
                files[i]['decode_time'] = tokens[3]
                
            continue
            
        m = finish_re.search(r)
        if m:
            tokens = m.groups()
            file_id = '{:s}-{:s}'.format(tokens[1], tokens[2])
            all_file_ids = ['{:s}-{:s}'.format(f['ingest_queue'], f['fileName']) for f in files]
            if file_id in all_file_ids:
                i = all_file_ids.index(file_id)
                files[i]['process_end_time'] = tokens[0].replace(',', '.')
                
            continue
    
    fid.close()

    for f in files:
        f['reference_designator'] = '{:s}-{:s}-{:s}'.format(f['subsite'],
            f['node'],
            f['sensor'])
            
    return files
    
particles_re = re.compile(r'''(\d{4}\-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{1,})
    \s+
    \[Ingest\.(.*)\]
    \s+ingest:\s+PERF:\s+ParticleFactory\s+\-\s+
    <(.*)>
    \s+File:\s+
    (.*)
    \s+Status:\s+Complete\s+
    (\d{1,})
    \s+particles\s+in\s+
    (.*)\s+m?s\(
    ''', re.X)
    
def parse_ingest_performance_log(edex_log):
    
    files = []
    
    if not os.path.exists(edex_log):
        sys.stderr.write('Invalid EDEX dataset_decoder log: {:s}\n'.format(edex_log))
        return files
        
    fid = open(edex_log, 'r')
    
    for r in fid:
        
        m = particles_re.search(r)
        if m:
            tokens = m.groups()
            files.append({'fileName' : tokens[3],
                'ingest_queue' : tokens[1],
                'particle_uuid' : tokens[2],
                'particle_time' : tokens[0].replace(',', '.'),
                'num_particles' : tokens[4],
                'particle_ingest_time' : tokens[5]})
            continue
            
    fid.close()
    
    return files
    
def parse_instrument_availability_csv(csv_file):

    fid = open(csv_file, 'rU')
    csv_reader = csv.reader(fid)
    
    # Read in the first 3 rows and discard
    csv_reader.next()
    csv_reader.next()
    csv_reader.next()
    
    instruments = []
    parameter = {'parser' : None,
    'level' : None,
    'calc' : None,
    'stream' : None,
    'parameter' : None} 
    
    instrument_streams = {} 
    for r in csv_reader:
        
        if r[1] and r[2]:
            
            if instrument_streams:
                instruments.append(instrument_streams)
         
            instrument_types = re.split('\s', r[1])
            if len(instrument_types) > 1:
                instrument_type = instrument_types[1][:-1]
            else:
                instrument_type = r[1]
                  
            instrument_streams = {'instrument' : instrument_type,
                'parameters' : []}
            continue
            
        if r[3] and r[4] and r[6]:
            # True if csv line has a parser name, level and stream/parameter name
            
            if not r[7]:
                # True if there is no pdID, in which it's a stream and not a parameter
                
                stream = r[6]
                #continue
            
            method = None
            if r[9].startswith('T'):
                method = 'telemetered'
            elif r[9].startswith('RH'):
                method = 'recovered_host'
            elif r[9].startswith('RI'):
                method = 'recovered_instrument'
            elif r[9].startswith('RW'):
                method = 'recovered_wfp'
                
            parameter = {'parser' : r[3],
                'level' : r[4],
                'calc' : r[5],
                'stream' : stream,
                'parameter' : r[6],
                'method' : method,
                'method_type' : r[9],
                'pdID' : r[7]} 
                
            instrument_streams['parameters'].append(parameter)
            
    if instrument_streams:
        instruments.append(instrument_streams)
            
    return instruments