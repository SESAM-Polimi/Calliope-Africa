import pandas as pd

# Step 1: Load the CSV file with MSR data
folder_path = 'C:/Users/user/OneDrive - Politecnico di Milano/DallaRiva - CalliopePowerPools/06-Results/Results_'

# List of scenario names
scenario_names = [
    # '_onlyRES_autarky_BESS',
    # '_onlyRES_autarky_PHES',
    # '_onlyRES_autarky_NoStorage',    
    # '_RES+GT_autarky_BESS',  
    # '_RES+GT_autarky_NoStorage',
    # '_RES+GT_autarky_PHES',
    # '_onlyRES_transmission_BESS',
    # '_onlyRES_transmission_NoStorage',
    # '_onlyRES_transmission_PHES',
    # '_RES+GT_transmission_BESS',
    # '_RES+GT_transmission_NoStorage',
    # '_RES+GT_transmission_PHES',
    '_onlyRES_transmission_exp_BESS',
    '_onlyRES_transmission_exp_NoStorage',
    '_onlyRES_transmission_exp_PHES',
    '_RES+GT_transmission_exp_BESS',
    '_RES+GT_transmission_exp_NoStorage',
    '_RES+GT_transmission_exp_PHES'
]

years = ['2030', '2035', '2040']

# Process each scenario
for scenario_name in scenario_names:
    investment_data = []  # Store data as list of dictionaries

    for year in years:
        # Load the CSV file for the current scenario
        csv_path = folder_path + year + '/ResultsWAPP_' + year + scenario_name + "/results_cost_investment.csv"
        results_data = pd.read_csv(csv_path)

        monetary_data = results_data[results_data['costs'].str.contains("monetary", na=False)]
        
        # Extract cost data
        ocgt_data = monetary_data[monetary_data['techs'] == "OCGT_pp_New"]
        msr_data = monetary_data[monetary_data['techs'].str.contains("MSR", na=False) & ~monetary_data['techs'].str.contains("installed", na=False)]

        # Filter rows where 'techs' contains "PV" or "Wind"
        PV_data = msr_data[(msr_data['techs'].str.contains("PV", na=False))]
        Wind_data = msr_data[(msr_data['techs'].str.contains("Wind", na=False))]

        PV_data = PV_data.groupby(['locs'])['cost_investment'].sum().reset_index()
        Wind_data = Wind_data.groupby(['locs'])['cost_investment'].sum().reset_index()

        storage_data = monetary_data[monetary_data['techs'].isin(["BESS", "PHES"])]
        
        # Convert to M$
        ocgt_data['cost_investment'] *= 1e-6
        PV_data['cost_investment'] *= 1e-6
        Wind_data['cost_investment'] *= 1e-6
        storage_data['cost_investment'] *= 1e-6
        
        #Group NGA regions
        # Identify NGA-related rows
        nga_mask = ocgt_data['locs'].str.startswith("NGA_")
        # Sum the NGA regions and create a new row
        nga_sum = ocgt_data.loc[nga_mask, 'cost_investment'].sum()
        # Remove individual NGA rows
        ocgt_data = ocgt_data[~nga_mask]
        # Append the new summed NGA row
        ocgt_data = pd.concat([ocgt_data, pd.DataFrame({'locs': ['NGA'], 'cost_investment': [nga_sum]})], ignore_index=True)

        # Identify NGA-related rows
        nga_mask = PV_data['locs'].str.startswith("NGA_")
        nga_sum = PV_data.loc[nga_mask, 'cost_investment'].sum()
        # Remove individual NGA rows
        PV_data = PV_data[~nga_mask]
        # Append the new summed NGA row
        PV_data = pd.concat([PV_data, pd.DataFrame({'locs': ['NGA'], 'cost_investment': [nga_sum]})], ignore_index=True)

        # Identify NGA-related rows
        nga_mask = Wind_data['locs'].str.startswith("NGA_")
        nga_sum = Wind_data.loc[nga_mask, 'cost_investment'].sum()
        # Remove individual NGA rows
        Wind_data = Wind_data[~nga_mask]
        # Append the new summed NGA row
        Wind_data = pd.concat([Wind_data, pd.DataFrame({'locs': ['NGA'], 'cost_investment': [nga_sum]})], ignore_index=True)

        # Identify NGA-related rows
        nga_mask = storage_data['locs'].str.startswith("NGA_")
        nga_sum = storage_data.loc[nga_mask, 'cost_investment'].sum()
        # Remove individual NGA rows
        storage_data = storage_data[~nga_mask]
        # Append the new summed NGA row
        storage_data = pd.concat([storage_data, pd.DataFrame({'locs': ['NGA'], 'cost_investment': [nga_sum]})], ignore_index=True)

        # Store data in structured format
        for df, category in zip([PV_data, Wind_data, ocgt_data, storage_data], ['PV', 'Wind', 'OCGT', 'Storage']):
            for _, row in df.iterrows():
                investment_data.append({
                    'locs': row['locs'],
                    'Category': category,
                    year: row['cost_investment']
                })

    # Convert list to DataFrame
    investment_df = pd.DataFrame(investment_data)
    
    # Pivot the data to match desired output
    investment_df = investment_df.pivot_table(index=['locs', 'Category'], values=years, aggfunc='sum').reset_index()
    
    # Save to CSV
    output_csv_path = f'Cost_{scenario_name.strip("_")}_formatted.csv'
    investment_df.to_csv(output_csv_path, index=False)

    print(f"Formatted CSV file saved for scenario '{scenario_name.strip('_')}' at {output_csv_path}")

print("Processing completed for all scenarios.")
