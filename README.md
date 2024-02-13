
Storage and Transmission
=========================

Calliope energy model to asses the impact of introducing renewable energy technologies and ancillary services to promote their utilization within the energy system.

__Model_run.py__
--------


Two renewable energy technologies are considered: solar photovoltaic and wind turbines, and two different ancillary services: expanding the grid capacity and installing storage capacity. The scenarios defined are the linear combination of the variation of three variables: 

- Renewable energy mix introduced: varying from 100\% solar to 100\% wind by 10\% steps. 
```bash
  share=[0, 0.1, 0.2, 0.3, 0.4,0.5, 0.6, 0.7, 0.8, 0.9, 1] #share of solar capacity over overall added capacity
```

- Amount of additional renewable capacity introduced: from 0 MW (base case) to the double of the overall exisitng national supply capacity.
```bash
capacity=[10000, ... ,25000] #in MW

#i.e for capacity: 1000MW and share: 0.5 500MW of solar and 500MW of Wind will be added to the system
```
- Integration strategy adopted: Renewables Only (RO), Transmission Expansion (TE), Pumped Hydro Storage (PHES), Pumped Hydro Storage and Transmission Expansion (PHES and TE). Depending on the selected integration strategy, unique values and technologies are incorporated into the model. The PHES capacity introduced in the model corresponds to the maxium PHES capacity available in the region where PHES is placed.


```bash
integration_strategies = ['RO', 'TE', 'PHES','PHES_TE' ]      
```
```bash
strategy_definition = {
    'RO': {'model_file': 'model_transmission.yaml', 'PHES_cap': 0, 'PHES_en': 0},
    'TE': {'model_file': 'model_transmission_exp.yaml', 'PHES_cap': 0, 'PHES_en': 0},
    'PHES': {'model_file': 'model_transmission.yaml', 'PHES_cap': 600000000, 'PHES_en': 3600000000},       #PHES capacity and energy in kW
    'PHES_TE': {'model_file': 'model_transmission_exp.yaml', 'PHES_cap': 600000000, 'PHES_en': 3600000000} #PHES capacity and energy in kW
}
```
Once the user defines the parameters __shares__ and __capacities__, and selects the desired integration strategies in __integration_strategies__, the code proceeds to run the model in operation mode. An  optimization based on minimizing system costs is performed providing the optimal generation mix.


__Run_min_PH.py__
------------
The code enables the calculation of the minimum storage size required to match the energy generation achieved when the storage size is set to its maximum available capacity, as obtained from the results generated by _'model_run.py'_.

After the user specifies the capacities (__capacity_values__), shares (__shares__), and integration strategy (__integration_strategies__) for which they wish to calculate the minimum storage size, the code is ready to execute. It's important to note that the model only functions for integration strategies involving PHES, hence only the _PHES_ and _PHES_TE_ scenarios Additionally, the model requires the results generated by _'model_run.py'_ beforehand; otherwise, a __FileNotFoundError__ will be raised.