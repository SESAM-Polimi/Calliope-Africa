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

strategy = 'PHES'  #select strategy

#NB change in model_min_PH the transmission yaml depending on transmission strategy considered
    
#%% ciclo for che prende i risultati di ogni run
main_folder_Base = f'Results/PHES/Solar_share_{share}%'


# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_Base) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    
# carico risultati scenario unlimited 

#energy

    Energy_Unlim = pd.read_csv(file_path_en)


    Solar_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='PV']
    
    Solar_Energy_Unlim=Solar_Energy_Unlim.loc[:,'carrier_prod'].sum()

    OCGT_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='OCGT_pp' ]
    
    OCGT_Energy_Unlim=OCGT_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    CCGT_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='CCGT_pp' ]
    
    CCGT_Energy_Unlim=CCGT_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Steam_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='Steam_Gas_pp' ]
    
    Steam_Energy_Unlim=Steam_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    OCGT_Oil_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='OCGT_Oil_pp' ]
    
    OCGT_Oil_Energy_Unlim=OCGT_Oil_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Hydro_Large_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Hydro_Large')]
    
    Hydro_Large_Energy_Unlim=Hydro_Large_Energy_Unlim.loc[:,'carrier_prod'].sum()
  
    Hydro_Small_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Hydro_Small')]
    
    Hydro_Small_Energy_Unlim=Hydro_Small_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Bio_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Bioenergy') ]
    
    Bio_Energy_Unlim=Bio_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Wind_Large1_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Wind_Large1')]
    
    Wind_Large1_Energy_Unlim=Wind_Large1_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Wind_Large2_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Wind_Large2')]
    
    Wind_Large2_Energy_Unlim=Wind_Large2_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    Wind_Small_Energy_Unlim=Energy_Unlim.loc[(Energy_Unlim['techs']=='Wind_Small')]
    
    Wind_Small_Energy_Unlim=Wind_Small_Energy_Unlim.loc[:,'carrier_prod'].sum()
    
    ISCC_Energy_Unlim=Energy_Unlim.loc[Energy_Unlim['techs']=='ISCC_pp']
    
    ISCC_Energy_Unlim=ISCC_Energy_Unlim.loc[:,'carrier_prod'].sum()

#capacity

    Capacity_Unlim = pd.read_csv(file_path_cap)

    Wind_Capacity_Unlim=Capacity_Unlim.loc[(Capacity_Unlim['techs']=='Wind_Large2') & (Capacity_Unlim['locs']=='EGY_CN')]
    
    Wind_Capacity_Unlim=Wind_Capacity_Unlim.loc[:,'energy_cap'].sum()
    
    Wind_Capacity_Unlim=Wind_Capacity_Unlim.tolist()
    
    Solar_Capacity_Unlim=Capacity_Unlim.loc[(Capacity_Unlim['techs']=='PV') & (Capacity_Unlim['locs']=='EGY_CN')]
    
    Solar_Capacity_Unlim=Solar_Capacity_Unlim.loc[:,'energy_cap'].sum()
    
    Solar_Capacity_Unlim=Solar_Capacity_Unlim.tolist()


    # calcolo valori
    
    Solar_min=Solar_Energy_Unlim*0.99
    OCGT_min=OCGT_Energy_Unlim*0.99
    OCGT_Oil_min=OCGT_Oil_Energy_Unlim*0.99
    CCGT_min=CCGT_Energy_Unlim*0.99
    Steam_min=Steam_Energy_Unlim*0.99
    Hydro_L_min=Hydro_Large_Energy_Unlim*0.99
    Hydro_S_min=Hydro_Small_Energy_Unlim*0.99
    Bio_min=Bio_Energy_Unlim*0.99
    Wind_Large1_min=Wind_Large1_Energy_Unlim*0.99
    Wind_Large2_min=Wind_Large2_Energy_Unlim*0.99
    Wind_Small_min=Wind_Small_Energy_Unlim*0.99
    ISCC_min=ISCC_Energy_Unlim*0.99

    Solar_max=Solar_Energy_Unlim*1.01
    OCGT_max=OCGT_Energy_Unlim*1.01
    OCGT_Oil_max=OCGT_Oil_Energy_Unlim*1.01
    CCGT_max=CCGT_Energy_Unlim*1.01
    Steam_max=Steam_Energy_Unlim*1.01
    Hydro_L_max=Hydro_Large_Energy_Unlim*1.01
    Hydro_S_max=Hydro_Small_Energy_Unlim*1.01
    Bio_max=Bio_Energy_Unlim*1.01
    Wind_Large1_max=Wind_Large1_Energy_Unlim*1.01
    Wind_Large2_max=Wind_Large2_Energy_Unlim*1.01
    Wind_Small_max=Wind_Small_Energy_Unlim*1.01
    ISCC_max=ISCC_Energy_Unlim*1.01
    
    Solar_min=Solar_min.tolist()
    OCGT_min=OCGT_min.tolist()
    CCGT_min=CCGT_min.tolist()
    OCGT_Oil_min=OCGT_Oil_min.tolist()
    Steam_min=Steam_min.tolist()  
    Hydro_L_min=Hydro_L_min.tolist()
    Hydro_S_min=Hydro_S_min.tolist()
    Bio_min=Bio_min.tolist()
    Wind_Large1_min=Wind_Large1_min.tolist()
    Wind_Large2_min=Wind_Large2_min.tolist()
    Wind_Small_min=Wind_Small_min.tolist()
    ISCC_min=ISCC_min.tolist()

    Solar_max=Solar_max.tolist()
    OCGT_max=OCGT_max.tolist()
    CCGT_max=CCGT_max.tolist()
    OCGT_Oil_max=OCGT_Oil_max.tolist()
    Steam_max=Steam_max.tolist()  
    Hydro_L_max=Hydro_L_max.tolist()
    Hydro_S_max=Hydro_S_max.tolist()
    Bio_max=Bio_max.tolist()
    Wind_Large1_max=Wind_Large1_max.tolist()
    Wind_Large2_max=Wind_Large2_max.tolist()
    Wind_Small_max=Wind_Small_max.tolist()
    ISCC_max=ISCC_max.tolist()


    
    # scrivo nuovo modello

    with open('model_min_PH.yaml', 'r') as file:
        Model_new = yaml.load(file, Loader=yaml.FullLoader)
    
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['PV_Energy_min']['carrier_prod_min']['power']=Solar_min
           
    Model_new['overrides']['Energy_constraint']['group_constraints']['OCGT_Energy_min']['carrier_prod_min']['power']=OCGT_min
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Steam_Energy_min']['carrier_prod_min']['power']=Steam_min
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['CCGT_Energy_min']['carrier_prod_min']['power']=CCGT_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['OCGT_Oil_Energy_min']['carrier_prod_min']['power']=OCGT_Oil_min
         
    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_Large_Energy_min']['carrier_prod_min']['power']=Hydro_L_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_Small_Energy_min']['carrier_prod_min']['power']=Hydro_S_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Bio_Energy_min']['carrier_prod_min']['power']=Bio_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind_Large1_Energy_min']['carrier_prod_min']['power']=Wind_Large1_min

    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind_Large2_Energy_min']['carrier_prod_min']['power']=Wind_Large2_min
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind_Small_Energy_min']['carrier_prod_min']['power']=Wind_Small_min
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['ISCC_Energy_min']['carrier_prod_min']['power']=ISCC_min

    
    
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['PV_Energy_max']['carrier_prod_max']['power']=Solar_max
           
    Model_new['overrides']['Energy_constraint']['group_constraints']['OCGT_Energy_max']['carrier_prod_max']['power']=OCGT_max
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Steam_Energy_max']['carrier_prod_max']['power']=Steam_max
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['CCGT_Energy_max']['carrier_prod_max']['power']=CCGT_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['OCGT_Oil_Energy_max']['carrier_prod_max']['power']=OCGT_Oil_max
         
    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_Large_Energy_max']['carrier_prod_max']['power']=Hydro_L_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Hydro_Small_Energy_max']['carrier_prod_max']['power']=Hydro_S_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Bio_Energy_max']['carrier_prod_max']['power']=Bio_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind_Large1_Energy_max']['carrier_prod_max']['power']=Wind_Large1_max

    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind_Large2_Energy_max']['carrier_prod_max']['power']=Wind_Large2_max
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['Wind_Small_Energy_max']['carrier_prod_max']['power']=Wind_Small_max
    
    Model_new['overrides']['Energy_constraint']['group_constraints']['ISCC_Energy_max']['carrier_prod_max']['power']=ISCC_max
    
    
    
    with open('Model_new.yaml', 'w') as outfile:
        yaml.dump(Model_new, outfile, default_flow_style=False)

    # aggiorno capacità scenario
    
    
    with open('Model_config/Location_Constraints_PH_min.yaml', 'r') as file:
        Location_Constraints_PH_min = yaml.load(file, Loader=yaml.FullLoader)
    
    Location_Constraints_PH_min['locations']['EGY_CN']['techs']['Wind_Large2']['constraints']['energy_cap_equals']=Wind_Capacity_Unlim
    Location_Constraints_PH_min['locations']['EGY_CN']['techs']['PV']['constraints']['energy_cap_equals']=Solar_Capacity_Unlim
    
    with open('Model_config/Location_Constraints_PH_min_new.yaml', 'w') as outfile:
        yaml.dump(Location_Constraints_PH_min, outfile, default_flow_style=False)
    
    name=subfolder.split('-')[1][:-2]

    filename= f'PH_min-{name}MW'
    
    # runno minimizzazione
    model = calliope.Model('Model_new.yaml', scenario='Energy_constraint')
    
    model.run()
    
    model.to_csv(f'Results/PHES_size/Minimized_{strategy}_{share}%/{filename}')

