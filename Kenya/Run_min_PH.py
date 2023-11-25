# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 16:44:46 2022

@author: baioc
"""
##################### MODEL RUN TO CALCULATE PHES SIZE ##################################à

import calliope
import pandas as pd
import yaml
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker


try:
    calliope.set_log_level('INFO')
except:
    calliope.set_log_verbosity('Error')
 
#%%

share = 50   #select share 

strategy = 'PHES'  #select strategy name

#NB change in model_min_PH the transmission yaml depending on transmission strategy considered
    
#%% ciclo for che prende i risultati di ogni run

main_folder_Base = f'Results/{strategy}/Solar_share_{share}%'


# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_Base) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
        

    #energy

    Energy_Unlim = pd.read_csv(file_path_en)

    
    Diesel_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='Diesel_Engine' ]
    
    Diesel_Energy_Unlim=Diesel_Energy_Unlim.loc[:,'carrier_prod'].sum()
        
    Solar_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='PV1']
    
    Solar_Energy_Unlim=Solar_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    OCGT_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='OCGT_Oil_pp' ]
    
    OCGT_Energy_Unlim=OCGT_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Geo_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='Geothermal' ]
    
    Geo_Energy_Unlim=Geo_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    HFO_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='HFO_pp' ]
    
    HFO_Energy_Unlim=HFO_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Hydro_Large1_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Hydro_Large1')]
    
    Hydro_Large1_Energy_Unlim=Hydro_Large1_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Hydro_Large2_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Hydro_Large2')]
    
    Hydro_Large2_Energy_Unlim=Hydro_Large2_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Hydro_Large3_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Hydro_Large3')]
    
    Hydro_Large3_Energy_Unlim=Hydro_Large3_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Hydro_Large4_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Hydro_Large4')]
    
    Hydro_Large4_Energy_Unlim=Hydro_Large4_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Hydro_Small1_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Hydro_Small1')]
    
    Hydro_Small1_Energy_Unlim=Hydro_Small1_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Bio_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Bioenergy') ]
    
    Bio_Energy_Unlim=Bio_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Wind1_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Wind1') & (Energy_Unlim['locs']=='KEN_NBOR')]
    
    Wind1_Energy_Unlim=Wind1_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Wind2_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Wind2')]
    
    Wind2_Energy_Unlim=Wind2_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Wind3_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Wind3')]
    
    Wind3_Energy_Unlim=Wind3_Energy_Unlim.loc[:,'carrier_prod'].sum()

    Wind4_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Wind1') & (Energy_Unlim['locs']=='KEN_MTKR')]
    
    Wind4_Energy_Unlim=Wind4_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
#capacity

    Capacity_Unlim = pd.read_csv(file_path_cap)

    Wind_Capacity_Unlim=Capacity_Unlim.loc[(Capacity_Unlim['techs']=='Wind1') & (Capacity_Unlim['locs']=='KEN_MTKR')]
    
    Wind_Capacity_Unlim=Wind_Capacity_Unlim.loc[:,'energy_cap'].sum()
    
    Wind_Capacity_Unlim=Wind_Capacity_Unlim.tolist()

    Solar_Capacity_Unlim=Capacity_Unlim.loc[(Capacity_Unlim['techs']=='PV1') & (Capacity_Unlim['locs']=='KEN_WSTR')]
    
    Solar_Capacity_Unlim=Solar_Capacity_Unlim.loc[:,'energy_cap'].sum()
    
    Solar_Capacity_Unlim=Solar_Capacity_Unlim.tolist()
    # calcolo valori
    
    Solar_min=Solar_Energy_Unlim*0.99
    Diesel_min=Diesel_Energy_Unlim*0.99
    OCGT_min=OCGT_Energy_Unlim*0.99
    Geo_min=Geo_Energy_Unlim*0.99
    HFO_min=HFO_Energy_Unlim*0.99
    Hydro_L1_min=Hydro_Large1_Energy_Unlim*0.99
    Hydro_L2_min=Hydro_Large2_Energy_Unlim*0.99
    Hydro_L3_min=Hydro_Large3_Energy_Unlim*0.99
    Hydro_L4_min=Hydro_Large4_Energy_Unlim*0.99
    Hydro_S1_min=Hydro_Small1_Energy_Unlim*0.99
    Bio_min=Bio_Energy_Unlim*0.99
    Wind1_min=Wind1_Energy_Unlim*0.99
    Wind2_min=Wind2_Energy_Unlim*0.99
    Wind3_min=Wind3_Energy_Unlim*0.99
    Wind4_min=Wind4_Energy_Unlim*0.99

    Solar_max=Solar_Energy_Unlim*1.01
    Diesel_max=Diesel_Energy_Unlim*1.01
    OCGT_max=OCGT_Energy_Unlim*1.01
    Geo_max=Geo_Energy_Unlim*1.01
    HFO_max=HFO_Energy_Unlim*1.01
    Hydro_L1_max=Hydro_Large1_Energy_Unlim*1.01
    Hydro_L2_max=Hydro_Large2_Energy_Unlim*1.01
    Hydro_L3_max=Hydro_Large3_Energy_Unlim*1.01
    Hydro_L4_max=Hydro_Large4_Energy_Unlim*1.01
    Hydro_S1_max=Hydro_Small1_Energy_Unlim*1.01
    Bio_max=Bio_Energy_Unlim*1.01
    Wind1_max=Wind1_Energy_Unlim*1.01
    Wind2_max=Wind2_Energy_Unlim*1.01
    Wind3_max=Wind3_Energy_Unlim*1.01
    Wind4_max=Wind4_Energy_Unlim*1.01
    
    
    Solar_min=Solar_min.tolist()
    Diesel_min=Diesel_min.tolist()
    OCGT_min=OCGT_min.tolist()
    Geo_min=Geo_min.tolist()
    HFO_min=HFO_min.tolist()
    Hydro_L1_min=Hydro_L1_min.tolist()
    Hydro_L2_min=Hydro_L2_min.tolist()
    Hydro_L3_min=Hydro_L3_min.tolist()
    Hydro_L4_min=Hydro_L4_min.tolist()
    Hydro_S1_min=Hydro_S1_min.tolist()
    Bio_min=Bio_min.tolist()
    Wind1_min=Wind1_min.tolist()
    Wind2_min=Wind2_min.tolist()
    Wind3_min=Wind3_min.tolist()
    Wind4_min=Wind4_min.tolist()

    Solar_max=Solar_max.tolist()
    Diesel_max=Diesel_max.tolist()
    OCGT_max=OCGT_max.tolist()
    Geo_max=Geo_max.tolist()
    HFO_max=HFO_max.tolist()
    Hydro_L1_max=Hydro_L1_max.tolist()
    Hydro_L2_max=Hydro_L2_max.tolist()
    Hydro_L3_max=Hydro_L3_max.tolist()
    Hydro_L4_max=Hydro_L4_max.tolist()
    Hydro_S1_max=Hydro_S1_max.tolist()
    Bio_max=Bio_max.tolist()
    Wind1_max=Wind1_max.tolist()
    Wind2_max=Wind2_max.tolist()
    Wind3_max=Wind3_max.tolist()
    Wind4_max=Wind4_max.tolist()

    
    # scrivo nuovo modello

    with open('model_min_PH.yaml', 'r') as file:
        Model_new = yaml.load(file, Loader=yaml.FullLoader)
    
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['PV_Energy_min']['carrier_prod_min']['power']=Solar_min
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Diesel_Energy_min']['carrier_prod_min']['power']=Diesel_min
       
    Model_new['overrides']['Energy_constraint']['group_constraints']['OCGT_Energy_min']['carrier_prod_min']['power']=OCGT_min
       
    Model_new['overrides']['Energy_constraint']['group_constraints']['Geo_Energy_min']['carrier_prod_min']['power']=Geo_min
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['HFO_Energy_min']['carrier_prod_min']['power']=HFO_min       
       
    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro1_Energy_min']['carrier_prod_min']['power']=Hydro_L1_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro2_Energy_min']['carrier_prod_min']['power']=Hydro_L2_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro3_Energy_min']['carrier_prod_min']['power']=Hydro_L3_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro4_Energy_min']['carrier_prod_min']['power']=Hydro_L4_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['HydroS1_Energy_min']['carrier_prod_min']['power']=Hydro_S1_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Bio_Energy_min']['carrier_prod_min']['power']=Bio_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind1_Energy_min']['carrier_prod_min']['power']=Wind1_min
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind2_Energy_min']['carrier_prod_min']['power']=Wind2_min
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind3_Energy_min']['carrier_prod_min']['power']=Wind3_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind4_Energy_min']['carrier_prod_min']['power']=Wind4_min
    
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['PV_Energy_max']['carrier_prod_max']['power']=Solar_max
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Diesel_Energy_max']['carrier_prod_max']['power']=Diesel_max
       
    Model_new['overrides']['Energy_constraint']['group_constraints']['OCGT_Energy_max']['carrier_prod_max']['power']=OCGT_max
       
    Model_new['overrides']['Energy_constraint']['group_constraints']['Geo_Energy_max']['carrier_prod_max']['power']=Geo_max
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['HFO_Energy_max']['carrier_prod_max']['power']=HFO_max       
       
    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro1_Energy_max']['carrier_prod_max']['power']=Hydro_L1_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro2_Energy_max']['carrier_prod_max']['power']=Hydro_L2_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro3_Energy_max']['carrier_prod_max']['power']=Hydro_L3_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro4_Energy_max']['carrier_prod_max']['power']=Hydro_L4_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['HydroS1_Energy_max']['carrier_prod_max']['power']=Hydro_S1_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Bio_Energy_max']['carrier_prod_max']['power']=Bio_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind1_Energy_max']['carrier_prod_max']['power']=Wind1_max
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind2_Energy_max']['carrier_prod_max']['power']=Wind2_max
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind3_Energy_max']['carrier_prod_max']['power']=Wind3_max
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind4_Energy_max']['carrier_prod_max']['power']=Wind4_max
    
    with open('Model_new.yaml', 'w') as outfile:
        yaml.dump(Model_new, outfile, default_flow_style=False)

    # aggiorno capacità scenario
    
    
    with open('Model_config/Location_Constraints_PH_min.yaml', 'r') as file:
        Location_Constraints_PH_min = yaml.load(file, Loader=yaml.FullLoader)
    
    Location_Constraints_PH_min['locations']['KEN_MTKR']['techs']['Wind4']['constraints']['energy_cap_equals']=Wind_Capacity_Unlim
    Location_Constraints_PH_min['locations']['KEN_WSTR']['techs']['PV1']['constraints']['energy_cap_equals']=Solar_Capacity_Unlim
    
    with open('Model_config/Location_Constraints_PH_min_new.yaml', 'w') as outfile:
        yaml.dump(Location_Constraints_PH_min, outfile, default_flow_style=False)
    
    
    name=subfolder.split('-')[1][:-2]

    filename= f'PH_min-{name}MW'
    
    # runno minimizzazione
    model = calliope.Model('Model_new.yaml', scenario='Energy_constraint')
    
    model.run()
    
    model.to_csv(f'Results/PHES_size/Minimized_{strategy}_{share}%/{filename}')
        


