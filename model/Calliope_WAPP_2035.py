# Multi-nodal model of the West African Power Pool
#Multiple-scenarios on transmission expansion and storage technologies to evaluate renewables integration

import calliope

try:
    calliope.set_log_level('Error')
except:
    calliope.set_log_verbosity('Error')

#Scenarios at 2035 Autarky

#1
model = calliope.Model('model_2035.yaml', scenario='2035_onlyRES_autarky_BESS')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_onlyRES_autarky_BESS', dropna=True) 

#2
model = calliope.Model('model_2035.yaml', scenario='2035_onlyRES_autarky_PHES')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_onlyRES_autarky_PHES', dropna=True) 

#3
model = calliope.Model('model_2035.yaml', scenario='2035_onlyRES_autarky_NoStorage')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_onlyRES_autarky_NoStorage', dropna=True) 

#4
model = calliope.Model('model_2035.yaml', scenario='2035_RES+GT_autarky_BESS')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_RES+GT_autarky_BESS', dropna=True) 

#5
model = calliope.Model('model_2035.yaml', scenario='2035_RES+GT_autarky_PHES')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_RES+GT_autarky_PHES', dropna=True) 

#6
model = calliope.Model('model_2035.yaml', scenario='2035_RES+GT_autarky_NoStorage')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_RES+GT_autarky_NoStorage', dropna=True) 

#Scenarios at 2035 Existing and planned connections

#7
model = calliope.Model('model_2035.yaml', scenario='2035_onlyRES_transmission_BESS')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_onlyRES_transmission_BESS', dropna=True) 

#8
model = calliope.Model('model_2035.yaml', scenario='2035_onlyRES_transmission_PHES')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_onlyRES_transmission_PHES', dropna=True) 

#9
model = calliope.Model('model_2035.yaml', scenario='2035_onlyRES_transmission_NoStorage')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_onlyRES_transmission_NoStorage', dropna=True) 

#10
model = calliope.Model('model_2035.yaml', scenario='2035_RES+GT_transmission_BESS')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_RES+GT_transmission_BESS', dropna=True) 

#11
model = calliope.Model('model_2035.yaml', scenario='2035_RES+GT_transmission_PHES')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_RES+GT_transmission_PHES', dropna=True) 

#12
model = calliope.Model('model_2035.yaml', scenario='2035_RES+GT_transmission_NoStorage')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_RES+GT_transmission_NoStorage', dropna=True) 

#Scenarios at 2035 Free expansion

#13
model = calliope.Model('model_2035.yaml', scenario='2035_onlyRES_transmission_exp_BESS')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_onlyRES_transmission_exp_BESS', dropna=True) 

#14
model = calliope.Model('model_2035.yaml', scenario='2035_onlyRES_transmission_exp_PHES')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_onlyRES_transmission_exp_PHES', dropna=True) 

#15
model = calliope.Model('model_2035.yaml', scenario='2035_onlyRES_transmission_exp_NoStorage')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_onlyRES_transmission_exp_NoStorage', dropna=True) 

#16
model = calliope.Model('model_2035.yaml', scenario='2035_RES+GT_transmission_exp_BESS')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_RES+GT_transmission_exp_BESS', dropna=True) 

#17
model = calliope.Model('model_2035.yaml', scenario='2035_RES+GT_transmission_exp_PHES')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_RES+GT_transmission_exp_PHES', dropna=True) 

#18
model = calliope.Model('model_2035.yaml', scenario='2035_RES+GT_transmission_exp_NoStorage')
model.run()      

model.to_csv('/global-scratch/bulk_pool/vbaiocco/Calliope/WAPP/Results_2035/ResultsWAPP_2035_RES+GT_transmission_exp_NoStorage', dropna=True) 