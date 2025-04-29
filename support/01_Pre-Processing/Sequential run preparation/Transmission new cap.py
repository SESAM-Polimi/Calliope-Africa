import pandas as pd
from ruamel.yaml import YAML
import copy

# Define YAML instance
yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=4, sequence=4, offset=2)

# Paths and scenario names
folder_path = 'C:/Users/user/OneDrive - Politecnico di Milano/DallaRiva - CalliopePowerPools/06-Results/Results_2030/ResultsWAPP_'
scenario_names = [
    '2030_onlyRES_transmission_exp_NoStorage',
    '2030_onlyRES_transmission_exp_BESS',
    '2030_onlyRES_transmission_exp_PHES',
    '2030_RES+GT_transmission_exp_NoStorage',
    '2030_RES+GT_transmission_exp_BESS',
    '2030_RES+GT_transmission_exp_PHES'
]
input_yaml_path = 'new_transmission.yaml'

# Step 2: Read the existing YAML file using ruamel.yaml

yaml = YAML()
yaml.preserve_quotes = True  # Preserve quotes around values
yaml.indent(mapping=4, sequence=4, offset=2)  # Customize indentation

# Load the initial YAML file
with open(input_yaml_path, 'r') as file:
    base_yaml_data = yaml.load(file)
    
# Process each scenario
for scenario_name in scenario_names:
    csv_path = folder_path + scenario_name + "/results_energy_cap.csv"
    distance_path = folder_path + scenario_name + "/inputs_distance.csv"
    transmission_data = pd.read_csv(csv_path)
    distance_data = pd.read_csv(distance_path)
    # Filter rows where 'techs' contains "transmission"
    transmission_data = transmission_data[
    (transmission_data['techs'].str.contains("kV", na=False)) & 
    (transmission_data['techs'].str.contains("new", na=False)) &
    (transmission_data['energy_cap']!= 0)
]
    # Make a deep copy of the base YAML data for modification
    yaml_data = copy.deepcopy(base_yaml_data)

    # Update the YAML data
    for _, row in transmission_data.iterrows():
        loc=row['locs']
        tech_name = row['techs']
        energy_cap = row['energy_cap']
        location2 = tech_name.split(":")[-1].strip()
        link_key = f"{loc},{location2}"
        new_tech_name= '300-330_kV_installed_2030'

        # Get distance value safely
        distance_row = distance_data[
            (distance_data['techs'] == tech_name) & (distance_data['locs'] == loc)
        ]
        distance = distance_row['distance'].values[0] if not distance_row.empty else None

        # Iterate through YAML links to find the corresponding location
        for location, loc_data in yaml_data.get('links', {}).items():
            if link_key in location:  # Ensure matching locations
                
                new_tech_constraints = {
                                'energy_cap_equals': energy_cap,
                                'energy_eff_per_distance': 0.99
                            }
                yaml_data['links'][link_key]['techs'][new_tech_name] = {
                    'constraints': new_tech_constraints,
                }
                # Set distance correctly outside constraints
                if distance is not None:
                    yaml_data['links'][link_key]['techs'][new_tech_name]['distance'] = float(distance)  # Ensure it's a float


    # Save the updated YAML file
    output_yaml_path = f'Updated_Transmission_WAPP_{scenario_name}.yaml'
    with open(output_yaml_path, 'w') as file:
        yaml.dump(yaml_data, file)  # Use ruamel.yaml's dump method

    print(f"Updated YAML file saved for scenario '{scenario_name}' at {output_yaml_path}")

print("Processing completed for all scenarios.")
