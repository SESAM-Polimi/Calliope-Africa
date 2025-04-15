import pandas as pd
import copy

# Step 1: Load the CSV file with MSR data
folder_path = 'C:/Users/user/OneDrive - Politecnico di Milano/DallaRiva - CalliopePowerPools/06-Results/Results_'

# List of scenario names
scenario_names = [
    # '_onlyRES_autarky_BESS',
     '_onlyRES_transmission_BESS',
    #  '_onlyRES_transmission_exp_BESS',
    # '_RES+GT_autarky_BESS',
     '_RES+GT_transmission_BESS',
    #  '_RES+GT_transmission_exp_BESS'
]

years = ['2030','2035','2040']

# Process each scenario
for scenario_name in scenario_names:

    storage_df= pd.DataFrame(columns=['locs','2030','2035','2040'])

    for year in years:
        # Step 1: Load the CSV file for the current scenario
        csv_path = folder_path + year + '/ResultsWAPP_'+ year + scenario_name + "/results_storage_cap.csv"
        storage_data = pd.read_csv(csv_path)

        # Drop the 'techs' column and keep 'locs' and 'storage_cap'
        storage_data = storage_data[['locs', 'storage_cap']]
        # Divide the storage_cap values by 1000
        storage_data['storage_cap'] = storage_data['storage_cap'] / 1000
        storage_data = storage_data.groupby(['locs'])['storage_cap'].sum().reset_index()


        # Identify NGA-related rows
        nga_mask = storage_data['locs'].str.startswith("NGA_")

        # Sum the NGA regions and create a new row
        nga_sum = storage_data.loc[nga_mask, 'storage_cap'].sum()

        # Remove individual NGA rows
        storage_data = storage_data[~nga_mask]

        # Append the new summed NGA row
        storage_data = pd.concat([storage_data, pd.DataFrame({'locs': ['NGA'], 'storage_cap': [nga_sum]})], ignore_index=True)

        # Rename the 'storage_cap' column to the current year
        storage_data.rename(columns={'storage_cap': year + '[MWh]'}, inplace=True)

        # Merge the current year's data into the storage_df
        if storage_df.empty:
            storage_df = storage_data
        else:
            storage_df = pd.merge(storage_df, storage_data, on='locs', how='outer')

        # Step 3: Write the consolidated data to a new CSV file
        output_csv_path = f'Storage_{scenario_name.strip("_")}.csv'
        storage_df.to_csv(output_csv_path, index=False)

    print(f"Consolidated CSV file saved for scenario '{scenario_name.strip('_')}' at {output_csv_path}")

print("Processing completed for all scenarios.")