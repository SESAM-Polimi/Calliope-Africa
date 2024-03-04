
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 08:53:25 2023

@author: baioc
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import matplotlib.ticker as mtick

average_supply= 268.74141906679006 / 0.844

#%%################################## SOLAR ###########################################################

#Base original transmissions

main_folder_Base = 'Results/RO/100%Solar_0%Wind'

Solar_cap_Base=[]
Solar_en_Base=[]


# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_Base) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate solar capacity
    Solar_Capacity=Capacity.loc[Capacity['techs']=='PV_added']
    
    Solar_Capacity=Solar_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    #calculate energy
    
    Solar_Energy=Energy.loc[Energy['techs']=='PV_added']

    Solar_Energy=Solar_Energy.loc[:,'carrier_prod'].sum()*1e-9

 

    #update array
    
    Solar_cap_Base.append(Solar_Capacity)
    Solar_en_Base.append(Solar_Energy)

    
# Base expanded (new exp)

main_folder_Base_exp = 'Results/TE/100%Solar_0%Wind'

Solar_cap_Base_exp=[]
Solar_en_Base_exp=[]


# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_Base_exp) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate solar capacity
    Solar_Capacity=Capacity.loc[Capacity['techs']=='PV_added']
    
    Solar_Capacity=Solar_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    #calculate energy
    
    Solar_Energy=Energy.loc[Energy['techs']=='PV_added']

    Solar_Energy=Solar_Energy.loc[:,'carrier_prod'].sum()*1e-9

    #update array
    
    Solar_cap_Base_exp.append(Solar_Capacity)
    Solar_en_Base_exp.append(Solar_Energy)



# PH  original transmission
main_folder_PH = 'Results/PHES/100%Solar_0%Wind'

Solar_cap_PH=[]
Solar_en_PH=[]
Solar_PH_en_PH=[]
# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_PH) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate solar capacity
    Solar_Capacity=Capacity.loc[Capacity['techs']=='PV_added']
    
    Solar_Capacity=Solar_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    #calculate energy
    
    Solar_Energy=Energy.loc[Energy['techs']=='PV_added']

    Solar_Energy=Solar_Energy.loc[:,'carrier_prod'].sum()*1e-9

    PH_Energy=Energy.loc[Energy['techs']=='PHES']
    
    PH_Energy=PH_Energy.loc[:,'carrier_prod'].sum()*1e-9  
    

    #update array
    
    Solar_cap_PH.append(Solar_Capacity)
    Solar_en_PH.append(Solar_Energy)
    Solar_PH_en_PH.append(PH_Energy)

# PH expanded (new exp)
main_folder_PH_exp = 'Results/PHES_TE/100%Solar_0%Wind'

Solar_cap_PH_exp=[]
Solar_en_PH_exp=[]
RE_share_PH_exp=[]
PH_en_PH_exp=[]
NG_en_PH_exp=[]

# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_PH_exp) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate solar capacity
    Solar_Capacity=Capacity.loc[Capacity['techs']=='PV_added']
    
    Solar_Capacity=Solar_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    #calculate energy
    
    Solar_Energy=Energy.loc[Energy['techs']=='PV_added']

    Solar_Energy=Solar_Energy.loc[:,'carrier_prod'].sum()*1e-9


    #update array
    
    Solar_cap_PH_exp.append(Solar_Capacity)
    Solar_en_PH_exp.append(Solar_Energy)


#%%########################## IMPORT MIN PH CAPACITY SOLAR #######################################

main_folder_Infinite = 'Results/Minimized_PHES/PHES/100%Solar_0%Wind_PHES_min'

subfolders = [f.path for f in os.scandir(main_folder_Infinite) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))

Solar_en_Min=[]
Solar_cap_Min=[]
Solar_PH_en_Min=[]
Solar_PH_cap_Min=[]

for subfolder in subfolders:
    
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    file_path_cap= os.path.join(subfolder, 'results_energy_cap.csv')
    
    #energy

    Energy_Minimized = pd.read_csv(file_path_en)
    
    Solar_Energy_Minimized=Energy_Minimized.loc[Energy_Minimized['techs']=='PV_added']
    
    Solar_Energy_Minimized=Solar_Energy_Minimized.loc[:,'carrier_prod'].sum()*1e-9
    
    PH_Energy_Minimized=Energy_Minimized.loc[Energy_Minimized['techs']=='PHES']
    
    PH_Energy_Minimized=PH_Energy_Minimized.loc[:,'carrier_prod'].sum()*1e-9


    #capacity
    
    Capacity_Minimized = pd.read_csv(file_path_cap)
    
    Solar_Capacity_Minimized=Capacity_Minimized.loc[Capacity_Minimized['techs']=='PV_added']
    
    Solar_Capacity_Minimized=Solar_Capacity_Minimized.loc[:,'energy_cap'].sum()*1e-6 #GW
        
    
    PH_Capacity_Minimized=Capacity_Minimized.loc[Capacity_Minimized['techs']=='PHES']
    
    PH_Capacity_Minimized=PH_Capacity_Minimized.loc[:,'energy_cap'].sum()*1e-6  #GW
    
    #aggiungo ad array
    
    Solar_cap_Min.append(Solar_Capacity_Minimized)
    Solar_en_Min.append(Solar_Energy_Minimized)
    Solar_PH_cap_Min.append(PH_Capacity_Minimized)
    Solar_PH_en_Min.append(PH_Energy_Minimized)

Solar_PHES_size=np.array(Solar_PH_cap_Min)*6


#%%########################## IMPORT MIN PH CAPACITY SOLAR EXP #######################################

main_folder_Solar_exp = 'Results/Minimized_PHES/PHES_TE/100%Solar_0%Wind_PHES_min'

subfolders = [f.path for f in os.scandir(main_folder_Solar_exp) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))

Solar_en_Min_exp=[]
Solar_cap_Min_exp=[]
Solar_PH_en_Min_exp=[]
Solar_PH_cap_Min_exp=[]

for subfolder in subfolders:
    
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    file_path_cap= os.path.join(subfolder, 'results_energy_cap.csv')
    
    #energy

    Energy_Minimized = pd.read_csv(file_path_en)
    
    Solar_Energy_Minimized=Energy_Minimized.loc[Energy_Minimized['techs']=='PV_added']
    
    Solar_Energy_Minimized=Solar_Energy_Minimized.loc[:,'carrier_prod'].sum()*1e-9
    
    PH_Energy_Minimized=Energy_Minimized.loc[Energy_Minimized['techs']=='PHES']
    
    PH_Energy_Minimized=PH_Energy_Minimized.loc[:,'carrier_prod'].sum()*1e-9


    #capacity
    
    Capacity_Minimized = pd.read_csv(file_path_cap)
    
    Solar_Capacity_Minimized=Capacity_Minimized.loc[Capacity_Minimized['techs']=='PV_added']
    
    Solar_Capacity_Minimized=Solar_Capacity_Minimized.loc[:,'energy_cap'].sum()*1e-6 #GW
        
    
    PH_Capacity_Minimized=Capacity_Minimized.loc[Capacity_Minimized['techs']=='PHES']
    
    PH_Capacity_Minimized=PH_Capacity_Minimized.loc[:,'energy_cap'].sum()*1e-6  #GW
    
    #aggiungo ad array
    
    Solar_cap_Min_exp.append(Solar_Capacity_Minimized)
    Solar_en_Min_exp.append(Solar_Energy_Minimized)
    Solar_PH_cap_Min_exp.append(PH_Capacity_Minimized)
    Solar_PH_en_Min_exp.append(PH_Energy_Minimized)

Solar_exp_PHES_size=np.array(Solar_PH_cap_Min_exp)*6

#%%################################## WIND ###########################################################

# Base original transmissions

main_folder_Base = 'Results/RO/0%Solar_100%Wind'

Wind_cap_Base=[]
Wind_en_Base=[]


# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_Base) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate Wind capacity
    Wind_Capacity=Capacity.loc[Capacity['techs']=='Wind_added']
    
    Wind_Capacity=Wind_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    #calculate energy
    
    Wind_Energy=Energy.loc[Energy['techs']=='Wind_added']

    Wind_Energy=Wind_Energy.loc[:,'carrier_prod'].sum()*1e-9

 

    #update array
    
    Wind_cap_Base.append(Wind_Capacity)
    Wind_en_Base.append(Wind_Energy)

    
# Base expanded (new exp)

main_folder_Base_exp = 'Results/TE/0%Solar_100%Wind'

Wind_cap_Base_exp=[]
Wind_en_Base_exp=[]


# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_Base_exp) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate Wind capacity
    Wind_Capacity=Capacity.loc[Capacity['techs']=='Wind_added']
    
    Wind_Capacity=Wind_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    #calculate energy
    
    Wind_Energy=Energy.loc[Energy['techs']=='Wind_added']

    Wind_Energy=Wind_Energy.loc[:,'carrier_prod'].sum()*1e-9

    #update array
    
    Wind_cap_Base_exp.append(Wind_Capacity)
    Wind_en_Base_exp.append(Wind_Energy)



# PH  original transmission
main_folder_PH = 'Results/PHES/0%Solar_100%Wind'

Wind_PH_en_PH=[]
Wind_cap_PH=[]
Wind_en_PH=[]

# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_PH) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate Wind capacity
    Wind_Capacity=Capacity.loc[Capacity['techs']=='Wind_added']
    
    Wind_Capacity=Wind_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    #calculate energy
    
    Wind_Energy=Energy.loc[Energy['techs']=='Wind_added']

    Wind_Energy=Wind_Energy.loc[:,'carrier_prod'].sum()*1e-9

    PH_Energy=Energy.loc[Energy['techs']=='PHES']
    
    PH_Energy=PH_Energy.loc[:,'carrier_prod'].sum()*1e-9

    #update array
    
    Wind_cap_PH.append(Wind_Capacity)
    Wind_en_PH.append(Wind_Energy)
    Wind_PH_en_PH.append(PH_Energy)
# PH expanded (new exp)
main_folder_PH_exp = 'Results/PHES_TE/0%Solar_100%Wind'

Wind_cap_PH_exp=[]
Wind_en_PH_exp=[]
RE_share_PH_exp=[]
PH_en_PH_exp=[]
NG_en_PH_exp=[]

# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_PH_exp) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate Wind capacity
    Wind_Capacity=Capacity.loc[Capacity['techs']=='Wind_added']
    
    Wind_Capacity=Wind_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    #calculate energy
    
    Wind_Energy=Energy.loc[Energy['techs']=='Wind_added']

    Wind_Energy=Wind_Energy.loc[:,'carrier_prod'].sum()*1e-9
    
    PH_Energy_Minimized=Energy_Minimized.loc[Energy_Minimized['techs']=='PHES']
    
    PH_Energy_Minimized=PH_Energy_Minimized.loc[:,'carrier_prod'].sum()*1e-9

    #update array
    
    Wind_cap_PH_exp.append(Wind_Capacity)
    Wind_en_PH_exp.append(Wind_Energy)


#%%########################## IMPORT MIN PH CAPACITY WIND #######################################

main_folder_Infinite = 'Results/Minimized_PHES/PHES/0%Solar_100%Wind_PHES_min'

subfolders = [f.path for f in os.scandir(main_folder_Infinite) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))

Wind_en_Min=[]
Wind_cap_Min=[]
Wind_PH_en_Min=[]
Wind_PH_cap_Min=[]

for subfolder in subfolders:
    
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    file_path_cap= os.path.join(subfolder, 'results_energy_cap.csv')
    
    #energy

    Energy_Minimized = pd.read_csv(file_path_en)
    
    Wind_Energy_Minimized=Energy_Minimized.loc[Energy_Minimized['techs']=='Wind_added']
    
    Wind_Energy_Minimized=Wind_Energy_Minimized.loc[:,'carrier_prod'].sum()*1e-9
    
    PH_Energy_Minimized=Energy_Minimized.loc[Energy_Minimized['techs']=='PHES']
    
    PH_Energy_Minimized=PH_Energy_Minimized.loc[:,'carrier_prod'].sum()*1e-9


    #capacity
    
    Capacity_Minimized = pd.read_csv(file_path_cap)
    
    Wind_Capacity_Minimized=Capacity_Minimized.loc[Capacity_Minimized['techs']=='Wind_added']
    
    Wind_Capacity_Minimized=Wind_Capacity_Minimized.loc[:,'energy_cap'].sum()*1e-6 #GW
        
    
    PH_Capacity_Minimized=Capacity_Minimized.loc[Capacity_Minimized['techs']=='PHES']
    
    PH_Capacity_Minimized=PH_Capacity_Minimized.loc[:,'energy_cap'].sum()*1e-6  #GW
    
    #aggiungo ad array
    
    Wind_cap_Min.append(Wind_Capacity_Minimized)
    Wind_en_Min.append(Wind_Energy_Minimized)
    Wind_PH_cap_Min.append(PH_Capacity_Minimized)
    Wind_PH_en_Min.append(PH_Energy_Minimized)

Wind_PHES_size=np.array(Wind_PH_cap_Min)*6

#%%########################## IMPORT Min_exp PH CAPACITY WIND EXP #######################################

main_folder_Infinite = 'Results/Minimized_PHES/PHES_TE/0%Solar_100%Wind_PHES_min'

subfolders = [f.path for f in os.scandir(main_folder_Infinite) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))

Wind_en_Min_exp=[]
Wind_cap_Min_exp=[]
Wind_PH_en_Min_exp=[]
Wind_PH_cap_Min_exp=[]

for subfolder in subfolders:
    
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    file_path_cap= os.path.join(subfolder, 'results_energy_cap.csv')
    
    #energy

    Energy_Minimized = pd.read_csv(file_path_en)
    
    Wind_Energy_Minimized=Energy_Minimized.loc[Energy_Minimized['techs']=='Wind_added']
    
    Wind_Energy_Minimized=Wind_Energy_Minimized.loc[:,'carrier_prod'].sum()*1e-9
    
    PH_Energy_Minimized=Energy_Minimized.loc[Energy_Minimized['techs']=='PHES']
    
    PH_Energy_Minimized=PH_Energy_Minimized.loc[:,'carrier_prod'].sum()*1e-9


    #capacity
    
    Capacity_Minimized = pd.read_csv(file_path_cap)
    
    Wind_Capacity_Minimized=Capacity_Minimized.loc[Capacity_Minimized['techs']=='Wind_added']
    
    Wind_Capacity_Minimized=Wind_Capacity_Minimized.loc[:,'energy_cap'].sum()*1e-6 #GW
        
    
    PH_Capacity_Minimized=Capacity_Minimized.loc[Capacity_Minimized['techs']=='PHES']
    
    PH_Capacity_Minimized=PH_Capacity_Minimized.loc[:,'energy_cap'].sum()*1e-6  #GW
    
    #aggiungo ad array
    
    Wind_cap_Min_exp.append(Wind_Capacity_Minimized)
    Wind_en_Min_exp.append(Wind_Energy_Minimized)
    Wind_PH_cap_Min_exp.append(PH_Capacity_Minimized)
    Wind_PH_en_Min_exp.append(PH_Energy_Minimized)

Wind_exp_PHES_size=np.array(Wind_PH_cap_Min_exp)*6

#%%############################################## SW ###############################################################
#optimal share evaluated

sh_Base = 0.5
sh_Base_exp = 0.5
sh_PH = 0.5
sh_PH_exp = 0.5
#%%################################## Base ###########################################################

main_folder_Base = f'Results/RO/10%Solar_90%Wind'

RE_cap_Base=[]
RE_en_Base=[]


# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_Base) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate solar capacity
    Solar_Capacity=Capacity.loc[(Capacity['techs']=='PV_added')  ]
    
    Solar_Capacity=Solar_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    Wind_Capacity=Capacity.loc[(Capacity['techs']=='Wind_added')   ]
    
    Wind_Capacity=Wind_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    RE_Capacity = Solar_Capacity + Wind_Capacity 
    
    #calculate energy
    
    Solar_Energy=Energy.loc[(Energy['techs']=='PV_added')]

    Solar_Energy=Solar_Energy.loc[:,'carrier_prod'].sum()*1e-9

    
    Wind_Energy=Energy.loc[(Energy['techs']=='Wind_added') ]

    Wind_Energy=Wind_Energy.loc[:,'carrier_prod'].sum()*1e-9
    
    RE_Energy  = Solar_Energy + Wind_Energy

    #update array
    
    RE_cap_Base.append(RE_Capacity)
    RE_en_Base.append(RE_Energy)

#%%################################## Base exp ###########################################################

main_folder_Base = f'Results/TE/10%Solar_90%Wind'

RE_cap_Base_exp=[]
RE_en_Base_exp=[]


# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_Base) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate solar capacity
    Solar_Capacity=Capacity.loc[(Capacity['techs']=='PV_added')  ]
    
    Solar_Capacity=Solar_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    Wind_Capacity=Capacity.loc[(Capacity['techs']=='Wind_added')   ]
    
    Wind_Capacity=Wind_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    RE_Capacity = Solar_Capacity + Wind_Capacity 
    
    #calculate energy
    
    Solar_Energy=Energy.loc[(Energy['techs']=='PV_added')]

    Solar_Energy=Solar_Energy.loc[:,'carrier_prod'].sum()*1e-9

    
    Wind_Energy=Energy.loc[(Energy['techs']=='Wind_added') ]

    Wind_Energy=Wind_Energy.loc[:,'carrier_prod'].sum()*1e-9
    
    RE_Energy  = Solar_Energy + Wind_Energy

    #update array
    
    RE_cap_Base_exp.append(RE_Capacity)
    RE_en_Base_exp.append(RE_Energy)

#%%################################## PH ###########################################################

main_folder_PH = f'Results/PHES/10%Solar_90%Wind'

RE_cap_PH=[]
RE_en_PH=[]


# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_PH) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate solar capacity
    Solar_Capacity=Capacity.loc[(Capacity['techs']=='PV_added')  ]
    
    Solar_Capacity=Solar_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    Wind_Capacity=Capacity.loc[(Capacity['techs']=='Wind_added')   ]
    
    Wind_Capacity=Wind_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    RE_Capacity = Solar_Capacity + Wind_Capacity 
    
    #calculate energy
    
    Solar_Energy=Energy.loc[(Energy['techs']=='PV_added')]

    Solar_Energy=Solar_Energy.loc[:,'carrier_prod'].sum()*1e-9

    
    Wind_Energy=Energy.loc[(Energy['techs']=='Wind_added') ]

    Wind_Energy=Wind_Energy.loc[:,'carrier_prod'].sum()*1e-9
    
    RE_Energy  = Solar_Energy + Wind_Energy

    #update array
    
    RE_cap_PH.append(RE_Capacity)
    RE_en_PH.append(RE_Energy)

#%%################################## PH exp ###########################################################

main_folder_PH = f'Results/PHES_TE/10%Solar_90%Wind'

RE_cap_PH_exp=[]
RE_en_PH_exp=[]


# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_PH) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate solar capacity
    Solar_Capacity=Capacity.loc[(Capacity['techs']=='PV_added')  ]
    
    Solar_Capacity=Solar_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    Wind_Capacity=Capacity.loc[(Capacity['techs']=='Wind_added')   ]
    
    Wind_Capacity=Wind_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    RE_Capacity = Solar_Capacity + Wind_Capacity 
    
    #calculate energy
    
    Solar_Energy=Energy.loc[(Energy['techs']=='PV_added')]

    Solar_Energy=Solar_Energy.loc[:,'carrier_prod'].sum()*1e-9

    
    Wind_Energy=Energy.loc[(Energy['techs']=='Wind_added') ]

    Wind_Energy=Wind_Energy.loc[:,'carrier_prod'].sum()*1e-9
    
    RE_Energy  = Solar_Energy + Wind_Energy

    #update array
    
    RE_cap_PH_exp.append(RE_Capacity)
    RE_en_PH_exp.append(RE_Energy)
    
#%%################################## PH minimized ###########################################################

main_folder_PH = 'Results/Minimized_PHES/PHES/10%Solar_90%Wind_PHES_min'

RE_cap_PH_Min=[]
RE_en_PH_Min=[]
PH_cap_SW_Min=[]
PH_en_SW_Min=[]


# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_PH) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate solar capacity
    Solar_Capacity=Capacity.loc[(Capacity['techs']=='PV_added')  ]
    
    Solar_Capacity=Solar_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    Wind_Capacity=Capacity.loc[(Capacity['techs']=='Wind_added')   ]
    
    Wind_Capacity=Wind_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    RE_Capacity = Solar_Capacity + Wind_Capacity 
           
    PH_Capacity=Capacity.loc[Capacity['techs']=='PHES']
    
    PH_Capacity=PH_Capacity.loc[:,'energy_cap'].sum()*1e-6  #GW
    
    
    #calculate energy
    
    Solar_Energy=Energy.loc[(Energy['techs']=='PV_added')]

    Solar_Energy=Solar_Energy.loc[:,'carrier_prod'].sum()*1e-9

    
    Wind_Energy=Energy.loc[(Energy['techs']=='Wind_added') ]

    Wind_Energy=Wind_Energy.loc[:,'carrier_prod'].sum()*1e-9
    
    RE_Energy  = Solar_Energy + Wind_Energy
    
    PH_Energy=Energy.loc[Energy['techs']=='PHES']
    
    PH_Energy=PH_Energy.loc[:,'carrier_prod'].sum()*1e-9

    #update array
    
    RE_cap_PH_Min.append(RE_Capacity)
    RE_en_PH_Min.append(RE_Energy)
    PH_cap_SW_Min.append(PH_Capacity)
    PH_en_SW_Min.append(PH_Energy)
    
SW_PHES_size=np.array(PH_cap_SW_Min)*6
#%%################################## PH exp Minimized ###########################################################

main_folder_PH = 'Results/Minimized_PHES/PHES_TE/10%Solar_90%Wind_PHES_min'

RE_cap_PH_Min_exp=[]
RE_en_PH_Min_exp=[]
PH_cap_SW_Min_exp=[]
PH_en_SW_Min_exp=[]


# Get a list of all the subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_PH) if f.is_dir()]

subfolders = sorted(subfolders, key=lambda x: float(x.split('-')[-1][:-2]))


for subfolder in subfolders:
    
    file_path_cap = os.path.join(subfolder, 'results_energy_cap.csv')
    file_path_en = os.path.join(subfolder, 'results_carrier_prod.csv')
    
    Capacity = pd.read_csv(file_path_cap)
    Energy = pd.read_csv(file_path_en)
    
    #calculate solar capacity
    Solar_Capacity=Capacity.loc[(Capacity['techs']=='PV_added')  ]
    
    Solar_Capacity=Solar_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    Wind_Capacity=Capacity.loc[(Capacity['techs']=='Wind_added')   ]
    
    Wind_Capacity=Wind_Capacity.loc[:,'energy_cap'].sum()*1e-6
    
    RE_Capacity = Solar_Capacity + Wind_Capacity 
           
    PH_Capacity=Capacity.loc[Capacity['techs']=='PHES']
    
    PH_Capacity=PH_Capacity.loc[:,'energy_cap'].sum()*1e-6  #GW
    
    
    #calculate energy
    
    Solar_Energy=Energy.loc[(Energy['techs']=='PV_added')]

    Solar_Energy=Solar_Energy.loc[:,'carrier_prod'].sum()*1e-9

    
    Wind_Energy=Energy.loc[(Energy['techs']=='Wind_added') ]

    Wind_Energy=Wind_Energy.loc[:,'carrier_prod'].sum()*1e-9
    
    RE_Energy  = Solar_Energy + Wind_Energy
    
    PH_Energy=Energy.loc[Energy['techs']=='PHES']
    
    PH_Energy=PH_Energy.loc[:,'carrier_prod'].sum()*1e-9

    #update array
    
    RE_cap_PH_Min_exp.append(RE_Capacity)
    RE_en_PH_Min_exp.append(RE_Energy)
    PH_cap_SW_Min_exp.append(PH_Capacity)
    PH_en_SW_Min_exp.append(PH_Energy)
    
SW_exp_PHES_size=np.array(PH_cap_SW_Min_exp)*6


#%% resize PH S

Solar_cap_Base = [x for x in Solar_cap_Base if x <= 90 and x>=10]
Solar_cap_Base_exp = [x for x in Solar_cap_Base_exp if x <= 90 and x>=10]
Solar_cap_PH = [x for x in Solar_cap_PH if x <= 90 and x>=10]
Solar_cap_PH_exp = [x for x in Solar_cap_PH_exp if x <= 90 and x>=10]
Solar_cap_Min = [x for x in Solar_cap_Min if x <= 90 and x>=10]
Solar_cap_Min_exp = [x for x in Solar_cap_Min_exp if x <= 90 and x>=10]


Solar_en_Base = Solar_en_Base [:len(Solar_cap_Base)]
Solar_en_Base_exp = Solar_en_Base_exp [:len(Solar_cap_Base_exp)]
Solar_en_PH = Solar_en_PH [:len(Solar_cap_PH)]
Solar_en_PH_exp = Solar_en_PH_exp [:len(Solar_cap_PH_exp)]
Solar_en_Min = Solar_en_Min [:len(Solar_cap_Min)]
Solar_en_Min_exp = Solar_en_Min_exp [:len(Solar_cap_Min_exp)]
Solar_PH_en_Min = Solar_PH_en_Min [:len(Solar_cap_Min)]
Solar_PH_en_Min_exp = Solar_PH_en_Min_exp [:len(Solar_cap_Min_exp)]

Solar_cap_Base = [round(value, 1) for value in Solar_cap_Base]
Solar_cap_Base_exp = [round(value, 1) for value in Solar_cap_Base_exp]
Solar_cap_PH = [round(value, 1) for value in Solar_cap_PH]
Solar_cap_PH_exp = [round(value, 1) for value in Solar_cap_PH_exp]
Solar_cap_Min = [round(value, 1) for value in Solar_cap_Min]
Solar_cap_Min_exp = [round(value, 1) for value in Solar_cap_Min_exp]

marker_x_Solar = [ 10, 30, 50, 70, 90]


marker_y_Solar_Base = [Solar_en_Base[Solar_cap_Base.index(pos)] for pos in marker_x_Solar]
marker_y_Solar_Base_exp = [Solar_en_Base_exp[Solar_cap_Base_exp.index(pos)] for pos in marker_x_Solar]
marker_y_Solar_PH = [Solar_en_PH[Solar_cap_PH.index(pos)] for pos in marker_x_Solar]
marker_y_Solar_PH_exp = [Solar_en_PH_exp[Solar_cap_PH_exp.index(pos)] for pos in marker_x_Solar]
marker_y_Solar_Min = [Solar_en_Min[Solar_cap_Min.index(pos)] for pos in marker_x_Solar]
marker_y_Solar_Min_exp = [Solar_en_Min_exp[Solar_cap_Min_exp.index(pos)] for pos in marker_x_Solar]
marker_y_Solar_PH_Min = [Solar_PH_en_Min[Solar_cap_Min.index(pos)] for pos in marker_x_Solar]
marker_y_Solar_PH_Min_exp = [Solar_PH_en_Min_exp[Solar_cap_Min_exp.index(pos)] for pos in marker_x_Solar]

Solar_PHES_size = [Solar_PHES_size[Solar_cap_Min.index(pos)] for pos in marker_x_Solar]
Solar_exp_PHES_size = [Solar_exp_PHES_size[Solar_cap_Min_exp.index(pos)] for pos in marker_x_Solar]


#%% resize PH W

Wind_cap_Base = [x for x in Wind_cap_Base if x <= 90 and x>=10]
Wind_cap_Base_exp = [x for x in Wind_cap_Base_exp if x <= 90 and x>=10]
Wind_cap_PH = [x for x in Wind_cap_PH if x <= 90 and x>=10]
Wind_cap_PH_exp = [x for x in Wind_cap_PH_exp if x <= 90 and x>=10]
Wind_cap_Min = [x for x in Wind_cap_Min if x <= 90 and x>=10]
Wind_cap_Min_exp = [x for x in Wind_cap_Min_exp if x <= 90 and x>=10]


Wind_en_Base = Wind_en_Base [:len(Wind_cap_Base)]
Wind_en_Base_exp = Wind_en_Base_exp [:len(Wind_cap_Base_exp)]
Wind_en_PH = Wind_en_PH [:len(Wind_cap_PH)]
Wind_en_PH_exp = Wind_en_PH_exp [:len(Wind_cap_PH_exp)]
Wind_en_Min = Wind_en_Min [:len(Wind_cap_Min)]
Wind_en_Min_exp = Wind_en_Min_exp [:len(Wind_cap_Min_exp)]
Wind_PH_en_Min = Wind_PH_en_Min [:len(Wind_cap_Min)]
Wind_PH_en_Min_exp = Wind_PH_en_Min_exp [:len(Wind_cap_Min_exp)]

Wind_cap_Base = [round(value, 1) for value in Wind_cap_Base]
Wind_cap_Base_exp = [round(value, 1) for value in Wind_cap_Base_exp]
Wind_cap_PH = [round(value, 1) for value in Wind_cap_PH]
Wind_cap_PH_exp = [round(value, 1) for value in Wind_cap_PH_exp]
Wind_cap_Min = [round(value, 1) for value in Wind_cap_Min]
Wind_cap_Min_exp = [round(value, 1) for value in Wind_cap_Min_exp]

marker_x_Wind = [ 10, 30, 50, 70, 90]


marker_y_Wind_Base = [Wind_en_Base[Wind_cap_Base.index(pos)] for pos in marker_x_Wind]
marker_y_Wind_Base_exp = [Wind_en_Base_exp[Wind_cap_Base_exp.index(pos)] for pos in marker_x_Wind]
marker_y_Wind_PH = [Wind_en_PH[Wind_cap_PH.index(pos)] for pos in marker_x_Wind]
marker_y_Wind_PH_exp = [Wind_en_PH_exp[Wind_cap_PH_exp.index(pos)] for pos in marker_x_Wind]
marker_y_Wind_Min = [Wind_en_Min[Wind_cap_Min.index(pos)] for pos in marker_x_Wind]
marker_y_Wind_Min_exp = [Wind_en_Min_exp[Wind_cap_Min_exp.index(pos)] for pos in marker_x_Wind]
marker_y_Wind_PH_Min = [Wind_PH_en_Min[Wind_cap_Min.index(pos)] for pos in marker_x_Wind]
marker_y_Wind_PH_Min_exp = [Wind_PH_en_Min_exp[Wind_cap_Min_exp.index(pos)] for pos in marker_x_Wind]

Wind_PHES_size = [Wind_PHES_size[Wind_cap_Min.index(pos)] for pos in marker_x_Wind]
Wind_exp_PHES_size = [Wind_exp_PHES_size[Wind_cap_Min_exp.index(pos)] for pos in marker_x_Wind]

#%% resize SW
RE_cap_Base = [x for x in RE_cap_Base if x <= 90 and x>=10]
RE_cap_Base_exp = [x for x in RE_cap_Base_exp if x <= 90 and x>=10]
RE_cap_PH = [x for x in RE_cap_PH if x <= 90 and x>=10]
RE_cap_PH_exp = [x for x in RE_cap_PH_exp if x <= 90 and x>=10]
RE_cap_PH_Min = [x for x in RE_cap_PH_Min if x <= 90 and x>=10]
RE_cap_PH_Min_exp = [x for x in RE_cap_PH_Min_exp if x <= 90 and x>=10]

RE_en_Base = RE_en_Base [:len(RE_cap_Base)]
RE_en_Base_exp = RE_en_Base_exp [:len(RE_cap_Base_exp)]
RE_en_PH = RE_en_PH [:len(RE_cap_PH)]
RE_en_PH_exp = RE_en_PH_exp [:len(RE_cap_PH_exp)]
RE_en_PH_Min = RE_en_PH_Min [:len(RE_cap_PH_Min)]
RE_en_PH_Min_exp = RE_en_PH_Min_exp [:len(RE_cap_PH_Min_exp)]
PH_en_SW_Min = PH_en_SW_Min [:len(RE_cap_PH_Min)]
PH_en_SW_Min_exp = PH_en_SW_Min_exp [:len(RE_cap_PH_Min_exp)]


RE_cap_Base = [round(value, 1) for value in RE_cap_Base]
RE_cap_Base_exp = [round(value, 1) for value in RE_cap_Base_exp]
RE_cap_PH = [round(value, 1) for value in RE_cap_PH]
RE_cap_PH_exp = [round(value, 1) for value in RE_cap_PH_exp]
RE_cap_PH_Min = [round(value, 1) for value in RE_cap_PH_Min]
RE_cap_PH_Min_exp = [round(value, 1) for value in RE_cap_PH_Min_exp]

marker_x_SW = [ 10, 30, 50, 70, 90]


marker_y_RE_Base = [RE_en_Base[RE_cap_Base.index(pos)] for pos in marker_x_SW]
marker_y_RE_Base_exp = [RE_en_Base_exp[RE_cap_Base_exp.index(pos)] for pos in marker_x_SW]
marker_y_RE_PH = [RE_en_PH[RE_cap_PH.index(pos)] for pos in marker_x_SW]
marker_y_RE_PH_exp = [RE_en_PH_exp[RE_cap_PH_exp.index(pos)] for pos in marker_x_SW]
marker_y_RE_Min = [RE_en_PH_Min[RE_cap_PH_Min.index(pos)] for pos in marker_x_SW]
marker_y_RE_Min_exp = [RE_en_PH_Min_exp[RE_cap_PH_Min_exp.index(pos)] for pos in marker_x_SW]
marker_y_RE_PH_Min = [PH_en_SW_Min[RE_cap_PH_Min.index(pos)] for pos in marker_x_SW]
marker_y_RE_PH_Min_exp = [PH_en_SW_Min_exp[RE_cap_PH_Min_exp.index(pos)] for pos in marker_x_SW]


SW_PHES_size = [SW_PHES_size[RE_cap_PH_Min.index(pos)] for pos in marker_x_SW]
SW_exp_PHES_size = [SW_exp_PHES_size[RE_cap_PH_Min_exp.index(pos)] for pos in marker_x_SW]

#%% PLOTS


######################## PHES sizing PH EXP ################################

#plot PHES capacity for Solar
RE_Share = [10, 20, 30, 40, 50, 60, 70, 80, 90]
RE_Share_ticks = [15, 30, 45, 60,75, 90]
x_values = range(len(RE_Share))
fmt = '%.0f%%'
yticks = mtick.FormatStrFormatter(fmt)

fig, ((ax1, ax2, ax14), (ax3,ax5, ax16), (ax9, ax11, ax18))= plt.subplots(3,3, figsize=(56.56,80), sharex=False)

fig.suptitle('Calliope Operation: Nigeria', fontweight='bold', fontsize=80)
plt.subplots_adjust(left=0.025, right=0.95, bottom=0.12, top=0.915, wspace=0.45, hspace=0.30) #per 3 righe

############### plot Solar Energy ##########################
x1=Solar_cap_Base
y1=Solar_en_Base

x2=Solar_cap_Base_exp
y2=Solar_en_Base_exp

x3=Solar_cap_PH
y3=Solar_en_PH

x4=Solar_cap_PH_exp
y4=Solar_en_PH_exp

ax1.plot(x_values, RE_Share, color='#FFFFFF')
custom_ax1ticks = RE_Share_ticks
ax1.set_xticks(marker_x_Solar)
ax1.tick_params(axis='x', labelsize=50, pad=10)
ax1.tick_params(axis='y', labelsize=60)
ax1.set_ylabel('Supply share',size=55)
ax1.yaxis.set_major_formatter(yticks)
ax1.set_yticks(RE_Share_ticks)
ax7 = ax1.twinx()
custom_ax7ticks = Solar_cap_PH_exp
ax7.plot(x1, y1,color='#64b551', linewidth=8, label='RO', marker='o', zorder=3) #verde
ax7.plot(x2, y2,color='#055e24', linewidth=8, label='TE', marker='o') #verde chiaro
ax7.plot(x3, y3, color='#bd7ce6' ,linewidth=12,label='PHES', marker='o', zorder=1) #lilla
ax7.plot(x4, y4, color='#8300d4' ,linewidth=8,label='PHES and TE', marker='o') #viola

ax7.scatter(marker_x_Solar, marker_y_Solar_Base, color='#64b551', s=2000, zorder=3)
ax7.scatter(marker_x_Solar, marker_y_Solar_Base_exp, color='#055e24', s=2000)
ax7.scatter(marker_x_Solar, marker_y_Solar_PH, color='#bd7ce6', s=3000, zorder=1)
ax7.scatter(marker_x_Solar, marker_y_Solar_PH_exp, color='#8300d4', s=2000)

ax1.set_xlabel('Solar Capacity [GW]',size=60, labelpad=30)
ax7.set_ylabel('Solar energy [TWh]',size=55,labelpad=30)
ax7.set_title('100% Solar',  fontweight='bold',fontsize=60, pad=40)
ax7.tick_params(axis='x', labelsize=60)
ax7.tick_params(axis='y', labelsize=60)
ax7.set_ylim(0,0.9*average_supply)
ax7.set_xticks(marker_x_Solar)
ax7.set_xlim(5,95)

legend_Solar = ax7.legend(loc='upper left', prop={'size': 55})

for line in legend_Solar.get_lines():
    line.set_linewidth(8)  #
    line.set_markersize(40)   


################### plot Wind Energy  #####################################

ax2.plot(x_values, RE_Share, color='#FFFFFF')
custom_ax2ticks = RE_Share_ticks
ax2.set_xticks(marker_x_Wind)
ax2.tick_params(axis='x', labelsize=50, pad=15)
ax2.tick_params(axis='y', labelsize=60, pad=15)
ax2.set_ylabel('Supply share',size=55)
ax2.yaxis.set_major_formatter(yticks)
ax2.set_yticks(RE_Share_ticks)

x5=Wind_cap_Base
y5=Wind_en_Base

x6=Wind_cap_Base_exp
y6=Wind_en_Base_exp

x7=Wind_cap_PH
y7=Wind_en_PH

x8=Wind_cap_PH_exp
y8=Wind_en_PH_exp

ax8 = ax2.twinx()
custom_ax8ticks = Wind_cap_Base 
ax8.plot(x5, y5,color='#64b551', linewidth=8, label='RO', marker='o') #verde
ax8.plot(x6, y6,color='#055e24', linewidth=8, label='TE', marker='o') #verde chiaro
ax8.plot(x7, y7, color='#bd7ce6' ,linewidth=8, label='PHES', marker='o') #lilla
ax8.plot(x8, y8, color='#8300d4' ,linewidth=8,label='PHES and TE', marker='o') #viola

ax8.scatter(marker_x_Wind, marker_y_Wind_Base, color='#64b551', s=2000)
ax8.scatter(marker_x_Wind, marker_y_Wind_Base_exp, color='#055e24', s=2000)
ax8.scatter(marker_x_Wind, marker_y_Wind_PH, color='#bd7ce6', s=2000)
ax8.scatter(marker_x_Wind, marker_y_Wind_PH_exp, color='#8300d4', s=2000)

ax2.set_xlabel('Wind Capacity [GW]',size=60, labelpad=30)
ax8.set_ylabel('Wind energy [TWh]',size=55,labelpad=30)
ax8.set_title('100% Wind', fontweight='bold',fontsize=60, pad=50)
ax8.tick_params(axis='x', labelsize=60)
ax8.tick_params(axis='y', labelsize=60)
legend_Wind = ax8.legend(loc='upper left', prop={'size': 55})
ax8.set_xticks(marker_x_Wind)
ax8.set_ylim(0,0.9*average_supply)
ax8.set_xlim(5,95)

for line in legend_Wind.get_lines():
    line.set_linewidth(8)  #
    line.set_markersize(40)   

############### plot SW Energy ##########################
custom_ax14ticks = RE_cap_Base

x10=RE_cap_Base
y1=RE_en_Base

x11=RE_cap_Base_exp
y2=RE_en_Base_exp

x12=RE_cap_PH
y3=RE_en_PH

x13=RE_cap_PH_exp
y4=RE_en_PH_exp

ax14.plot(x_values, RE_Share, color='#FFFFFF')
custom_ax14ticks = RE_Share_ticks
ax14.set_xticks(marker_x_Wind)
ax14.tick_params(axis='x', labelsize=50, pad=10)
ax14.tick_params(axis='y', labelsize=60, pad=15)
ax14.set_ylabel('Supply share',size=55)
ax14.yaxis.set_major_formatter(yticks)
ax14.set_yticks(RE_Share_ticks)

ax15 = ax14.twinx()
ax15.plot(x10, y1,color='#64b551', linewidth=8, marker='o', markersize=1, label='RO') #verde
ax15.plot(x11, y2,color='#055e24', linewidth=8, marker='o', markersize=1,label='TE') #verde chiaro
ax15.plot(x12, y3, color='#bd7ce6' ,linewidth=8,  marker='o', markersize=1, label=f'PHES') #lilla
ax15.plot(x13, y4, color='#8300d4' ,linewidth=8, marker='o', markersize=1, label=f'PHES and TE') #viola

ax15.scatter(marker_x_SW, marker_y_RE_Base, color='#64b551', s=2000)
ax15.scatter(marker_x_SW, marker_y_RE_Base_exp, color='#055e24', s=2000)
ax15.scatter(marker_x_SW, marker_y_RE_PH, color='#bd7ce6', s=2000)
ax15.scatter(marker_x_SW, marker_y_RE_PH_exp, color='#8300d4', s=2000)


ax14.set_xlabel('RE Capacity [GW]',size=60, labelpad=30)
ax15.set_ylabel('RE energy [TWh]',size=55,labelpad=30)
ax15.set_title('Optimal mix: 10% Solar, 90% Wind',  fontweight='bold',fontsize=60, pad=50)
ax15.tick_params(axis='x', labelsize=60, pad=10)
ax15.tick_params(axis='y', labelsize=60, pad=15)
legend_SW =ax15.legend(loc='upper left', prop={'size':55})
ax15.set_ylim(0, 0.9*average_supply)
ax15.set_xticks(marker_x_Wind)
ax15.set_xlim(5,95)

for line in legend_SW.get_lines():
    line.set_linewidth(8)  #
    line.set_markersize(40)
    
######################## PHES sizing PH ################################

#plot PHES capacity for Solar

ax4 = ax3.twinx()

ax3.bar(marker_x_Solar, Solar_PHES_size, color='#5c7ce6',width=8, label='PHES size')
ax3.set_title('Solar with PHES: PHES sizing', fontweight='bold',fontsize=60, pad=50)
ax3.set_ylabel('PHES size [GWh]',size=55)
ax3.set_xlabel('Solar Capacity [GW]',size=60, labelpad=30)
ax3.tick_params(labelsize=50, pad=10)
ax3.set_xticks(marker_x_Solar)
ax3.set_ylim(0,150)
ax3.set_xlim(5,95)

ax4.plot(Solar_cap_Min,Solar_PH_en_Min, linewidth=8,label='PHES Energy',color='#53c9c0', marker='o', markersize=0)
ax4.plot(Solar_cap_Min,Solar_en_Min, linewidth=8,label='Solar Energy',color='#bd7ce6', marker='o', markersize=0)
ax4.set_ylabel('Energy [TWh]',size=55,labelpad=30)
ax4.tick_params(labelsize=50, pad=10)
ax4.set_xlim(5,95)
ax4.set_ylim(0,150)
ax4.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax4.yaxis.set_major_locator(ticker.MultipleLocator(base=50))
ax4.scatter(marker_x_Solar,marker_y_Solar_PH_Min , color='#53c9c0', s=2000)
ax4.scatter(marker_x_Solar,marker_y_Solar_Min , color='#bd7ce6', s=2000)

lines, labels = ax3.get_legend_handles_labels()
lines2, labels2 = ax4.get_legend_handles_labels()
legend_Solar_PH = ax3.legend(lines + lines2, labels + labels2, loc='upper left', prop={'size': 55})

for line in legend_Solar_PH.get_lines():
    line.set_linewidth(8)  #
    line.set_markersize(40)   
    
#plot PHES capacity for Wind

ax5.bar(marker_x_Wind, Wind_PHES_size, color='#5c7ce6',width=8, label='PHES size')
ax5.set_title('Wind with PHES: PHES sizing', fontweight='bold',fontsize=60, pad=50)
ax5.set_ylabel('PHES size [GWh]',size=55)
ax5.set_xlabel('Wind Capacity [GW]',size=60, labelpad=30)
ax5.tick_params(labelsize=50, pad=10)
ax5.set_xlim(5,95)
ax5.set_ylim(0,150)
ax5.set_xticks(marker_x_Wind)


ax6 = ax5.twinx()
ax6.plot(Wind_cap_Min,Wind_PH_en_Min, linewidth=8,label='PHES Energy',color='#53c9c0', marker='o', markersize=0)
ax6.plot(Wind_cap_Min,Wind_en_Min, linewidth=8,label='Wind Energy',color='#bd7ce6', marker='o', markersize=0)
ax6.scatter(marker_x_Wind,marker_y_Wind_PH_Min , color='#53c9c0', s=2000)
ax6.scatter(marker_x_Wind,marker_y_Wind_Min , color='#bd7ce6', s=2000)
ax6.set_ylabel('Energy [TWh]',size=55,labelpad=30)
ax6.tick_params(labelsize=50, pad=10)
ax6.set_ylim(0,250)


lines, labels = ax5.get_legend_handles_labels()
lines2, labels2 = ax6.get_legend_handles_labels()
legend_Wind_PH = ax5.legend(lines + lines2, labels + labels2, loc='upper left', prop={'size': 55})
ax6.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax6.yaxis.set_major_locator(ticker.MultipleLocator(base=50))

for line in legend_Wind_PH.get_lines():
    line.set_linewidth(8)  #
    line.set_markersize(40)
    
# plot PHES capacity SW

ax17 = ax16.twinx()

ax16.bar(marker_x_SW, SW_PHES_size, color='#5c7ce6',width=8, label='PHES size')
custom_ax16ticks = RE_cap_PH_Min
ax16.set_title('Optimal mix with PHES: PHES sizing', fontweight='bold',fontsize=60, pad=50)
ax16.set_ylabel('PHES size [GWh]',size=55)
ax16.set_xlabel('RE Capacity [GW]',size=60, labelpad=30)
ax16.tick_params(labelsize=50, pad=10)
ax16.set_xticks(marker_x_Wind)
ax16.set_ylim(0,150)

ax17.plot(RE_cap_PH_Min,PH_en_SW_Min, linewidth=8,label='PHES Energy',color='#53c9c0', marker='o', markersize=0)
ax17.plot(RE_cap_PH_Min,RE_en_PH_Min, linewidth=8,label='RE Energy',color='#bd7ce6', marker='o', markersize=0)
ax17.scatter(marker_x_SW,marker_y_RE_PH_Min , color='#53c9c0', s=2000)
ax17.scatter(marker_x_SW,marker_y_RE_Min , color='#bd7ce6', s=2000)
ax17.set_ylabel('Energy [TWh]',size=55,labelpad=30)
ax17.tick_params(labelsize=50, pad=10)
ax17.set_xlim(5,95)
ax17.set_ylim(0,250)
ax17.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax17.yaxis.set_major_locator(ticker.MultipleLocator(base=50))


lines, labels = ax16.get_legend_handles_labels()
lines2, labels2 = ax17.get_legend_handles_labels()
legend_SW_PH = ax16.legend(lines + lines2, labels + labels2, loc='upper left', prop={'size': 55})

for line in legend_SW_PH.get_lines():
    line.set_linewidth(8)  #
    line.set_markersize(40)    
    
################### PHES sizing PH exp ################################

#plot PHES capacity for Solar exp



ax9.bar(marker_x_Solar, Solar_exp_PHES_size, color='#5c7ce6',width=8, label='PHES size')
ax9.set_title('Solar with PHES and TE: \n PHES sizing', fontweight='bold',fontsize=60, pad=50)
ax9.set_ylabel('PHES size [GWh]',size=55)
ax9.set_xlabel('Solar Capacity [GW]',size=60, labelpad=30)
ax9.tick_params(labelsize=50, pad=10)
ax9.set_xticks(marker_x_Solar)
ax9.set_ylim(0,330)
ax9.set_xlim(5,95)

ax10 = ax9.twinx()

ax10.plot(Solar_cap_Min_exp,Solar_PH_en_Min_exp, linewidth=8,label='PHES Energy',color='#53c9c0', marker='o', markersize=0)
ax10.plot(Solar_cap_Min_exp,Solar_en_Min_exp, linewidth=8,label='Solar Energy',color='#8300d4', marker='o', markersize=0)
ax10.set_ylabel('Energy [TWh]',size=55,labelpad=30)
ax10.scatter(marker_x_Solar,marker_y_Solar_PH_Min_exp , color='#53c9c0', s=2000)
ax10.scatter(marker_x_Solar,marker_y_Solar_Min_exp , color='#8300d4', s=2000)
ax10.tick_params(labelsize=50, pad=10)
ax10.set_ylim(0,250)

lines, labels = ax9.get_legend_handles_labels()
lines2, labels2 = ax10.get_legend_handles_labels()
legend_Solar_PH_exp = ax9.legend(lines + lines2, labels + labels2, loc='upper left', prop={'size': 55})

for line in legend_Solar_PH_exp.get_lines():
    line.set_linewidth(8)  #
    line.set_markersize(40)    
    
#plot PHES capacity for Wind exp

ax11.bar(marker_x_Wind, Wind_exp_PHES_size, color='#5c7ce6',width=8, label='PHES size')
ax11.set_title('Wind with PHES and TE: \n PHES sizing', fontweight='bold',fontsize=60, pad=50)
ax11.set_ylabel('PHES size [GWh]',size=55)
ax11.set_xlabel('Wind Capacity [GW]',size=60, labelpad=30)
ax11.tick_params(labelsize=50, pad=10)
ax11.set_xticks(marker_x_Wind)
ax11.set_ylim(0,330)
ax11.set_xlim(5,95)

ax12 = ax11.twinx()
ax12.plot(Wind_cap_Min_exp,Wind_PH_en_Min_exp, linewidth=8,label='PHES Energy',color='#53c9c0', marker='o', markersize=0)
ax12.plot(Wind_cap_Min_exp,Wind_en_Min_exp, linewidth=8,label='Wind Energy',color='#8300d4', marker='o', markersize=0)
ax12.scatter(marker_x_Wind,marker_y_Wind_PH_Min_exp , color='#53c9c0', s=2000)
ax12.scatter(marker_x_Wind,marker_y_Wind_Min_exp , color='#8300d4', s=2000)
ax12.set_ylabel('Energy [TWh]',size=55,labelpad=30)
ax12.tick_params(labelsize=50, pad=10)
ax12.set_ylim(0,250)

lines, labels = ax11.get_legend_handles_labels()
lines2, labels2 = ax12.get_legend_handles_labels()
legend_Wind_PH_exp = ax11.legend(lines + lines2, labels + labels2, loc='upper left', prop={'size': 55})

for line in legend_Wind_PH_exp.get_lines():
    line.set_linewidth(8)  #
    line.set_markersize(40)    
    
#plot PHES capacity

ax19 = ax18.twinx()

ax18.bar(marker_x_SW, SW_exp_PHES_size, color='#5c7ce6',width=8, label='PHES size')
custom_ax18ticks = RE_cap_PH_Min_exp
ax18.set_title('Optimal mix with PHES and TE: \n PHES sizing', fontweight='bold',fontsize=60, pad=50)
ax18.set_ylabel('PHES size [GWh]',size=55)
ax18.set_xlabel('RE Capacity [GW]',size=60, labelpad=30)
ax18.tick_params(labelsize=50, pad=10)
ax18.set_xticks(marker_x_Wind)
ax18.set_ylim(0,330)
ax18.set_xlim(5,95)

ax19.plot(RE_cap_PH_Min_exp,PH_en_SW_Min_exp, linewidth=8,label='PHES Energy',color='#53c9c0', marker='o', markersize=0)
ax19.plot(RE_cap_PH_Min_exp,RE_en_PH_Min_exp, linewidth=8,label='RE Energy',color='#8300d4', marker='o', markersize=0)
ax19.scatter(marker_x_SW,marker_y_RE_PH_Min_exp , color='#53c9c0', s=2000)
ax19.scatter(marker_x_SW,marker_y_RE_Min_exp , color='#8300d4', s=2000)
ax19.set_ylabel('Energy [TWh]',size=55,labelpad=30)
ax19.tick_params(labelsize=50, pad=10)
ax19.set_xlim(5,95)
ax19.set_ylim(0,250)
ax19.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax19.yaxis.set_major_locator(ticker.MultipleLocator(base=50))


lines, labels = ax18.get_legend_handles_labels()
lines2, labels2 = ax19.get_legend_handles_labels()
legend_SW_PH_exp = ax18.legend(lines + lines2, labels + labels2, loc='upper left', prop={'size': 55})

for line in legend_SW_PH_exp.get_lines():
    line.set_linewidth(8)  #
    line.set_markersize(40)    
    
plt.show()







