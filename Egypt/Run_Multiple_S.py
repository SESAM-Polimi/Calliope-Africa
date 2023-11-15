# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 14:36:38 2023

@author: baioc
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 16:44:46 2022

@author: baioc
"""
import calliope

try:
    calliope.set_log_level('INFO')
except:
    calliope.set_log_verbosity('Error')
      
#%% 
import pandas as pd

demand = pd.read_csv('Timeseries/Demand.csv')
demand_tot=-(demand.loc[:,'EGY_NE'].sum()+demand.loc[:,'EGY_AL'].sum()+demand.loc[:,'EGY_ME'].sum()
             +demand.loc[:,'EGY_CR'].sum()+demand.loc[:,'EGY_UE'].sum()+demand.loc[:,'EGY_CN'].sum())*1e-9

demand_NE = -demand.loc[:,'EGY_NE'].sum()*1e-9

demand_CN = -demand.loc[:,'EGY_CN'].sum()*1e-9

demand_UE = -demand.loc[:,'EGY_UE'].sum()*1e-9

demand_CR = -demand.loc[:,'EGY_CR'].sum()*1e-9

demand_AL = -demand.loc[:,'EGY_AL'].sum()*1e-9

demand_ME = -demand.loc[:,'EGY_ME'].sum()*1e-9

#%% Original

model = calliope.Model('model_multiple_S_CO2.yaml', scenario='Original')
model.run()
model.to_csv('Original_CO2_2.0')

#%%
import pandas as pd

cost_var=pd.read_csv('Original_CO2/results_cost_var.csv')
co2=cost_var.loc[cost_var['costs']=='co2'].loc[:,'cost_var'].sum()*1e-9

#%% 500
model = calliope.Model('model_multiple_S.yaml', scenario='500MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-500MW')

#%% 1000
model = calliope.Model('model_multiple_S.yaml', scenario='1000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-1000MW')

#%% 5000
model = calliope.Model('model_multiple_S.yaml', scenario='5000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-5000MW')

#%% 7500
model = calliope.Model('model_multiple_S.yaml', scenario='7500MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-7500MW')

#%% 10000
model = calliope.Model('model_multiple_S.yaml', scenario='10000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-10000MW')

#%% 15000
model = calliope.Model('model_multiple_S.yaml', scenario='15000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-15000MW')

#%% 20000
model = calliope.Model('model_multiple_S.yaml', scenario='20000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-20000MW')

#%% 25000
model = calliope.Model('model_multiple_S.yaml', scenario='25000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-25000MW')

#%% 30000
model = calliope.Model('model_multiple_S.yaml', scenario='30000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-30000MW')
#%% 35000
model = calliope.Model('model_multiple_S.yaml', scenario='35000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-35000MW')
#%% 40000
model = calliope.Model('model_multiple_S.yaml', scenario='40000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-40000MW')

#%% 45000
model = calliope.Model('model_multiple_S.yaml', scenario='45000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-45000MW')

#%% 50000
model = calliope.Model('model_multiple_S.yaml', scenario='50000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-50000MW')
#%% 60000
model = calliope.Model('model_multiple_S.yaml', scenario='60000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-60000MW')

#%% 70000
model = calliope.Model('model_multiple_S.yaml', scenario='70000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-70000MW')
#%% 80000
model = calliope.Model('model_multiple_S.yaml', scenario='80000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-80000MW')
#%% 90000
model = calliope.Model('model_multiple_S.yaml', scenario='90000MW')
model.run()
model.to_csv('Results/Base_exp_Solar/Base_exp_Solar-90000MW')

#%% 100000
model = calliope.Model('model_multiple_S.yaml', scenario='100000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-100000MW')
#%% 125000
model = calliope.Model('model_multiple_S.yaml', scenario='125000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-125000MW')

#%% 150000
model = calliope.Model('model_multiple_S.yaml', scenario='150000MW')
model.run()
model.to_csv('Results/Base_exp_SW/SW_1.0%/Base_exp_Solar-150000MW')

