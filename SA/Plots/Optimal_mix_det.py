# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 11:45:26 2024

@author: baioc
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import pandas as pd
import os
from scipy.integrate import simpson

#%% DATA INPUTS

capacities=list(range(10000,91000,10000))+[100000, 120000] #in MW

shares = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


results =  ['RO', 'TE', 'PHES', 'PHES_TE']


renewables_data = {
    
    'scenario': [],
    'share': [],     
    'res_capacity': [],    #overall capacity of added renewables (wind+solar) in GW
    'res_energy':[]      #overall used energy of added renewables (wind+solar) in TWh

    
    }

renewables_data = pd.DataFrame(renewables_data)

#technologies to investigate

added_techs = ['PV_added', 'Wind_added']


#%% DATA GATHERING



for res in results:
    
    
    for sh in shares:
        for cap in capacities:
            
            sh_name = int(sh*100)

            filepath= f'/global-scratch/bulk_pool/nstevanato/Calliope/South_Africa_Results/{res}/{sh_name}%Solar_{100-sh_name}%Wind/Added_renewables-{cap}MW'
          
            energy_path = filepath + '/results_carrier_prod.csv' 
            
            capacity_path = filepath + '/results_energy_cap.csv' 
            
            try:
                energy=pd.read_csv(energy_path)     #energy use
                capacity=pd.read_csv(capacity_path) #capacity values
            
                res_energy=energy.loc[energy['techs'].isin(added_techs)].groupby(['techs']).sum(numeric_only=True).sum(numeric_only=True).item()*1e-9
                res_capacity=capacity.loc[capacity['techs'].isin(added_techs)].groupby(['techs']).sum(numeric_only=True).sum(numeric_only=True).item()*1e-6
                
                phes_size = capacity.loc[capacity['techs']=='PHES'].sum(numeric_only=True).item()*1e-6*6
                
                
                row = {'scenario': res, 'share': sh, 'res_capacity': res_capacity, 'res_energy': res_energy, 'phes_size': phes_size}
                row_df = pd.DataFrame([row])  # Convert dictionary to DataFrame
    
                renewables_data = pd.concat([renewables_data, row_df], ignore_index=True)

            except FileNotFoundError:
                
                print(f"Missing model run for: {filepath}")

#%% CALCULATE AREA

area_dict = {
    
    'scenario': [],
    'share': [],     
    'area': []
    
    }

area_df = pd.DataFrame(area_dict)

for sh in shares:
    for scen in results:
        
        data = renewables_data.loc[(renewables_data['scenario']==scen) & (renewables_data['share']==sh)]
                                                                                                    
        area = simpson(x= data.loc[:,'res_capacity'], y= data.loc[:,'res_energy'])  

        row =  {'scenario': res, 'share': sh, 'area':area}
        
        row_df = pd.DataFrame([row])
        
        area_df = pd.concat([area_df, row_df], ignore_index=True)
                              
area_df=area_df.groupby('share').sum(numeric_only=True)        

max_area_index = area_df['area'].idxmax()

#%% RETURN AREA

print(max_area_index)

