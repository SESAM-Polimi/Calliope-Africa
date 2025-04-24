
# Pre - Processing

The pre-processing folder is used for the geographical explicit representation of VRES potential sites.
The **cluster creation** groups similar Model Supply Regions (MSRs), provided by IRENA, into clusters.
**Cluster to YAML** converts the MSRs input file (.csv) into a YAML format ready to be inserted into the Calliope inputs.
- The country list has to correctly represent the MSRs countries: '' 'country_code_mapping = {"Benin": "BEN", "BurkinaFaso": "BFA", "IvoryCoast": "CIV", "Gambia": "GMB", "Ghana": "GHA", "Guinea": "GIN", "Guinea-Bissau": "GNB", "Liberia": "LBR", "Mali": "MLI", "Niger": "NER", "Nigeria_East": "NGA_E", "Nigeria_North": "NGA_CNW","Senegal": "SEN", "SierraLeone": "SLE", "Togo": "TGO" # Add other countries and their codes here}' ''

- Technology parameters can be changed here: 

```python
    def create_yaml_tech(row, country_code):
        entry = {
            f"PV_{country_code}_MSR{row['MSR_ID']}": {
                "essentials": {
                    "color": "#FFA52B",
                    "name": f"PV Power Plant {country_code} {row['MSR_ID']}",
                    "parent": "supply_plus",
                    "carrier_out": "power"
                },
                "constraints": {
                    "resource": "inf",
                    "lifetime": 25,
                    "force_resource": True
                },
                "costs": {
                    "monetary": {
                        "energy_cap": 1070 + row['trCAPEX-kW'],
                        "om_annual": 20,
                        "interest_rate": 0.10
                    },
                    "co2": {
                        "om_prod": 0
                    }
                }
            }
        }
        return entry
```

**Sequential running approach** extract the results of the previous run (i.e installed capacity of new technologies) and creates a YAML file that can be used to overwrite Calliope inputs for each scenario.

## Graph creation
The file *graphs.ipynb* extract from the results folders the chosen results for each scenario and grouped them in .csv files.
Those files are then used as input to create graphs for a clearer data visualization.

### Post - Processing
This folder contains codes used to obtain particular data from the Calliope results folders and report them on graphs or excel files for better interpretation.