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

share = 50   #select share 

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

#energy

    Energy_Unlim = pd.read_csv(file_path_en)


    Solar1_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='PV1']
    
    Solar1_Energy_Unlim=Solar1_Energy_Unlim.loc[:,'carrier_prod'].sum()

    Solar2_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='PV2']
    
    Solar2_Energy_Unlim=Solar2_Energy_Unlim.loc[:,'carrier_prod'].sum()

    OCGT_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='OCGT_pp' ]
    
    OCGT_Energy_Unlim=OCGT_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    CSP_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='CSP_pp' ]
    
    CSP_Energy_Unlim=CSP_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Coal_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='Coal_pp' ]
    
    Coal_Energy_Unlim=Coal_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Nuclear_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='Nuclear_pp' ]
    
    Nuclear_Energy_Unlim=Nuclear_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Hydro_Dam_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Hydro_Dam')]
    
    Hydro_Dam_Energy_Unlim=Hydro_Dam_Energy_Unlim.loc[:,'carrier_prod'].sum()
  
    Hydro_Ror_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Hydro_Ror')]
    
    Hydro_Ror_Energy_Unlim=Hydro_Ror_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Hydro_pumped_open_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Hydro_pumped_open')]
    
    Hydro_pumped_open_Energy_Unlim=Hydro_pumped_open_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Bio_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Bio_pp') ]
    
    Bio_Energy_Unlim=Bio_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Wind1_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Wind1')]
    
    Wind1_Energy_Unlim=Wind1_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Wind2_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Wind2')]
    
    Wind2_Energy_Unlim=Wind2_Energy_Unlim.loc[:,'carrier_prod'].sum()
    


#capacity

    Capacity_Unlim = pd.read_csv(file_path_cap)

    Solar2_Capacity_Unlim=Capacity_Unlim.loc[Capacity_Unlim['techs']=='PV2']
    
    Solar2_Capacity_Unlim=Solar2_Capacity_Unlim.loc[:,'energy_cap'].sum()
    
    Solar2_Capacity_Unlim=Solar2_Capacity_Unlim.tolist()

    Wind2_Capacity_Unlim=Capacity_Unlim.loc[Capacity_Unlim['techs']=='Wind2']
    
    Wind2_Capacity_Unlim=Wind2_Capacity_Unlim.loc[:,'energy_cap'].sum()
    
    Wind2_Capacity_Unlim=Wind2_Capacity_Unlim.tolist()

    # calcolo valori
    
    Solar1_min=Solar1_Energy_Unlim*0.99
    Solar2_min=Solar2_Energy_Unlim*0.99
    OCGT_min=OCGT_Energy_Unlim*0.99
    Nuclear_min=Nuclear_Energy_Unlim*0.99
#    CSP_min=CSP_Energy_Unlim*0.99
    Coal_min=Coal_Energy_Unlim*0.99
    Hydro_Dam_min=Hydro_Dam_Energy_Unlim*0.99
    Hydro_Ror_min=Hydro_Ror_Energy_Unlim*0.99
    Hydro_pumped_open_min=Hydro_pumped_open_Energy_Unlim*0.99
    Bio_min=Bio_Energy_Unlim*0.99
    Wind1_min=Wind1_Energy_Unlim*0.99
    Wind2_min=Wind2_Energy_Unlim*0.99
    
    Solar1_max=Solar1_Energy_Unlim*1.01
    Solar2_max=Solar2_Energy_Unlim*1.01
    OCGT_max=OCGT_Energy_Unlim*1.01
    Nuclear_max=Nuclear_Energy_Unlim*1.01
    CSP_max=CSP_Energy_Unlim*1.01
    Coal_max=Coal_Energy_Unlim*1.01
    Hydro_Dam_max=Hydro_Dam_Energy_Unlim*1.01
    Hydro_Ror_max=Hydro_Ror_Energy_Unlim*1.01
    Hydro_pumped_open_max=Hydro_pumped_open_Energy_Unlim*1.01
    Bio_max=Bio_Energy_Unlim*1.01
    Wind1_max=Wind1_Energy_Unlim*1.01
    Wind2_max=Wind2_Energy_Unlim*1.01
  
    Solar1_min=Solar1_min.tolist()
    Solar2_min=Solar2_min.tolist()
    OCGT_min=OCGT_min.tolist()
#    CSP_min=CSP_min.tolist()
    Nuclear_min=Nuclear_min.tolist()
    Coal_min=Coal_min.tolist()  
    Hydro_Dam_min=Hydro_Dam_min.tolist()
    Hydro_Ror_min=Hydro_Ror_min.tolist()
    Hydro_pumped_open_min=Hydro_pumped_open_min.tolist()
    Bio_min=Bio_min.tolist()
    Wind1_min=Wind1_min.tolist()
    Wind2_min=Wind2_min.tolist()
#    CSP_min=CSP_min.tolist()

    Solar1_max=Solar1_max.tolist()
    Solar2_max=Solar2_max.tolist()
    OCGT_max=OCGT_max.tolist()
    CSP_max=CSP_max.tolist()
    Nuclear_max=Nuclear_max.tolist()
    Coal_max=Coal_max.tolist()  
    Hydro_Dam_max=Hydro_Dam_max.tolist()
    Hydro_Ror_max=Hydro_Ror_max.tolist()
    Hydro_pumped_open_max=Hydro_pumped_open_max.tolist()
    Bio_max=Bio_max.tolist()
    Wind1_max=Wind1_max.tolist()
    Wind2_max=Wind2_max.tolist()
#    CSP_max=CSP_max.tolist()


    
    # scrivo nuovo modello

    with open('model_min_PH.yaml', 'r') as file:
        Model_new = yaml.load(file, Loader=yaml.FullLoader)
    
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['PV1_Energy_min']['carrier_prod_min']['power']=Solar1_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['PV2_Energy_min']['carrier_prod_min']['power']=Solar2_min
         
    Model_new['overrides']['Energy_constraint']['group_constraints']['OCGT_Energy_min']['carrier_prod_min']['power']=OCGT_min
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Coal_Energy_min']['carrier_prod_min']['power']=Coal_min
    
#    Model_new['overrides']['Energy_constraint']['group_constraints']['CSP_Energy_min']['carrier_prod_min']['power']=CSP_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Nuclear_Energy_min']['carrier_prod_min']['power']=Nuclear_min
         
    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_Dam_Energy_min']['carrier_prod_min']['power']=Hydro_Dam_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_Ror_Energy_min']['carrier_prod_min']['power']=Hydro_Ror_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_PH_open_Energy_min']['carrier_prod_min']['power']=Hydro_pumped_open_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Bio_Energy_min']['carrier_prod_min']['power']=Bio_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind1_Energy_min']['carrier_prod_min']['power']=Wind1_min
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind2_Energy_min']['carrier_prod_min']['power']=Wind2_min
    

    
    
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['PV1_Energy_max']['carrier_prod_max']['power']=Solar1_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['PV2_Energy_max']['carrier_prod_max']['power']=Solar2_max
         
    Model_new['overrides']['Energy_constraint']['group_constraints']['OCGT_Energy_max']['carrier_prod_max']['power']=OCGT_max
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Coal_Energy_max']['carrier_prod_max']['power']=Coal_max
    
#    Model_new['overrides']['Energy_constraint']['group_constraints']['CSP_Energy_max']['carrier_prod_max']['power']=CSP_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Nuclear_Energy_max']['carrier_prod_max']['power']=Nuclear_max
         
    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_Dam_Energy_max']['carrier_prod_max']['power']=Hydro_Dam_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_Ror_Energy_max']['carrier_prod_max']['power']=Hydro_Ror_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_PH_open_Energy_max']['carrier_prod_max']['power']=Hydro_pumped_open_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Bio_Energy_max']['carrier_prod_max']['power']=Bio_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind1_Energy_max']['carrier_prod_max']['power']=Wind1_max
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind2_Energy_max']['carrier_prod_max']['power']=Wind2_max
    
    
    
    
    with open('Model_new.yaml', 'w') as outfile:
        yaml.dump(Model_new, outfile, default_flow_style=False)

    # aggiorno capacità scenario
    
    
    with open('Model_config/Location_Constraints_PH_min.yaml', 'r') as file:
        Location_Constraints_PH_min = yaml.load(file, Loader=yaml.FullLoader)
    
    Location_Constraints_PH_min['locations']['SA_WSTR']['techs']['PV2']['constraints']['energy_cap_equals']=Solar2_Capacity_Unlim
    Location_Constraints_PH_min['locations']['SA_CSTR']['techs']['Wind2']['constraints']['energy_cap_equals']=Wind2_Capacity_Unlim
    
    with open('Model_config/Location_Constraints_PH_min_new.yaml', 'w') as outfile:
        yaml.dump(Location_Constraints_PH_min, outfile, default_flow_style=False)
    
    name=subfolder.split('-')[1][:-2]

    filename= f'PH_min-{name}MW'    
    
    # runno minimizzazione
    model = calliope.Model('Model_new.yaml', scenario='Energy_constraint')
    
    model.run()
    
    model.to_csv(f'Results/PHES_size/Minimized_{strategy}_{share}%/{filename}')
        
