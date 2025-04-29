import pandas as pd
import copy
import re

# Step 1: Load the CSV file with MSR data
folder_path = 'C:/Users/user/OneDrive - Politecnico di Milano/DallaRiva - CalliopePowerPools/06-Results/Results_'

# Function to extract the base ID of the technology
def extract_base_tech(tech):
    return re.sub(r'_\d{4}_installed$', '', tech)  # Remove "_2030_installed" or "_2035_installed"

# List of scenario names
scenario_names = [
    # '_onlyRES_autarky_BESS',
    # '_onlyRES_autarky_NoStorage',
    # '_onlyRES_autarky_PHES',        
    # '_onlyRES_transmission_BESS',
    # '_onlyRES_transmission_NoStorage',
    # '_onlyRES_transmission_PHES',
    '_onlyRES_transmission_exp_BESS',
    '_onlyRES_transmission_exp_NoStorage',
    '_onlyRES_transmission_exp_PHES'    
    # '_RES+GT_autarky_BESS',
    # '_RES+GT_autarky_NoStorage',
    # '_RES+GT_autarky_PHES',
    # '_RES+GT_transmission_BESS',
    # '_RES+GT_transmission_NoStorage',
    # '_RES+GT_transmission_PHES',
    # '_RES+GT_transmission_exp_BESS',
    # '_RES+GT_transmission_exp_NoStorage',
    # '_RES+GT_transmission_exp_PHES'
]

years = ['2030','2035','2040']

# Process each scenario
for scenario_name in scenario_names:

    PV_df= pd.DataFrame(columns=['locs','2030','2035','2040'])
    Wind_df= pd.DataFrame(columns=['locs','2030','2035','2040'])

    for year in years:
        # Step 1: Load the CSV file for the current scenario
        csv_path = folder_path + year + '/ResultsWAPP_'+ year + scenario_name + "/results_energy_cap.csv"
        tech_data = pd.read_csv(csv_path)
        # Filter rows where 'techs' contains "MSR"
        tech_data = tech_data[(tech_data['techs'].str.contains("MSR", na=False))] #& (~tech_data['techs'].str.contains("installed", na=False)) ]

        # Filter rows where 'techs' contains "PV" or "Wind"
        PV_data = tech_data[(tech_data['techs'].str.contains("PV", na=False))]
        Wind_data = tech_data[(tech_data['techs'].str.contains("Wind", na=False))]

        # Divide the energy_cap values by 1000
        PV_data['energy_cap'] = PV_data['energy_cap'] / 1000 #Convert to MW
        Wind_data['energy_cap'] = Wind_data['energy_cap'] / 1000 #Convert to MW

        # Group by LOCS sum
        PV_data = PV_data.groupby('locs', as_index=False)['energy_cap'].sum()
        Wind_data = Wind_data.groupby('locs', as_index=False)['energy_cap'].sum()

        # Rename the 'energy_cap' column to the current year
        PV_data.rename(columns={'energy_cap': year + '[MW]'}, inplace=True)
        Wind_data.rename(columns={'energy_cap': year + '[MW]'}, inplace=True)

        # Merge the current year's data into the PV_df
        if PV_df.empty:
            PV_df = PV_data
        else:
            PV_df = pd.merge(PV_df, PV_data, on='locs', how='outer')

        # Merge the current year's data into the PV_df
        if Wind_df.empty:
            Wind_df = Wind_data
        else:
            Wind_df = pd.merge(Wind_df, Wind_data, on='locs', how='outer')

        # Step 3: Write the consolidated data to a new CSV file
        output_csv_path = f'PV_{scenario_name.strip("_")}.csv'
        PV_df.to_csv(output_csv_path, index=False)

        output_csv_path = f'Wind_{scenario_name.strip("_")}.csv'
        Wind_df.to_csv(output_csv_path, index=False)

    print(f"Consolidated CSV file saved for scenario '{scenario_name.strip('_')}' at {output_csv_path}")

print("Processing completed for all scenarios.")