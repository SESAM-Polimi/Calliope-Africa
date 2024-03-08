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

capacities=list(range(10000,91000,10000))  #in MW

#share of solar capacity over overall added capacity
shares=[0, 0.2 0.4, 0.6, 0.8, 1] 

average_supply= 181028205646.60526 *1e-6/ 0.844

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
fig.suptitle('Calliope Operation Egypt: \n Increasing PV and Wind capacity with different shares', fontweight='bold',fontsize=80)  
plt.subplots_adjust(left=0.025, right=0.95, bottom=0.12, top=0.85, wspace=0.4, hspace=0.30) #per 3 righe
    
fmt = '%.0f%%'
yticks=ticker.FormatStrFormatter(fmt)

RE_Share = [0, 15, 20, 30, 40, 50, 60, 70, 80, 90]
RE_Share_ticks = [15, 30, 45, 60, 75, 90]

x_values = range(len(RE_Share))

sup_lim = 0.9

x_lim = 95

marker_x = [ 10, 30, 50, 70, 90]

i=1
legend_elements = [plt.Line2D([0], [0], marker='o', color='#64b551', markerfacecolor='#64b551', markersize=40, linewidth=8, label='RO'),
                   plt.Line2D([0], [0], marker='o', color='#055e24', markerfacecolor='#055e24', markersize=40, linewidth=8, label='TE'),
                   plt.Line2D([0], [0], marker='o', color='#bd7ce6', markerfacecolor='#bd7ce6', markersize=40,  linewidth=8,label='PHES'),
                   plt.Line2D([0], [0], marker='o', color='#bd7ce6', markerfacecolor='#8300d4', markersize=40,  linewidth=8,label='PHES and TE')]
for sh in shares:
    
    #extract needed data:
    ############################BASE ###################################################################
    
    RO_data = renewables_data.loc[(renewables_data['share']==sh) & (renewables_data['scenario']=='RO') ]
    RO_cap = RO_data.loc[:, 'res_capacity']
    RO_en = RO_data.loc[:, 'res_energy']
    
    RO_data_marker = renewables_data.loc[(renewables_data['share']==sh) & (renewables_data['scenario']=='RO') & (renewables_data['res_capacity'].isin(marker_x))]
    RO_cap_marker = RO_data_marker.loc[:, 'res_capacity']
    RO_en_marker = RO_data_marker.loc[:, 'res_energy']
   
    # ########################### TE ###################################################################
    TE_data = renewables_data.loc[(renewables_data['share']==sh) & (renewables_data['scenario']=='TE') ]
    TE_cap = TE_data.loc[:, 'res_capacity']
    TE_en = TE_data.loc[:, 'res_energy']

    TE_data_marker = renewables_data.loc[(renewables_data['share']==sh) & (renewables_data['scenario']=='TE') & (renewables_data['res_capacity'].isin(marker_x))]
    TE_cap_marker = TE_data_marker.loc[:, 'res_capacity']
    TE_en_marker = TE_data_marker.loc[:, 'res_energy']
    
    ############################ PHES ###################################################################
    PHES_data = renewables_data.loc[(renewables_data['share']==sh) & (renewables_data['scenario']=='PHES') ]
    PHES_cap = PHES_data.loc[:, 'res_capacity']
    PHES_en = PHES_data.loc[:, 'res_energy']
    
    PHES_data_marker = renewables_data.loc[(renewables_data['share']==sh) & (renewables_data['scenario']=='PHES') & (renewables_data['res_capacity'].isin(marker_x))]
    PHES_cap_marker = PHES_data_marker.loc[:, 'res_capacity']
    PHES_en_marker = PHES_data_marker.loc[:, 'res_energy']   
   
    ############################ PHES_TE ###################################################################
    PHES_TE_data = renewables_data.loc[(renewables_data['share']==sh) & (renewables_data['scenario']=='PHES_TE') ]
    PHES_TE_cap = PHES_TE_data.loc[:, 'res_capacity']
    PHES_TE_en = PHES_TE_data.loc[:, 'res_energy']

    PHES_TE_data_marker = renewables_data.loc[(renewables_data['share']==sh) & (renewables_data['scenario']=='PHES_TE') & (renewables_data['res_capacity'].isin(marker_x))]
    PHES_TE_cap_marker = PHES_TE_data_marker.loc[:, 'res_capacity']
    PHES_TE_en_marker = PHES_TE_data_marker.loc[:, 'res_energy']

        
    ax= globals()[f'ax{i}']   
    
    ax.plot(x_values, RE_Share, color='#FFFFFF')
    ax.set_xticks(marker_x)
    ax.set_yticks(RE_Share_ticks)
    ax.tick_params(axis='x', labelsize=50, pad=30)
    ax.tick_params(axis='y', labelsize=50, pad=30)
    ax.set_ylabel('Supply share',size=60)
    ax.set_xlabel('RE capacity [GW]',size=60)
    ax.yaxis.set_major_formatter(yticks)
    ax.set_ylim(0,sup_lim*100 )
    ax.set_xlim(0,x_lim+3)
    ax_bis = ax.twinx()
    
    ax_bis.plot(RO_cap, RO_en, linewidth=6, color='#64b551', zorder=4)
    ax_bis.plot(TE_cap, TE_en, linewidth=12, color='#055e24', zorder=1)
    ax_bis.plot(PHES_cap, PHES_en, linewidth=6, color='#bd7ce6', zorder=4) 
    ax_bis.plot(PHES_TE_cap, PHES_TE_en, linewidth=12, color='#8300d4', zorder=1)
    
    ax_bis.scatter(RO_cap_marker, RO_en_marker, s=2000, color='#64b551', zorder=4)
    ax_bis.scatter(TE_cap_marker, TE_en_marker, s=1000, color='#055e24', zorder=1)
    ax_bis.scatter(PHES_cap_marker, PHES_en_marker, s=2000, color='#bd7ce6', zorder=4) 
    ax_bis.scatter(PHES_TE_cap_marker, PHES_TE_en_marker, s=1000, color='#8300d4', zorder=1)

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

    ax.legend(handles=legend_elements, loc='upper left',prop={'size': 50})
    
plt.show()

