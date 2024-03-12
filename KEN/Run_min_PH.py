# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 16:38:11 2024

@author: baioc
"""

##################### MODEL RUN TO CALCULATE PHES SIZE ##################################


#The code calculates the minimum PHES size required to achieve the same energy generation results
#as the initial model run, where the introduced PHES capacity corresponds to the maximum possible 
#capacity installable in the region. Therefore, it is necessary to first run the model with 
#maximum capacity availability.

import calliope
import pandas as pd
import yaml
import os
import numpy as np


try:
    calliope.set_log_level('INFO')
except:
    calliope.set_log_verbosity('Error')
    
#%% DATA INPUT DEFINE CHARACTHERISTICS OF MODEL

#technologies present model
gen_techs = ['Diesel_Engine', 'HFO', 'OCGT_Oil', 'Hydro_Large1', 'Hydro_Large2', 'Hydro_Large3', 'Hydro_Large4', 'Hydro_Small', 
         'Wind1', 'Wind2', 'Wind3', 'Wind_added', 'Geothermal', 'Bioenergy', 'PV', 'PV_added']

#technologies added 
added_techs = ['PV_added', 'Wind_added']

#location of added technolgies
PV_added_loc = 'KEN_WSTR'
Wind_added_loc = 'KEN_MTKR'

#select deseried capacity values and shares for which the minimum PHES size needs to be calculated
capacity_values = list(range(250,3751, 500))
shares = [0,0.3, 1]
integration_strategies = ['PHES', 'PHES_TE' ]                                                            

# definition of integration strategies 
strategy_model = {
    'PHES': {'model_file': 'model_min_PH.yaml'},       
    'PHES_TE': {'model_file': 'model_min_PH_TE.yaml'} 
}


capacity_values=[1000,None]
shares=[0,None]
#%% PHES CAPACITY MINIMIZATION MODEL RUN

for strategy in integration_strategies:
    
    for sh in shares:
        
        for cap in capacity_values:
            
            sh_name = int(sh*100)    
                        
            filepath =  f'Results/{strategy}/{sh_name}%Solar_{100-sh_name}%Wind/Added_renewables-{cap}MW'   
 
            energy_path = os.path.join(filepath,'results_carrier_prod.csv')
            capacity_path = os.path.join(filepath,'results_energy_cap.csv')     
            
            try:
                #take annual production of generation technologies
                energy=pd.read_csv(energy_path)

                #energy=energy.loc[energy['techs'].isin(gen_techs)].groupby(['techs', 'locs']).sum()
                energy=energy.loc[energy['techs'].isin(gen_techs)].groupby(['techs']).sum()
                            
            except FileNotFoundError:
                
                print(f"Missing maxium PHES capacity model run for: \n {strategy}/{sh_name}%Solar_{100-sh_name}%Wind/Added_renewables-{cap}MW")
                
                break
            
            #take capacity of unlimited model

            capacity=pd.read_csv(capacity_path)
            capacity=capacity.loc[capacity['techs'].isin(added_techs)]

            energy.reset_index(inplace=True)
        
        

            # ADDED RENEWAVLE CAPACITY
            
            with open('Model_config/Location_Constraints_PH_min.yaml', 'r') as file:
                Location_Constraints_PH_min = yaml.load(file, Loader=yaml.FullLoader)
            
            Location_Constraints_PH_min['locations'][Wind_added_loc]['techs']['Wind_added']['constraints']['energy_cap_equals']=capacity.loc[capacity['techs']=='Wind_added'].loc[:,'energy_cap'].sum().item()
            Location_Constraints_PH_min['locations'][PV_added_loc]['techs']['PV_added']['constraints']['energy_cap_equals']=capacity.loc[capacity['techs']=='PV_added'].loc[:,'energy_cap'].sum().item()
            with open('Model_config/Location_Constraints_PH_min_new.yaml', 'w') as outfile:
                yaml.dump(Location_Constraints_PH_min, outfile, default_flow_style=False)
                     
            
            # DEFINE PRODUCTION LIMITS AND DEFINE CONSTRAINTS
            
            #define production limitis            
            energy['carrier_prod_max']=energy['carrier_prod']*(1+0.025)
            energy['carrier_prod_min']=energy['carrier_prod']*(1-0.025)
                                                               
            #update overrides file                                                                  
            overrides_file_path = 'Model_config/Overrides_empty.yaml'

            with open(overrides_file_path, 'r') as file:
                overrides_new = yaml.load(file, Loader=yaml.FullLoader)
                                 
            for i in range(len(energy)):
            
                #minumum production constraint
                overrides_new['overrides']['Energy_constraint']['group_constraints'][f"{energy.iloc[i]['techs']}_Energy_min"]['carrier_prod_min']['power'] = energy.iloc[i]['carrier_prod_min'].item()
                #maximum production contraint
                overrides_new['overrides']['Energy_constraint']['group_constraints'][f"{energy.iloc[i]['techs']}_Energy_max"]['carrier_prod_max']['power'] = energy.iloc[i]['carrier_prod_max'].item()
                                
            with open('Model_config/Overrides_updated.yaml', 'w') as outfile:
                yaml.dump(overrides_new, outfile, default_flow_style=False)
                
            # MODEL RUN    



            model=calliope.Model(strategy_model[strategy]['model_file'], scenario='Energy_constraint')
            
            model.run()
            
            model.to_csv(f'Results/Minimized_PHES/{strategy}/{sh_name}%Solar_{100-sh_name}%Wind_PHES_min/Added_renewables-{cap}MW')






