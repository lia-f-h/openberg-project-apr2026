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

#def calc_iceberg_size(o):
#   '''correct iceberg size with empirical relations when only parts of the dimensions are set
#    '''
#    rho_i, rho_w = 900,1027 #kg/m3
#    lengths = o.get_configspec()['seed:length']['value']
#    cond_length = length!=o.get_configspec()['seed:sail']['length']
#    if cond_length and o.get_configspec()['seed:width']['value']==o.get_configspec()['seed:width']['default']: #if length:new, but width=default
#        widths = 0.7*lengths*np.exp(-0.00062*length)
#        o.set_config('seed:width',widths)
#    elif cond_length and np.logical_or(o.get_configspec()['seed:sail']['value']==o.get_configspec()['seed:sail']['default'],o.get_configspec()['seed:draft']['value']==o.get_configspec()['seed:draft']['default']:#if length:new, but sail or draft=default, adapt sail and draft with known relations
#        hi = np.array(0.3*lengths*np.exp(-0.00062*lengths))
#        if o.get_configspec()['seed:draft']['value']==o.get_configspec()['seed:draft']['default']: 
#            drafts = hi*(rho_i/rho_w)
#            o.set_config('seed:draft',drafts)
#        if o.get_configspec()['seed:sail']['value']==o.get_configspec()['seed:sail']['default']: 
#            sails = hi*(1-rho_i/rho_w) 
#            o.set_config('seed:sail',sails)
#    return 

def calc_iceberg_size(iceberg_in1):
    '''Correct iceberg size not supplied with empirical relations before seeding iceberg.
    '''
    lengths = iceberg_in1['length']
    if 'length' in iceberg_in1 and 'width' not in iceberg_in1:
        iceberg_in1['width'] = 0.7*lengths*np.exp(-0.00062*length)
    if 'length' in iceberg_in1 and np.logical_or('draft' not in iceberg_in1,'sail' not in iceberg_in1):
        rho_i, rho_w = 900,1027 #kg/m3
        height = np.array(0.3*lengths*np.exp(-0.00062*lengths))
        if 'draft' not in iceberg_in1:  iceberg_in1['drafts'] = height*(rho_i/rho_w)
        if 'sail' not in iceberg_in1:  iceberg_in1['sails'] = height*(1-rho_i/rho_w) 
    return iceberg_in1

# CHECKS
def check_simulation_results(oi_in, dict_in_in):
    '''
    Checks if icebrg seeding, model configurations and variable reading worked correctly.
    '''
    print('Performing checks..')
    #Checks model configurations
    for c in dict_in_in['config']:
        if 'seed' in c: test = abs(dict_in_in['config'][c]-oi_in[c.split(':')[1]][:,0].values[0])>0.01 #Some configurations can be accessed as dataset variables
        else: test = str(dict_in_in['config'][c])==str(oi_in.attrs['config_'+c]) #Some configurations can be accessed as attributes
        if test==True: print(c,' not defined corretly in the model: ',dict_in_in['config'][c],oi_in.attrs['config_'+c])
    #Checks if iceberg(s) were seeded correctly
    for s in dict_in_in['seed']:
        if s not in ('number','time'): 
            test = np.abs(dict_in_in['seed'][s]-oi_in[s][:,0].values[0])>0.01
            if test==True: print(s,' not seeded correctly, difference: ',np.abs(dict_in_in['seed'][s]-oi_in[s][:,0].values[0]))
    #Checks if input variables were read (if Readers worked)
    v_l = ['x_sea_water_velocity',  'y_sea_water_velocity', 'x_wind', 'y_wind',  'sea_water_temperature', 'sea_water_salinity', #list of mmost important input variables
           'sea_ice_area_fraction','sea_ice_thickness', 'sea_ice_x_velocity', 'sea_ice_y_velocity','sea_surface_wave_stokes_drift_x_velocity', 'sea_surface_wave_stokes_drift_y_velocity',] #'sea_surface_wave_significant_height', 'sea_surface_wave_from_direction',  
    test=np.all(oi_in[v_l] == 0) #checks all variable arrays  at once
    for v in v_l: 
        if test[v]==True: print(v, 'NOT imported!') #print warning if variable all zero
    logger.info('Checks done.')
    return

def simu_late(dict_in={'config':{},'input':['topaz4',],'seed':{},'more':{}}):
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
    # LOGGING
    logfile = False if 'logfile' not in dict_in['more'].keys() else dict_in['more']['logfile']
    if logfile!=False: 
        if 'loglevel' not in dict_in['more']: 
            dict_in['more']['loglevel']=10 
            if logfile in [10,20,50]: dict_in['more']['loglevel']=logfile
#        log_file = open('%s/out.log'%(path_res), 'w')
#        sys.stdout = log_file  # Redirects print() output
#        sys.stderr = log_file  # Redirects error messages
    # INITIALISATION
    o = OpenBerg(loglevel=50 if 'loglevel' not in dict_in['more'] else dict_in['more']['loglevel'], logfile='run.log' if logfile!=False else '') 
    logger = logging.getLogger('opendrift')
    # CONFIG
    for ck in dict_in['config'].keys(): o.set_config(ck,dict_in['config'][ck])
    #o.set_config(**dict_in['config'])
    # READERS
    inputmapping =  {'topaz4':{'ref':'cmems_mod_arc_phy_my_topaz4_P1D-m','type':'url'},
              'topaz5':{'ref':'cmems_mod_glo_phy_anfc_0.083deg_PT1H-m','type':'url'},
              'mercator':{'ref':'cmems_mod_glo_phy_anfc_0.083deg_PT1H-m','type':'url'},
              'glorys':{'ref':'cmems_mod_glo_phy_my_0.083deg_P1D-m','type':'url'},
              'nextsimanfc':{'ref':'cmems_mod_arc_phy_anfc_nextsim_hm','type':'url'},
              'nextsim':{'ref':'cmems_mod_arc_phy_my_nextsim_P1D-m','type':'url'},
              'era5':{'ref':None,'type':'file','standard_name_mapping':{'u10':'x_wind','v10':'y_wind'},'name':'ERA5-Reader'},
              'carra':{'ref':None,'type':'file','standard_name_mapping':{'u10':'x_wind','v10':'y_wind'},'name':'CARRA-Reader'}}
    #Used input
    input_used = {} #dict of input that will be used in simulations and its mapping (where needed)
    for inp in dict_in['input']:
        if type(inp)==str and inp in inputmapping: input_used[inp]=inputmapping[inp] #if dict_in[input] calls input name listed in input dict, copy given information
        elif type(inp)==str and inp not in inputmapping: input_used[inp] = {'ref':inp} #if dict_in[input] unkown str, assume it is ref
        elif type(inp)==dict: 
            inpn = next(iter(inp))
            input_used[inpn] = inp[inpn] #if dict_in[input] is dict, use directly (overwrites info from input_mapping if available)
            if inpn in inputmapping: input_used[inpn] = {**inputmapping[inpn],**input_used[inpn]} #add input_mapping infromation not given by dict_in[input]
    print('Input used: ',list(input_used.keys()))                                                                                 
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
        #print(inp['ref'],inp['standard_name_mapping'],inp['name'])
        reader_files = reader_files+[r]
    o.add_reader(reader_files)

    
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
    iceberg_in = calc_iceberg_size(iceberg_in) #add missing iceberg sizes
    #if iceberg['length'].size>1: iceberg['number']= iceberg['length'].size
    o.seed_elements(**iceberg_in)
#    o.seed_elements(lon=lon_i[i], lat=lat_i[i], number=1, radius=1, time=time_i[i], 
#                    length=o.get_configspec('seed:length')['seed:length']['value'],sail=o.get_configspec('seed:sail')['seed:sail']['value'],draft=o.get_configspec('seed:draft')['seed:draft']['value'],width=o.get_configspec('seed:width')['seed:width']['value'],
#                    water_drag_coeff=o.get_configspec('seed:water_drag_coeff')['seed:water_drag_coeff']['value'],wind_drag_coeff=o.get_configspec('seed:wind_drag_coeff')['seed:wind_drag_coeff']['value'],)
        
    #RUN SIMULATIONS 
    if 'duration' in dict_in['more']: 
        simulation_days = dict_in['more']['duration'] # Simulation time in days. Negative sign causes backwards simulation.
        oi = o.run(duration=timedelta(days=simulation_days))
    else: oi = o.run() 

    # CHECK SEEDING, MODEL SETTINGS and INPUT:
    check_simulation_results(oi, dict_in) #Prints if something is wrong
    
    # SAVE RESULTS
    #try: log_file.close()
    #except: pass
    
    print('\a')
    return o,oi

#e.g. o1 = simu_late(dict_in) and dict_in = {'config':{'drift:current_drag':True},'input':['cmems_mod_arc_phy_anfc_6km_detided_PT1H-i',],'seed':{'length':100,'n':1,'duration':1'}}

#Interessting functions
#before running
#o.get_configspec()['seed:length']
#after running
#o.elements
#o.get_property('sail')