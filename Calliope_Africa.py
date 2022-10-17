# Multi-nodal model of the African continent as of 2021

import calliope

try:
    calliope.set_log_level('Error')
except:
    calliope.set_log_verbosity('Error')

#model = calliope.Model('model.yaml')
model = calliope.Model('model_S.yaml', scenario='2040_AC')
model.run()      
model.to_csv('ResultsAfrica_AC5', dropna=True) 
model.to_netcdf('ResultsAfrica_AC51')