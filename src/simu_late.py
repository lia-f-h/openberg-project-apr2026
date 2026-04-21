# Wrapper and additional functions for OpenBerg
# Derived from Lia's code from phd work

from src.utils import *

#def set_config_fromdict(o_in,dict_in):   
#    ''' 
#    Applies configurations provided in a dictory 
#    instead of applying o.set_config() for every individual configuration.
#    Input: o to configure, dictionary of configurations
#    Output: o
#    '''
#    for ck in config_dict.keys(): o_in.set_config(ck,dict_in[ck])
#    return o_in

def simu_late(dict_in={'config':{},'input':['cmems_mod_arc_phy_my_topaz4_P1D-m',],'seed':{}}):
    '''
    Initialises, seedings and runs OpenBerg simulation.
    Input: Nested dictionary including:
     - dict of seeding data
     - dict of input of ocean, sea ice and atmospheric data
     - dict for configuration, e.g. {'drift:current_drag':True}
    '''
    # LOAD PACKAGES
    from opendrift.models.openberg import OpenBerg
    from opendrift.readers.reader_netCDF_CF_generic import Reader    
    # DEFINITIONS
    path_env = './input/'   #Directory for input read from local files
    path_res = './results/' #Directory to save results in
    # INITIALISATION
    o = OpenBerg(loglevel=50) 
    # CONFIG
    for ck in dict_in['config'].keys(): o.set_config(ck,dict_in['config'][ck])
    
    # READERS
    input_l = [i for i in dict_in['input'] if i[:3]!='.nc'] #readers from non-local files
    o.add_readers_from_list(input_l) 
    #input_l = [Reader(i) for i in dict_in['input'] if i[:3]=='.nc'] #readers from local files (requires extra step)
    #o.add_reader(input_l) #--> add functionality to supply name mapping
    
    # SEEDING
    # Read from dict_in['seed']. Keys: e.g. length, width, sail, draft, lat, lon, time, radius. Values should be provided as floats or arrays.
    #iceberg = {}
    #if 'seed' in dict_in.keys():
    #    if 'length' in dict_in['seed']: iceberg['length']=dict_in['seed']['length']
    #    if 'width' in dict_in['seed']: iceberg['width']=dict_in['seed']['width']
    #    if 'sail' in dict_in['seed']: iceberg['sail']=dict_in['seed']['sail']
    #    if 'draft' in dict_in['seed']: iceberg['draft']=dict_in['seed']['draft']

    #    if 'lat' in dict_in['seed']: iceberg['lat']=dict_in['seed']['lat']
    #    if 'lon' in dict_in['seed']: iceberg['lon']=dict_in['seed']['lon']
    #    if 'time' in dict_in['seed']: iceberg['time']=dict_in['seed']['time']
            
    #    if 'radius' in dict_in['seed']: iceberg['radius']=dict_in['seed']['radius']
    iceberg_in = dict_in.get('seed', {})
    #if iceberg['length'].size>1: iceberg['number']= iceberg['length'].size
    o.seed_elements(**iceberg_in)
        
    #RUN SIMULATIONS 
    if 'duration' in dict_in['more']: simulation_days = dict_in['more']['duration'] # Simulation time in days. Negative sign causes backwards simulation.
    oi = o.run(duration=timedelta(days=simulation_days))

    return o,oi

#e.g. o1 = simu_late(dict_in) and dict_in = {'config':{'drift:current_drag':True},'input':['cmems_mod_arc_phy_anfc_6km_detided_PT1H-i',],'seed':{'length':100,'n':1,'duration':1'}}