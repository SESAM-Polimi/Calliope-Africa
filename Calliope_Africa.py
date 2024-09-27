#%%  Multi-nodal model of the African continent as of 2021

import calliope

try:
    calliope.set_log_level('Error')
except:
    calliope.set_log_verbosity('Error')

# model = calliope.Model('model.yaml')
model = calliope.Model('model.yaml')
model.run()   


#%%
model.to_csv('results', dropna=True) 
model.to_netcdf('results.nc')