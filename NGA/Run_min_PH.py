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
gen_techs = ['Hydro_Large', 'Hydro_Small', 'PV', 'PV_added', 'OCGT', 'CCGT', 'GST', 'HFO', 'Wind', 'Wind_added']  

#technologies added 
added_techs = ['PV_added', 'Wind_added']

#location of added technolgies
PV_added_loc = 'NGA_E'
Wind_added_loc = 'NGA_E'

#select deseried capacity values and shares for which the minimum PHES size needs to be calculated
shares = [0, 0.5]
capacity_values = [10000, 25000]
integration_strategies = ['PHES', 'PHES_TE' ]                                                            

# definition of integration strategies 
strategy_model = {
    'PHES': {'model_file': 'model_min_PH.yaml'},       
    'PHES_TE': {'model_file': 'model_min_PH_TE.yaml'} 
}

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



#%% CHECK CONSTRAINT APPLICATION:
    
energy_PHES_max = pd.read_csv('Results/PHES/0%Solar_100%Wind/Added_renewables-25000MW/results_carrier_prod.csv')    
   
energy_PHES_max=energy_PHES_max.loc[energy_PHES_max['techs'].isin(gen_techs)].groupby(['techs']).sum()

    
energy_constrained=pd.read_csv('Results/Minimized_PHES/PHES/0%Solar_100%Wind_PHES_min/Added_renewables-25000MW/results_carrier_prod.csv')

energy_constrained=energy_constrained.loc[energy_constrained['techs'].isin(gen_techs)].groupby(['techs']).sum()



























#%%


import time

# Record the start time
start_time = time.time()

# Your code to measure here
# For example:
    
res= 0
for i in range(10000):
    res=res + 50000*i
    pass  # Replace this with the code you want to measure

# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

# Print the elapsed time
print("Elapsed time:", elapsed_time, "seconds")













