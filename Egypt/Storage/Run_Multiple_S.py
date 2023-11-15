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
      

#%% 500
model = calliope.Model('model_multiple_S.yaml', scenario='500MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-500MW')

#%% 1000
model = calliope.Model('model_multiple_S.yaml', scenario='1000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-1000MW')

#%% 5000
model = calliope.Model('model_multiple_S.yaml', scenario='5000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-5000MW')

#%% 7500
model = calliope.Model('model_multiple_S.yaml', scenario='7500MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-7500MW')

#%% 10000
model = calliope.Model('model_multiple_S.yaml', scenario='10000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-10000MW')

#%% 12500
model = calliope.Model('model_multiple_S.yaml', scenario='15000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-15000MW')

#%% 15000
model = calliope.Model('model_multiple_S.yaml', scenario='12500MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-12500MW')

#%% 20000
model = calliope.Model('model_multiple_S.yaml', scenario='20000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-20000MW')

#%% 25000
model = calliope.Model('model_multiple_S.yaml', scenario='25000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-25000MW')

#%% 30000
model = calliope.Model('model_multiple_S.yaml', scenario='30000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-30000MW')
#%% 35000
model = calliope.Model('model_multiple_S.yaml', scenario='35000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-35000MW')

#%% 40000
model = calliope.Model('model_multiple_S.yaml', scenario='40000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-40000MW')

#%% 45000
model = calliope.Model('model_multiple_S.yaml', scenario='45000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-45000MW')

#%% 50000
model = calliope.Model('model_multiple_S.yaml', scenario='50000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-50000MW')

#%% 60000
model = calliope.Model('model_multiple_S.yaml', scenario='60000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-60000MW')
#%% 70000
model = calliope.Model('model_multiple_S.yaml', scenario='70000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-70000MW')
#%% 80000
model = calliope.Model('model_multiple_S.yaml', scenario='80000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-80000MW')
#%% 90000
model = calliope.Model('model_multiple_S.yaml', scenario='90000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-90000MW')
#%% 100000
model = calliope.Model('model_multiple_S.yaml', scenario='100000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-100000MW')
#%% 115000
model = calliope.Model('model_multiple_S.yaml', scenario='115000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-115000MW')
#%% 125000
model = calliope.Model('model_multiple_S.yaml', scenario='125000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-125000MW')
#%% 150000
model = calliope.Model('model_multiple_S.yaml', scenario='150000MW')
model.run()
model.to_csv('Results/PH_SW/SW_1.0%/PH_Solar-150000MW')