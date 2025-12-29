import pandas as pd

# Step 1: Load the CSV file with MSR data
folder_path = 'C:\\Users\\giorg\\Desktop\\PoliMi\\Tesi\\20_RESULTS_Calliope\\'
# List of scenario names

group_names = [
    # 'Autarky',
    # 'Existing_Transmission',
    'Transmission_Expansion'
]

years = [
    # '2030',
    # '2035',
    '2040'
]

scenario_names = [
    '_VRES_BESS',
    '_VRES_BESS+PHES',
    '_VRES_no_Storage',    
    '_VRES_PHES',  
    '_VRES+Hydro4_BESS',
    '_VRES+Hydro4_BESS+PHES',
    '_VRES+Hydro4_no_Storage',    
    '_VRES+Hydro4_PHES', 
    '_VRES+Hydro4+NG_BESS',
    '_VRES+Hydro4+NG_BESS+PHES',
    '_VRES+Hydro4+NG_no_Storage',    
    '_VRES+Hydro4+NG_PHES' 
]

# Process each scenario
for scenario_name in scenario_names:
    investment_data = []  # Store data as list of dictionaries
    for group in group_names:
        for year in years:
        # Load the CSV file for the current scenario
            csv_path = folder_path + group + '\\' + year + '\\' + 'Results_' + group + scenario_name + "\\results_cost_investment.csv"
            results_data = pd.read_csv(csv_path)

            monetary_data = results_data[results_data['costs'].str.contains("monetary", na=False)]
        
        # Extract cost data
            ocgt_data = monetary_data[monetary_data['techs'] == "OCGT_pp_New"]
            transmission_data = monetary_data[
                monetary_data['techs'].str.startswith("400_kV_New", na=False)
            ][['locs', 'techs', 'cost_investment']].copy()

            msr_data = monetary_data[monetary_data['techs'].str.contains("MSR", na=False) & ~monetary_data['techs'].str.contains("installed", na=False)]

        # Filter rows where 'techs' contains "PV" or "Wind"
            PV_data = msr_data[(msr_data['techs'].str.contains("PV", na=False))]
            Wind_data = msr_data[(msr_data['techs'].str.contains("Wind", na=False))]

            PV_data = PV_data.groupby(['locs'])['cost_investment'].sum().reset_index()
            Wind_data = Wind_data.groupby(['locs'])['cost_investment'].sum().reset_index()

            storage_data = monetary_data[monetary_data['techs'].isin(["BESS_New", "PHES_New"])]
        
            hydro_new_data = monetary_data[monetary_data['techs'].str.startswith("Hydro_Large_New", na=False)][['locs', 'cost_investment']].copy()
            # Aggrego per locs (sommando eventuali Hydro_Large_New_###)
            if not hydro_new_data.empty:
                hydro_new_data = hydro_new_data.groupby(['locs'], as_index=False)['cost_investment'].sum()
        # Convert to M$
            ocgt_data        = ocgt_data.copy()
            transmission_data= transmission_data.copy()
            PV_data          = PV_data.copy()
            Wind_data        = Wind_data.copy()
            storage_data     = storage_data.copy()
            hydro_new_data   = hydro_new_data.copy()
            
            ocgt_data.loc[:, 'cost_investment']         *= 1e-6
            transmission_data.loc[:, 'cost_investment'] *= 1e-6
            PV_data.loc[:, 'cost_investment']           *= 1e-6
            Wind_data.loc[:, 'cost_investment']         *= 1e-6
            storage_data.loc[:, 'cost_investment']      *= 1e-6
            if not hydro_new_data.empty:
                hydro_new_data.loc[:, 'cost_investment'] *= 1e-6
        
        #Group MOZ regions
        # OCGT
            moz_mask = ocgt_data['locs'].str.startswith("MOZ_")
            moz_sum = ocgt_data.loc[moz_mask, 'cost_investment'].sum()
            ocgt_data = ocgt_data[~moz_mask]
            ocgt_data = pd.concat([ocgt_data, pd.DataFrame({'locs': ['MOZ'], 'cost_investment': [moz_sum]})], ignore_index=True)

        # Transmission
            if (transmission_data['locs'].str.startswith("MOZ_")).any():
                 td = transmission_data.copy()
                 td.loc[td['locs'].str.startswith("MOZ_"), 'locs'] = 'MOZ'
                 transmission_data = td.groupby(['locs', 'techs'], as_index=False)['cost_investment'].sum()
        
        # PV
            moz_mask = PV_data['locs'].str.startswith("MOZ_")
            moz_sum = PV_data.loc[moz_mask, 'cost_investment'].sum()
            PV_data = PV_data[~moz_mask]
            PV_data = pd.concat([PV_data, pd.DataFrame({'locs': ['MOZ'], 'cost_investment': [moz_sum]})], ignore_index=True)

        # Wind
            moz_mask = Wind_data['locs'].str.startswith("MOZ_")
            moz_sum = Wind_data.loc[moz_mask, 'cost_investment'].sum()
            Wind_data = Wind_data[~moz_mask]
            Wind_data = pd.concat([Wind_data, pd.DataFrame({'locs': ['MOZ'], 'cost_investment': [moz_sum]})], ignore_index=True)

        # Storage
            moz_mask = storage_data['locs'].str.startswith("MOZ_")
            moz_sum = storage_data.loc[moz_mask, 'cost_investment'].sum()
            storage_data = storage_data[~moz_mask]
            storage_data = pd.concat([storage_data, pd.DataFrame({'locs': ['MOZ'], 'cost_investment': [moz_sum]})], ignore_index=True)
        
        # Hydro
            if not hydro_new_data.empty:
                moz_mask = hydro_new_data['locs'].str.startswith("MOZ_")
                moz_sum = hydro_new_data.loc[moz_mask, 'cost_investment'].sum()
                hydro_new_data = hydro_new_data[~moz_mask]
                hydro_new_data = pd.concat([hydro_new_data, pd.DataFrame({'locs': ['MOZ'], 'cost_investment': [moz_sum]})], ignore_index=True)
       
        # Store data in structured format
            for df, category in [(PV_data, 'PV'),(Wind_data, 'Wind'),(ocgt_data, 'OCGT'),(storage_data, 'Storage')]:
                for _, row in df.iterrows():
                    if row['cost_investment'] > 0:
                        investment_data.append({'locs': row['locs'],'Category': category,year: row['cost_investment']})
            for _, row in transmission_data.iterrows():
                if row['cost_investment'] > 0:
                    investment_data.append({'locs': row['locs'],'Category': row['techs'],year: row['cost_investment']})
        
        # HYDRO
            if not hydro_new_data.empty:
                for _, row in hydro_new_data.iterrows():
                    if row['cost_investment'] > 0:
                        investment_data.append({'locs': row['locs'], 'Category': 'Hydro_New', year: row['cost_investment']})

    # Convert list to DataFrame
        investment_df = pd.DataFrame(investment_data)
    
    # Pivot the data to match desired output
        investment_df = investment_df.pivot_table(index=['locs', 'Category'], values=years, aggfunc='sum').reset_index()
    
    # Save to CSV
        output_csv_path = f'Cost_{scenario_name.strip("_")}_formatted.csv'
        investment_df.to_csv(output_csv_path, index=False)

        print(f"Formatted CSV file saved for scenario '{scenario_name.strip('_')}' at {output_csv_path}")

print("Processing completed for all scenarios.")
