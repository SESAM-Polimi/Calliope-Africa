# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 10:26:51 2023

@author: baioc
"""
#################### MODEL RUN #########################################

import yaml
import calliope

try:
    calliope.set_log_level('INFO')
except:
    calliope.set_log_verbosity('Error')

#%%

capacity = [50, 500, 1000, 1500, 2000, 2500, 3000] #MW

share=[0, 0.1, 0.2, 0.3, 0.4,0.5, 0.6, 0.7, 0.8, 0.9, 1]

capacity = [500, 3000] #MW

share=[0, 0.5, 1]

#%% 4 integration strategies are considered

#Renewables Only (RO): only rewables are added
#PHES: add renewables and PHES
#Transmission expansion (TE) : add transmission expansion
#PHES and transmissio expansio (PHES and TE) : add PHES and transmission expansion

#%% select transmission option

transm_opt = 0  # 0 for current transmission, 1 for expanded tranmission       

################################################
if transm_opt == 1:
    
    model_file = f'model_transmission_exp.yaml'

if transm_opt == 0:
    
    model_file = f'model_transmission.yaml'


#%%select phes option

phes_opt = 1   # 0 for no storage, 1 for storage

#################################################
if phes_opt == 1:
    
    #maximum PHES plants available
    
    PHES_cap = 33333333
    PHES_en = 200000000

if phes_opt == 0:

    PHES_cap = 0
    PHES_en = 0

#%%

for cap in capacity:
    for sh in share:
        
        cap_kW = cap * 1e3
        
        Solar_cap = sh * cap_kW
        
        Wind_cap = cap_kW - Solar_cap
        
        with open('Model_config/Location_Constraints.yaml', 'r') as file:
            Location_Constraints = yaml.load(file, Loader=yaml.FullLoader)
            
        Location_Constraints['locations']['KEN_WSTR']['techs']['PV1']['constraints']['energy_cap_equals']=Solar_cap
        Location_Constraints['locations']['KEN_MTKR']['techs']['Wind1']['constraints']['energy_cap_equals']=Wind_cap
        Location_Constraints['locations']['KEN_WSTR']['techs']['PHES']['constraints']['energy_cap_equals']=PHES_cap
        Location_Constraints['locations']['KEN_WSTR']['techs']['PHES']['constraints']['storage_cap_equals']=PHES_en
        
        with open('Model_config/Location_Constraints_new.yaml', 'w') as outfile:
            yaml.dump(Location_Constraints, outfile, default_flow_style=False)
            
        model = calliope.Model(model_file)
       
        model.run()
         
        name_sh = int(sh*100)
        name_cap= int(cap)
         
        #give name to results file
        
        filename= f'Results-{name_cap}MW'
        foldername= f'Solar_share_{name_sh}%'
        integration = f'PHES'   #integration strategy name (RO, TE, PHES, PHES_TE)
        
        model.to_csv(f'Results/{integration}/{foldername}/{filename}')

    
