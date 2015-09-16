

def find_incomplete_processed_files(files):
    '''Return a list of files for which the edex dataset_decoder log did not 
    report either a start or end process time.
    
    Parameters:
        files - array of dictionaries created from a parsed edex dataset_decoder
            log file
    
    Returns:
        List of files for which either a process start time or process end time
        was reported
    '''
    
    return [f for f in files if not f['process_start_time'] or not f['process_end_time']]
    
def find_complete_processed_files(files):
    '''Return a list of files for which the edex dataset_decoder log reported
    both a start and end process time.
    
    Parameters:
        files - array of dictionaries created from a parsed edex dataset_decoder
            log file
    
    Returns:
        List of files for which both a process start time and process end time
        was reported
    '''
    
    return [f for f in files if f['process_start_time'] and f['process_end_time']]

def find_parser_errors(files):
    '''Return a list of files for which the edex dataset_decoder log reported
    a parser error.
    
    Parameters:
        files - array of dictionaries created from a parsed edex dataset_decoder
            log file
    
    Returns:
        List of files for which both a process start time and process end time
        was reported
    '''
    
    return [f for f in files if 'parser_error' in f.keys()]
        
def filter_files_by_subsite(files, subsite):
    
    return [f for f in files if f['subsite'] == subsite]
    
def filter_files_by_refdes(files, refdes):
    
    return [f for f in files if f['reference_designator'] == refdes]
    
def filter_files_by_parser(files, parser_name):
    
    return [f for f in files if f['parserName'] == parser_name]
    
def filter_files_by_ingest_queue(files, ingest_queue):
    
    return [f for f in files if f['ingest_queue'].find(ingest_queue) > -1]
    
def list_unique_reference_designators(files):
    
    ref_des = list(set([f['reference_designator'] for f in files if not f['reference_designator'].startswith('None')]))
    ref_des.sort()
    
    return ref_des
    
#def list_incomplete_processed_files_reference_designators(files):
#    
#    incomplete = find_incomplete_processed_files(files)
#    
#    ref_des = list(set([f['reference_designator'] for f in incomplete]))
#    ref_des.sort()
#    
#    return ref_des
