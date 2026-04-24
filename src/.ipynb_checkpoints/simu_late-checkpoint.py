# Wrapper and additional functions for OpenBerg
# Derived from Lia's code from phd work

from src.utils import *

# INPUT: Name mapping and pre-defined input
inputmapping =  {#Ocean and sea ice models
        'topaz4':{'ref':'cmems_mod_arc_phy_my_topaz4_P1D-m','type':'url'},
        'topaz5':{'ref':'cmems_mod_glo_phy_anfc_0.083deg_PT1H-m','type':'url'},
        'mercator':{'ref':'cmems_mod_glo_phy_anfc_0.083deg_PT1H-m','type':'url'},
        'glorys':{'ref':'cmems_mod_glo_phy_my_0.083deg_P1D-m','type':'url'},
        #sea ice models
        'nextsimanfc':{'ref':'cmems_mod_arc_phy_anfc_nextsim_hm','type':'url'},
        'nextsim':{'ref':'cmems_mod_arc_phy_my_nextsim_P1D-m','type':'url'},
        #Wave models 
        'arcmfcwam':{'ref':'dataset-wam-arctic-1hr3km-be','type':'url'},
        'arcmfcwamhind':{'ref':'cmems_mod_arc_wav_my_3km_PT1H-i','type':'url'},
        'mfwam':{'ref':'cmems_mod_glo_wav_anfc_0.083deg_PT3H-i','type':'url'},
        'waverys':{'ref':'cmems_mod_glo_wav_my_0.2deg_PT3H-i','type':'url'},
        #Mercator ocean model also supplies waves
        #Wind models
        'era5':{'ref':None,'type':'file','standard_name_mapping':{'u10':'x_wind','v10':'y_wind'},'name':'ERA5-Reader'},
        'carra':{'ref':None,'type':'file','standard_name_mapping':{'u10':'x_wind','v10':'y_wind'},'name':'CARRA-Reader'}}

def simu_late(dict_in={'config':{},'input':['topaz4',],'seed':{},'run':{}}):
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
    import sys
    # DEFINITIONS
    path_env = '../input/'   #Directory for input read from local files
    path_res = '../results/' #Directory to save results in
    # LOGGING DEFINITIONS
    logfile = False if 'logfile' not in dict_in['run'].keys() else dict_in['run']['logfile']
    loglevel = dict_in['run']['loglevel'] if 'loglevel' in dict_in['run'] else 10
    # INITIALISATION
    o = OpenBerg(loglevel=50 if 'loglevel' not in dict_in['run'] else dict_in['run']['loglevel'], 
                 logfile='../results/%s.log'%dict_in['simulationname'] if logfile!=False else None) 
    # MORE LOGGING
    logger = logging.getLogger('opendrift')
    for h in logger.handlers:
        h.setLevel(logging.DEBUG)   # or INFO
    logger.setLevel(logging.DEBUG)
    logger.info("This will now appear in the logfile")
    # SET MODEL CONFIGURATIONS
    for ck in dict_in['config'].keys(): o.set_config(ck,dict_in['config'][ck])

    # INPUT AND READERS
    #Define which input will be used
    input_used = {} #dict of input that will be used in simulations and its mapping (where needed)
    for inp in dict_in['input']:
        if type(inp)==str and inp in inputmapping: input_used[inp]=inputmapping[inp] #if dict_in[input] calls input name listed in input dict, copy given information
        elif type(inp)==str and inp not in inputmapping: input_used[inp] = {'ref':inp} #if dict_in[input] unkown str, assume it is ref
        elif type(inp)==dict: 
            inpn = next(iter(inp))
            input_used[inpn] = inp[inpn] #if dict_in[input] is dict, use directly (overwrites info from input_mapping if available)
            if inpn in inputmapping: input_used[inpn] = {**inputmapping[inpn],**input_used[inpn]} #add input_mapping infromation not given by dict_in[input]
    print('Input used: ',list(input_used.keys()))    
    print(input_used)
    #url input
    input_url = [v['ref'] for v in input_used.values() if v.get('type') != 'file']
    o.add_readers_from_list(input_url) 
    #input from local files
    input_files = {k:v for k,v in input_used.items() if v.get('type') == 'file'} #dict of inputs from files
    reader_files = []
    for inpn,inp in input_files.items(): #adds readers input for input
        if inpn=='carra':
            ds_corr = xr.open_mfdataset(fn_l)
            ds_corr['longitude'] = ds_corr['longitude'] - 360
            ds_corr.u10.attrs['standard_name'] = 'x_wind'
            ds_corr.v10.attrs['standard_name'] = 'y_wind'
            r = Reader(ds_corr,standard_name_mapping=inp['standard_name_mapping'],name=inp['name'])
            ds_corr.close()
        else:
            r = Reader(inp['ref'],standard_name_mapping=inp['standard_name_mapping'],name=inp['name'])
        reader_files = reader_files+[r]
    o.add_reader(reader_files)

    # SEEDING
    # Read from dict_in['seed']. Keys: e.g. length, width, sail, draft, lat, lon, time, radius. Values should be provided as floats or arrays.
    iceberg_in = dict_in.get('seed', {})
    iceberg_in = calc_iceberg_size(iceberg_in) #add missing iceberg sizes
    o.seed_elements(**iceberg_in)

    #RUN SIMULATIONS 
    dict_run = {'outfile':'../results/%s.nc'%dict_in['run']['simulationname'] if 'simulationname' in dict_in['run'] else 'results'} #name of output file of results
    if 'duration' in dict_in: dict_run['duration'] = dict_in['run']['duration'] 
    if 'time_step' in dict_in: dict_run['time_step'] = dict_in['run']['time_step'] #simulation (NOT OUTPUT) time steps
    oi = o.run(**dict_run) 

    # CHECK SEEDING, MODEL SETTINGS and INPUT:
    check_simulation_results(oi, dict_in,logger) #Prints if something is wrong
    
    print('\a')
    return o
    #You may also ouput oi, that is the simulation output (including model settings and input) in form of a dataset.

#e.g. o1 = simu_late(dict_in) and dict_in = {'config':{'drift:current_drag':True},'input':['cmems_mod_arc_phy_anfc_6km_detided_PT1H-i',],'seed':{'length':100,'n':1,'duration':1'}}

# MORE FUNCTIONS
def calc_iceberg_size(iceberg_in1):
    '''Correct iceberg size not supplied with empirical relations before seeding iceberg.
    '''
    lengths = iceberg_in1['length']
    if 'length' in iceberg_in1 and 'width' not in iceberg_in1:
        iceberg_in1['width'] = 0.7*lengths*np.exp(-0.00062*length)
    if 'length' in iceberg_in1 and np.logical_or('draft' not in iceberg_in1,'sail' not in iceberg_in1):
        rho_i, rho_w = 900,1027 #kg/m3
        height = np.array(0.3*lengths*np.exp(-0.00062*lengths))
        if 'draft' not in iceberg_in1:  iceberg_in1['draft'] = height*(rho_i/rho_w)
        if 'sail' not in iceberg_in1:  iceberg_in1['sail'] = height*(1-rho_i/rho_w) 
    return iceberg_in1

# CHECKS
def check_simulation_results(oi_in, dict_in_in, logger):
    '''
    Checks if icebrg seeding, model configurations and variable reading worked correctly.
    '''
    logger.info('Performing checks..')
    #Checks model configurations
    for c in dict_in_in['config']:
        if 'seed' in c: test = abs(dict_in_in['config'][c]-oi_in[c.split(':')[1]][:,0].values[0])>0.01 #Some configurations can be accessed as dataset variables
        else: test = str(dict_in_in['config'][c])==str(oi_in.attrs['config_'+c]) #Some configurations can be accessed as attributes
        if test==True: print('Checks: ',c,' not defined corretly in the model: ',dict_in_in['config'][c],oi_in.attrs['config_'+c])
    #Checks if iceberg(s) were seeded correctly
    for s in dict_in_in['seed']:
        if s not in ('number','time','radius'): 
            test = np.any(np.abs(dict_in_in['seed'][s]-oi_in[s][:,0].values)>0.01)
            if test==True: print('Checks: ',s,' not seeded correctly, difference: ',np.abs(dict_in_in['seed'][s]-oi_in[s][:,0].values))
    #Checks if input variables were read (if Readers worked)
    #list of mmost important input variables
    v_l = ['x_sea_water_velocity',  'y_sea_water_velocity', 'x_wind', 'y_wind',  'sea_water_temperature', 'sea_water_salinity', 
           'sea_ice_area_fraction','sea_ice_thickness', 'sea_ice_x_velocity', 'sea_ice_y_velocity','sea_surface_wave_stokes_drift_x_velocity', 'sea_surface_wave_stokes_drift_y_velocity',] #'sea_surface_wave_significant_height', 'sea_surface_wave_from_direction',  
    test=np.all(oi_in[v_l] == 0) #checks all variable arrays  at once
    for v in v_l: 
        if test[v]==True: print('Checks: ',v, 'NOT imported!') #print warning if variable all zero
    logger.info('Checks done.')
    return

#Note: Calling attributes and variables from Openberg at different stages:
    #before running: o.get_configspec()['seed:length']
    #after running: o.elements or o.get_property('sail') or o1.sail or o1.attrs['config_seed:length']