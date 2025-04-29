# WAPP Planning

This project utilizes the Calliope energy system modeling framework to support energy transition planning within the West African Power Pool (WAPP) region.
It investigates the integration of variable renewable energy sources (solar and wind) with a geographical explicit representation of the potential sites.
The potential sites are obtained by adopting the Model Supply Regions (MSRs) developed by IRENA. As reference: https://doi.org/10.1038/s41597-022-01786-5 
The  starting MSRs dataset is available at: https://doi.org/10.5281/zenodo.14870967

The model also includes grid flexibility enablers such as natural gas-fired power plant, the possibility to expand regional interconnectors and storage technologies (BESS and PHES).

## Structure
The folder **model** contains the Calliope model. The analysis is conducted with a sequential running approach within a 5-years intervals. Therefore, there are different inputs for the 2030, 2035 and 2040 runs. The file *overrides.YAML* ensures that for each scenario the correct inputs are overwritten on the starting energy system.

The folder **support** contains complementaries to use the model.
