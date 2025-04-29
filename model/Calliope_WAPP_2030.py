#Multi-nodal model of the West African Power Pool
#Multiple-scenarios on transmission expansion and storage technologies to evaluate renewables integration

import calliope
import gc

try:
    calliope.set_log_level('Error')
except:
    calliope.set_log_verbosity('Error')

#Scenarios at 2030 Autarky

#1
model = calliope.Model('model_2030.yaml', scenario='2030_onlyRES_autarky_BESS')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_onlyRES_autarky_BESS', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#2
model = calliope.Model('model_2030.yaml', scenario='2030_onlyRES_autarky_PHES')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_onlyRES_autarky_PHES', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#3
model = calliope.Model('model_2030.yaml', scenario='2030_onlyRES_autarky_NoStorage')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_onlyRES_autarky_NoStorage', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#4
model = calliope.Model('model_2030.yaml', scenario='2030_RES+GT_autarky_BESS')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_RES+GT_autarky_BESS', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#5
model = calliope.Model('model_2030.yaml', scenario='2030_RES+GT_autarky_PHES')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_RES+GT_autarky_PHES', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#6
model = calliope.Model('model_2030.yaml', scenario='2030_RES+GT_autarky_NoStorage')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_RES+GT_autarky_NoStorage', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#Scenarios at 2030 Existing and planned connections

#7
model = calliope.Model('model_2030.yaml', scenario='2030_onlyRES_transmission_BESS')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_onlyRES_transmission_BESS', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#8
model = calliope.Model('model_2030.yaml', scenario='2030_onlyRES_transmission_PHES')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_onlyRES_transmission_PHES', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#9
model = calliope.Model('model_2030.yaml', scenario='2030_onlyRES_transmission_NoStorage')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_onlyRES_transmission_NoStorage', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#10
model = calliope.Model('model_2030.yaml', scenario='2030_RES+GT_transmission_BESS')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_RES+GT_transmission_BESS', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#11
model = calliope.Model('model_2030.yaml', scenario='2030_RES+GT_transmission_PHES')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_RES+GT_transmission_PHES', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#12
model = calliope.Model('model_2030.yaml', scenario='2030_RES+GT_transmission_NoStorage')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_RES+GT_transmission_NoStorage', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#Scenarios at 2030 Free expansion

#13
model = calliope.Model('model_2030.yaml', scenario='2030_onlyRES_transmission_exp_BESS')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_onlyRES_transmission_exp_BESS', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#14
model = calliope.Model('model_2030.yaml', scenario='2030_onlyRES_transmission_exp_PHES')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_onlyRES_transmission_exp_PHES', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#15
model = calliope.Model('model_2030.yaml', scenario='2030_onlyRES_transmission_exp_NoStorage')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_onlyRES_transmission_exp_NoStorage', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#16
model = calliope.Model('model_2030.yaml', scenario='2030_RES+GT_transmission_exp_BESS')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_RES+GT_transmission_exp_BESS', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#17
model = calliope.Model('model_2030.yaml', scenario='2030_RES+GT_transmission_exp_PHES')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_RES+GT_transmission_exp_PHES', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()

#18
model = calliope.Model('model_2030.yaml', scenario='2030_RES+GT_transmission_exp_NoStorage')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/ResultsWAPP_2030_RES+GT_transmission_exp_NoStorage', dropna=True) 
# Clean up backend resources
model.backend_model.dispose()

# Clean up memory
del model
gc.collect()