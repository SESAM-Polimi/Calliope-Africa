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
    '2030_onlyRES_autarky_NoStorage',
    '2030_onlyRES_autarky_BESS',
    '2030_onlyRES_autarky_PHES',
    '2030_onlyRES_transmission_NoStorage',
    '2030_onlyRES_transmission_BESS',
    '2030_onlyRES_transmission_PHES',
    '2030_onlyRES_transmission_exp_NoStorage',
    '2030_onlyRES_transmission_exp_BESS',
    '2030_onlyRES_transmission_exp_PHES',
    '2030_RES+GT_autarky_NoStorage',
    '2030_RES+GT_autarky_BESS',
    '2030_RES+GT_autarky_PHES',
    '2030_RES+GT_transmission_NoStorage',
    '2030_RES+GT_transmission_BESS',
    '2030_RES+GT_transmission_PHES',
    '2030_RES+GT_transmission_exp_NoStorage',
    '2030_RES+GT_transmission_exp_BESS',
    '2030_RES+GT_transmission_exp_PHES'    
]
input_yaml_path = 'Location_Constraints_WAPP.yaml'

# Load the initial YAML file
with open(input_yaml_path, 'r') as file:
    base_yaml_data = yaml.load(file)

# Process each scenario
for scenario_name in scenario_names:
    csv_path = folder_path + scenario_name + "/results_energy_cap.csv"
    msr_data = pd.read_csv(csv_path)

    # Filter rows where 'techs' contains "MSR" and 'energy_cap' is not zero
    msr_data = msr_data[(msr_data['techs'].str.contains("MSR", na=False)) & (msr_data['energy_cap'] != 0)]

    # Make a copy of the base YAML data for modification
    yaml_data = copy.deepcopy(base_yaml_data)

    # Update the YAML data
    for _, row in msr_data.iterrows():
        tech_name = row['techs']
        energy_cap = row['energy_cap']

        for location, loc_data in yaml_data.get('locations', {}).items():
            if 'techs' in loc_data and tech_name in loc_data['techs']:
                tech_data = loc_data['techs'][tech_name]

                # Update the existing tech's maximum capacity
                if 'constraints' in tech_data and 'energy_cap_max' in tech_data['constraints']:
                    original_max = tech_data['constraints']['energy_cap_max']
                    new_max = max(0, original_max - energy_cap)
                    tech_data['constraints']['energy_cap_max'] = new_max

                # Add the new tech representing the installed capacity
                new_tech_name = f"{tech_name}_2030_installed"
                if new_tech_name not in loc_data['techs']:
                    new_tech_constraints = {
                        'energy_cap_equals': energy_cap
                    }
                    # Copy additional constraints from the original tech
                    for constraint_key in ['resource', 'resource_unit']:
                        if constraint_key in tech_data['constraints']:
                            new_tech_constraints[constraint_key] = tech_data['constraints'][constraint_key]
                    
                    # Add the new tech
                    loc_data['techs'][new_tech_name] = {
                        'constraints': new_tech_constraints
                    }

    # Save the updated YAML file
    output_yaml_path = f'Updated_Location_Constraints_WAPP_{scenario_name}.yaml'
    with open(output_yaml_path, 'w') as file:
        yaml.dump(yaml_data, file)  # Use ruamel.yaml's dump method

    print(f"Updated YAML file saved for scenario '{scenario_name}' at {output_yaml_path}")

print("Processing completed for all scenarios.")
