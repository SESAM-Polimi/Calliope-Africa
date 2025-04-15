import pandas as pd
import copy

# Step 1: Load the CSV file with MSR data
folder_path = 'C:/Users/user/OneDrive - Politecnico di Milano/DallaRiva - CalliopePowerPools/06-Results/Results_'

# List of scenario names
scenario_names = [
    # '_RES+GT_autarky_BESS',
    # '_RES+GT_autarky_NoStorage',
    # '_RES+GT_autarky_PHES',
    '_RES+GT_transmission_BESS',
    '_RES+GT_transmission_NoStorage',
    '_RES+GT_transmission_PHES',
    # '_RES+GT_transmission_exp_BESS',
    # '_RES+GT_transmission_exp_NoStorage',
    # '_RES+GT_transmission_exp_PHES'
]

years = ['2030','2035','2040']

# Process each scenario
for scenario_name in scenario_names:

    ocgt_df= pd.DataFrame(columns=['locs','2030','2035','2040'])

    for year in years:
        # Step 1: Load the CSV file for the current scenario
        csv_path = folder_path + year + '/ResultsWAPP_'+ year + scenario_name + "/results_energy_cap.csv"
        ocgt_data = pd.read_csv(csv_path)

        # Filter rows where 'techs' contains "OCGT_pp_new"
        ocgt_data = ocgt_data[(ocgt_data['techs'].str.contains("OCGT_pp_New", na=False))]

        # Drop the 'techs' column and keep 'locs' and 'energy_cap'
        ocgt_data = ocgt_data[['locs', 'energy_cap']]
        # Divide the energy_cap values by 1000
        ocgt_data['energy_cap'] = ocgt_data['energy_cap'] / 1000
        ocgt_data = ocgt_data.groupby(['locs'])['energy_cap'].sum().reset_index()
        # Identify NGA-related rows
        nga_mask = ocgt_data['locs'].str.startswith("NGA_")

        # Sum the NGA regions and create a new row
        nga_sum = ocgt_data.loc[nga_mask, 'energy_cap'].sum()

        # Remove individual NGA rows
        ocgt_data = ocgt_data[~nga_mask]

        # Append the new summed NGA row
        ocgt_data = pd.concat([ocgt_data, pd.DataFrame({'locs': ['NGA'], 'energy_cap': [nga_sum]})], ignore_index=True)

        # Rename the 'energy_cap' column to the current year
        ocgt_data.rename(columns={'energy_cap': year + '[MW]'}, inplace=True)

        # Merge the current year's data into the ocgt_df
        if ocgt_df.empty:
            ocgt_df = ocgt_data
        else:
            ocgt_df = pd.merge(ocgt_df, ocgt_data, on='locs', how='outer')

        # Step 3: Write the consolidated data to a new CSV file
        output_csv_path = f'ocgt_{scenario_name.strip("_")}.csv'
        ocgt_df.to_csv(output_csv_path, index=False)

    print(f"Consolidated CSV file saved for scenario '{scenario_name.strip('_')}' at {output_csv_path}")

print("Processing completed for all scenarios.")