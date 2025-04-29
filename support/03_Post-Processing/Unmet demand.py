import pandas as pd

# Step 1: Load the CSV file with MSR data
folder_path = 'C:/Users/user/OneDrive - Politecnico di Milano/DallaRiva - CalliopePowerPools/06-Results/Results_'

# List of scenario names
scenario_names = [
    # '_onlyRES_autarky_PHES',
    # '_onlyRES_autarky_NoStorage',    
    '_onlyRES_transmission_NoStorage',
]

years = ['2030','2035','2040']

# Process each scenario
for scenario_name in scenario_names:

    unmet_demand_df= pd.DataFrame(columns=['locs','2030','2035','2040'])

    for year in years:
        file_path= folder_path + year + '/ResultsWAPP_'+ year + scenario_name + '/results_unmet_demand.csv'

        data = pd.read_csv(file_path)

        unmet_demand_summary = data[data['unmet_demand'] >= 0].groupby('locs')['unmet_demand'].sum().reset_index()
        unmet_demand_summary['unmet_demand'] = unmet_demand_summary['unmet_demand'] / 1000000

        unmet_demand_summary.columns = ['locs', year]

        # Merge the current year's data into the unmet_demand_df
        if unmet_demand_df.empty:
            unmet_demand_df = unmet_demand_summary
        else:
            unmet_demand_df = pd.merge(unmet_demand_df, unmet_demand_summary, on='locs', how='outer')

        # Step 3: Write the consolidated data to a new CSV file
        output_csv_path = f'Unmet_demand_{scenario_name.strip("_")}.csv'
        unmet_demand_df.to_csv(output_csv_path, index=False)

    print(f"Consolidated CSV file saved for scenario '{scenario_name.strip('_')}' at {output_csv_path}")

print("Processing completed for all scenarios.")