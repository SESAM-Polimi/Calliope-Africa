# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 11:59:25 2024

@author: baioc
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.integrate import simpson
import math

capacities=list(range(0, 25001, 2500)) #in MW

#share of solar capacity over overall added capacity
shares=[0, 0.2 0.4, 0.6, 0.8, 1] 

average_supply= 31.426000000029504 / 0.88

results =  ['RO', 'TE', 'PHES', 'PHES_TE']


renewables_data = {
    
    'scenario': [],
    'share': [],     
    'res_capacity': [],    #overall capacity of added renewables (wind+solar) in GW
    'res_energy':[]      #overall used energy of added renewables (wind+solar) in TWh

    
    }

renewables_data = pd.DataFrame(renewables_data)

#technologies to investigate

added_techs =  ['PV_added','Wind_added']
#%% Data gatherning

for res in results:
    
    
    for sh in shares:
        for cap in capacities:
            
            sh_name = int(sh*100)

            filepath= f'Results/{res}/{sh_name}%Solar_{100-sh_name}%Wind/Added_renewables-{cap}MW'
          
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
                
#%%

fig, ((ax1, ax2, ax3), (ax4,ax5,ax6))= plt.subplots(2,3, figsize=(63,43.5),)
fig.suptitle('Calliope Operation Nigeria: \n Increasing PV and Wind capacity with different shares', fontweight='bold',fontsize=80)  
plt.subplots_adjust(left=0.025, right=0.95, bottom=0.12, top=0.85, wspace=0.4, hspace=0.30) #per 3 righe
    

RE_Share = [10, 20, 30, 40, 50, 60, 70, 80, 90]
RE_Share_ticks = [10, 20, 30, 40, 50, 60, 70, 80, 90]

x_values = range(len(RE_Share))

sup_lim = 0.9

x_lim = 25

marker_x = [0.5 , 5, 10, 15, 20, 25]

i=1

for sh in shares:
    
    #extract needed data:
    ############################BASE ###################################################################
    
    RO_data = renewables_data.loc[(renewables_data['share']==sh) & (renewables_data['scenario']=='RO') ]
    RO_cap = RO_data.loc[:, 'res_capacity']
    RO_en = RO_data.loc[:, 'res_energy']
   
    # ############################Base_exp ###################################################################
    TE_data = renewables_data.loc[(renewables_data['share']==sh) & (renewables_data['scenario']=='TE') ]
    TE_cap = TE_data.loc[:, 'res_capacity']
    TE_en = TE_data.loc[:, 'res_energy']
   
    ############################PH ###################################################################
    PHES_data = renewables_data.loc[(renewables_data['share']==sh) & (renewables_data['scenario']=='PHES') ]
    PHES_cap = PHES_data.loc[:, 'res_capacity']
    PHES_en = PHES_data.loc[:, 'res_energy']
   
   
    ############################PH_exp ###################################################################
    PHES_TE_data = renewables_data.loc[(renewables_data['share']==sh) & (renewables_data['scenario']=='PHES_TE') ]
    PHES_TE_cap = PHES_TE_data.loc[:, 'res_capacity']
    PHES_TE_en = PHES_TE_data.loc[:, 'res_energy']
   
    
        
    ax= globals()[f'ax{i}']   
    
    ax.plot(x_values, RE_Share, color='#FFFFFF')
    ax.set_xticks(marker_x)
    ax.tick_params(axis='x', labelsize=50, pad=30)
    ax.tick_params(axis='y', labelsize=50, pad=30)
    ax.set_ylabel('Supply share',size=60)
    ax.set_xlabel('RE capacity [GW]',size=60)
#    ax.yaxis.set_major_formatter(yticks)
    ax.set_ylim(0,sup_lim*100 )
    ax.set_xlim(0,x_lim+3)
    ax_bis = ax.twinx()
    
    ax_bis.plot(RO_cap, RO_en, linewidth=6, color='#64b551', marker='o', markersize=30)
    ax_bis.plot(TE_cap, TE_en, linewidth=6, color='#055e24', marker='o', markersize=30)
    ax_bis.plot(PHES_cap, PHES_en, linewidth=6, color='#bd7ce6', marker='o', markersize=30) 
    ax_bis.plot(PHES_TE_cap, PHES_TE_en, linewidth=6, color='#8300d4', marker='o', markersize=30)

    ax_bis.set_ylabel('RE Energy [TWh]',size=55, labelpad=40)
    ax_bis.set_ylim(0,sup_lim*average_supply)
    ax_bis.tick_params(axis='y', labelsize=40)

    sh_Solar = int(sh*100)
    sh_Wind = math.ceil((1-sh)*100)
    
    if sh == 0:
        ax.set_title('100% Wind', fontweight='bold', fontsize=55, pad=40)
    elif sh == 1:
        ax.set_title('100% Solar', fontweight='bold', fontsize=55, pad=40)
    else:
        ax.set_title(f'{sh_Solar}% Solar, {sh_Wind}% Wind', fontweight='bold', fontsize=55, pad=40)
        
    i+=1
    
    
