import os
import sys
import json
from copy import deepcopy

def merge_decoder_and_particle_performance(edex_decoder_obj, edex_particle_obj):
    '''Merges the keys from each entry in edex_decoder_obj and edex_particle_obj
    using the edex_particle_obj['particle_uuid'] and edex_decoder_obj['decoder_uuid']
    keys.
    
    Parameters:
        edex_decoder_obj: object returned by parsers.parse_edex_dataset_decoder_log
        edex_particle_obj: object returned by parsers.parse_edex_ingest_performance_log
        
    Returns:
        Array of merged dictionaries representing ingested files
    '''
    
    particle_uuids = [p['particle_uuid'] for p in edex_particle_obj]
    
    merged = []
    for f in edex_decoder_obj:
        
        m = deepcopy(f)
        
        num_particles = 0
        particle_ingest_time = -1
        if m['decoder_uuid'] in particle_uuids:
            i = particle_uuids.index(f['decoder_uuid'])
            num_particles = edex_particle_obj[i]['num_particles']
            particle_ingest_time = edex_particle_obj[i]['particle_ingest_time']
        
        m['num_particles_ingested'] = num_particles
        m['particle_ingest_time'] = particle_ingest_time
        
        merged.append(m)
        
    return merged
        