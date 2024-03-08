# -*- coding: utf-8 -*-
"""
Created on Wed Feb 07 15:36:08 2024

@author: baioc
"""

import yaml
import calliope
import cal_graph as gg
try:
    calliope.set_log_level('INFO')
except:
    calliope.set_log_verbosity('Error')



#%% INPUT DATA

#cumulative capacity of additional wind and solar technologie (in MW)
capacity=list(range(10000,91000,10000))+[100000, 120000]

#share of solar capacity over overall added capacity
share=[0, 0.1, 0.2, 0.3, 0.4,0.5, 0.6, 0.7, 0.8, 0.9, 1] 

capacity=[10000, 50000]
share = [0,1]
#%% 4 integration strategies are considered

#Renewables Only (RO): only rewables are added
#PHES: add renewables and PHES
#Transmission expansion (TE) : add transmission expansion
#PHES and transmissio expansio (PHES and TE) : add PHES and transmission expansion

#NB model runs in operation

#%% INTEGRATION STRATEGY SELECTION AND DEFINITION


###### choose integration strategies to investigate #############
                                                                #
integration_strategies = ['RO', 'TE', 'PHES', 'PHES_TE']        #
                                                                #                                      
#################################################################

# data input for integration strategies:
# NB PHES capacity corresponds to maximum PHES plants available in the region from https://re100.eng.anu.edu.au/global/

strategy_definition = {
    'RO': {'model_file': 'model_transmission.yaml', 'PHES_cap': 0, 'PHES_en': 0},
    'TE': {'model_file': 'model_transmission_exp.yaml', 'PHES_cap': 0, 'PHES_en': 0},
    'PHES': {'model_file': 'model_transmission.yaml', 'PHES_cap': 200000000, 'PHES_en': 1200000000},       #PHES capacity and energy in kW
    'PHES_TE': {'model_file': 'model_transmission_exp.yaml', 'PHES_cap': 200000000, 'PHES_en': 1200000000} #PHES capacity and energy in kW
}


#%% MODELS RUN

for strategy in integration_strategies:
    # Check if the strategy is valid
    if strategy not in strategy_definition:
        raise NameError("Undefined strategy") 
        break
    
    # Access the values from the dictionary based on the strategy
    model_file = strategy_definition[strategy]['model_file']
    PHES_cap = strategy_definition[strategy]['PHES_cap']
    PHES_en = strategy_definition[strategy]['PHES_en']

    for cap in capacity:
        for sh in share:
            
            cap_kW = cap * 1e3
            
            Solar_cap = sh * cap_kW
            
            Wind_cap = cap_kW - Solar_cap
            
            with open('Model_config/Location_Constraints.yaml', 'r') as file:
                Location_Constraints = yaml.load(file, Loader=yaml.FullLoader)
            
            Location_Constraints['locations']['EGY_CN']['techs']['PV_added']['constraints']['energy_cap_equals']=Solar_cap
            Location_Constraints['locations']['EGY_CN']['techs']['Wind_added']['constraints']['energy_cap_equals']=Wind_cap
            Location_Constraints['locations']['EGY_CN']['techs']['PHES']['constraints']['energy_cap_equals']=PHES_cap
            Location_Constraints['locations']['EGY_CN']['techs']['PHES']['constraints']['storage_cap_equals']=PHES_en
            
            with open('Model_config/Location_Constraints_new.yaml', 'w') as outfile:
                yaml.dump(Location_Constraints, outfile, default_flow_style=False)
                
            model = calliope.Model(model_file)
           
            model.run()
    
            Solar_sh = int(sh*100)
            Wind_sh = 100 - Solar_sh
            name_cap= int(cap)
             
            #give name to results file
            
            filename= f'Added_renewables-{name_cap}MW'
            foldername= f'{Solar_sh}%Solar_{Wind_sh}%Wind'

            model.to_csv(f'Results/{strategy}/{foldername}/{filename}')     
            
