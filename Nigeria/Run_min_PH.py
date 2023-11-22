# -*- coding: utf-8 -*-
"""
Created on Sat Aug  12 16:44:46 2023

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

share = 100   #select share 

strategy = 'PHES'  #select strategy

#NB change in model_min_PH the transmission yaml depending on transmission strategy considered

#%%

main_folder_Base = f'Results/{strategy}/Solar_share_{share}%'  # folder path


# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_Base) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    
    # carico risultati scenario unlimited 

    # energy

    Energy_Unlim = pd.read_csv(file_path_en)

    CCGT_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='CCGT_pp' ]
    
    CCGT_Energy_Unlim=CCGT_Energy_Unlim.loc[:,'carrier_prod'].sum()
        
    Solar_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='PV']
    
    Solar_Energy_Unlim=Solar_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    OCGT_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='OCGT_pp' ]
    
    OCGT_Energy_Unlim=OCGT_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    GST_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='GST_pp' ]
    
    GST_Energy_Unlim=GST_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    HFO_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='HFO_pp' ]
    
    HFO_Energy_Unlim=HFO_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Hydro_Large_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Hydro_Large')  ]
    
    Hydro_Large_Energy_Unlim=Hydro_Large_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Hydro_Small_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Hydro_Small') ]
    
    Hydro_Small_Energy_Unlim=Hydro_Small_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Wind_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Wind')]
    
    Wind_Energy_Unlim=Wind_Energy_Unlim.loc[:,'carrier_prod'].sum()

    # capacity

    Capacity_Unlim = pd.read_csv(file_path_cap)

    Wind_Capacity_Unlim=Capacity_Unlim.loc[(Capacity_Unlim['techs']=='Wind') & (Capacity_Unlim['locs']=='NGA_E')]
    
    Wind_Capacity_Unlim=Wind_Capacity_Unlim.loc[:,'energy_cap'].sum()
    
    Wind_Capacity_Unlim=Wind_Capacity_Unlim.tolist()
    
    Solar_Capacity_Unlim=Capacity_Unlim.loc[(Capacity_Unlim['techs']=='PV') & (Capacity_Unlim['locs']=='NGA_E')]
    
    Solar_Capacity_Unlim=Solar_Capacity_Unlim.loc[:,'energy_cap'].sum()
    
    Solar_Capacity_Unlim=Solar_Capacity_Unlim.tolist()

    # calcolo valori
    
    Solar_min=Solar_Energy_Unlim*0.99
    CCGT_min=CCGT_Energy_Unlim*0.99
    OCGT_min=OCGT_Energy_Unlim*0.99
    GST_min=GST_Energy_Unlim*0.99
    HFO_min=HFO_Energy_Unlim*0.99
    Hydro_Large_min=Hydro_Large_Energy_Unlim*0.99
    Hydro_Small_min=Hydro_Small_Energy_Unlim*0.99
    Wind_min=Wind_Energy_Unlim*0.99
    
    Solar_max=Solar_Energy_Unlim*1.01
    CCGT_max=CCGT_Energy_Unlim*1.01
    OCGT_max=OCGT_Energy_Unlim*1.01
    GST_max=GST_Energy_Unlim*1.01
    HFO_max=HFO_Energy_Unlim*1.01
    Hydro_Large_max=Hydro_Large_Energy_Unlim*1.01
    Hydro_Small_max=Hydro_Small_Energy_Unlim*1.01
    Wind_max=Wind_Energy_Unlim*1.01
    
    Solar_min=Solar_min.tolist()
    CCGT_min=CCGT_min.tolist()
    OCGT_min=OCGT_min.tolist()
    GST_min=GST_min.tolist()
    HFO_min=HFO_min.tolist()
    Hydro_Large_min=Hydro_Large_min.tolist()
    Hydro_Small_min=Hydro_Small_min.tolist()
    Wind_min=Wind_min.tolist()
    
    Solar_max=Solar_max.tolist()
    CCGT_max=CCGT_max.tolist()
    OCGT_max=OCGT_max.tolist()
    GST_max=GST_max.tolist()
    HFO_max=HFO_max.tolist()
    Hydro_Large_max=Hydro_Large_max.tolist()
    Hydro_Small_max=Hydro_Small_max.tolist()
    Wind_max=Wind_max.tolist()

    # scrivo nuovo modello: aggiungo valori a overrides

    with open('model_min_PH.yaml', 'r') as file:
        Model_new = yaml.load(file, Loader=yaml.FullLoader)
    
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['PV_Energy_min']['carrier_prod_min']['electricity']=Solar_min
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['CCGT_Energy_min']['carrier_prod_min']['electricity']=CCGT_min
       
    Model_new['overrides']['Energy_constraint']['group_constraints']['OCGT_Energy_min']['carrier_prod_min']['electricity']=OCGT_min
       
    Model_new['overrides']['Energy_constraint']['group_constraints']['GST_Energy_min']['carrier_prod_min']['electricity']=GST_min
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['HFO_Energy_min']['carrier_prod_min']['electricity']=HFO_min
        
    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_Large_Energy_min']['carrier_prod_min']['electricity']=Hydro_Large_min
       
    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_Small_Energy_min']['carrier_prod_min']['electricity']=Hydro_Small_min
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind_Energy_min']['carrier_prod_min']['electricity']=Wind_min
    

    
    Model_new['overrides']['Energy_constraint']['group_constraints']['PV_Energy_max']['carrier_prod_max']['electricity']=Solar_max
        
    Model_new['overrides']['Energy_constraint']['group_constraints']['CCGT_Energy_max']['carrier_prod_max']['electricity']=CCGT_max
        
    Model_new['overrides']['Energy_constraint']['group_constraints']['OCGT_Energy_max']['carrier_prod_max']['electricity']=OCGT_max
        
    Model_new['overrides']['Energy_constraint']['group_constraints']['GST_Energy_max']['carrier_prod_max']['electricity']=GST_max
        
    Model_new['overrides']['Energy_constraint']['group_constraints']['HFO_Energy_max']['carrier_prod_max']['electricity']=HFO_max
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_Large_Energy_max']['carrier_prod_max']['electricity']=Hydro_Large_max
      
    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_Small_Energy_max']['carrier_prod_max']['electricity']=Hydro_Small_max
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind_Energy_max']['carrier_prod_max']['electricity']=Wind_max
    
    
    with open('Model_new.yaml', 'w') as outfile:
        yaml.dump(Model_new, outfile, default_flow_style=False)
        

    # aggiorno capacità scenario
    
    
    with open('Model_config/Location_Constraints_PH_min.yaml', 'r') as file:
        Location_Constraints_PH_min = yaml.load(file, Loader=yaml.FullLoader)
    
    Location_Constraints_PH_min['locations']['NGA_E']['techs']['Wind']['constraints']['energy_cap_equals']=Wind_Capacity_Unlim
    Location_Constraints_PH_min['locations']['NGA_E']['techs']['PV']['constraints']['energy_cap_equals']=Solar_Capacity_Unlim
    
    with open('Model_config/Location_Constraints_PH_min_new.yaml', 'w') as outfile:
        yaml.dump(Location_Constraints_PH_min, outfile, default_flow_style=False)

    name=subfolder.split('-')[1][:-2]

    filename= f'PH_min-{name}MW'
    
    # runno minimizzazione
    model = calliope.Model('Model_new.yaml', scenario='Energy_constraint')
    
    model.run()
    
    model.to_csv(f'Results/PHES_size/Minimized_{strategy}_{share}%/{filename}')
        
