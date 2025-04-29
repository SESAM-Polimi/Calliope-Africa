import pandas as pd
from ruamel.yaml import YAML
import copy

# Step 1: Load the CSV file with MSR data
folder_path = 'C:/Users/user/OneDrive - Politecnico di Milano/DallaRiva - CalliopePowerPools/06-Results/Results_2030/ResultsWAPP_'

# List of scenario names
scenario_names = [
    '2030_onlyRES_autarky_PHES',
    '2030_onlyRES_transmission_PHES',
    '2030_onlyRES_transmission_exp_PHES',
    '2030_RES+GT_autarky_PHES',
    '2030_RES+GT_transmission_PHES',
    '2030_RES+GT_transmission_exp_PHES'
]

# Step 2: Read the existing YAML file using ruamel.yaml
input_yaml_path = 'Storage_PHES.yaml'  # Replace with the actual file path
yaml = YAML()
yaml.preserve_quotes = True  # Preserve quotes around values
yaml.indent(mapping=4, sequence=4, offset=2)  # Customize indentation

# Load the initial YAML file
with open(input_yaml_path, 'r') as file:
    base_yaml_data = yaml.load(file)

# Process each scenario
for scenario_name in scenario_names:
    # Step 1: Load the CSV file for the current scenario
    csv_path = folder_path + scenario_name + "/results_energy_cap.csv"
    storage_data = pd.read_csv(csv_path)

    # Filter rows where 'techs' contains "PHES" and 'energy_cap' is not zero
    storage_data = storage_data[(storage_data['techs'].str.contains("PHES", na=False)) & (storage_data['energy_cap'] != 0)]

    # Make a deep copy of the base YAML data for modification
    yaml_data = copy.deepcopy(base_yaml_data)

    # Step 2: Update the YAML data with values from the CSV
    for _, row in storage_data.iterrows():
        loc_name = row['locs']
        tech_name = row['techs']
        energy_cap = row['energy_cap']

        if loc_name in yaml_data.get('locations', {}):
            tech_data = yaml_data['locations'][loc_name].get('techs', {})

            # Update the existing tech's maximum capacity
            if tech_name in tech_data:
                constraints = tech_data[tech_name].get('constraints', {})
                original_max=constraints['energy_cap_max']
                new_max = max(0, original_max - energy_cap)
                constraints['energy_cap_max'] = new_max
                tech_data[tech_name]['constraints'] = constraints

            # Add the new tech representing the installed capacity
            new_tech_name = f"{tech_name}_2030_installed"
            if new_tech_name not in tech_data:
                new_tech_constraints = {
                    'energy_cap_equals': energy_cap,
                    'energy_cap_per_storage_cap_equals': 0.16666666667
                }
                
                # Add the new tech
                tech_data[new_tech_name] = {
                    'constraints': new_tech_constraints
                }


    # Step 3: Write the updated YAML back to a new file
    output_yaml_path = f'Storage_{scenario_name}.yaml'
    with open(output_yaml_path, 'w') as file:
        yaml.dump(yaml_data, file)

    print(f"Updated YAML file saved for scenario '{scenario_name}' at {output_yaml_path}")

print("Processing completed for all scenarios.")