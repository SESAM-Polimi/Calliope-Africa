import pandas as pd
import os
import geopandas as gpd

class Results_data:

    def __init__(self, path):
        self.carrier_prod_df = pd.read_csv(path + '/results_carrier_prod.csv')
        self.cap_df = pd.read_csv(path + '/results_energy_cap.csv')
        self.LCOE_df = pd.read_csv(path + '/results_total_levelised_cost.csv')
        self.carrier_con_df = pd.read_csv(path + '/results_carrier_con.csv')
        self.inheritance_df = pd.read_csv(path + '/inputs_inheritance.csv')
        self.lookup_remotes_df = pd.read_csv(path + '/inputs_lookup_remotes.csv')
        self.colors_df = pd.read_csv(path + '/inputs_colors.csv')

    def get_export_data(self, carr):

        #identify transmission technologies from lookup remotes file
        transmission_techs = self.lookup_remotes_df['techs']
        #get import data
        import_df = self.carrier_prod_df[(self.carrier_prod_df['techs'].isin(transmission_techs)) & (self.carrier_prod_df['carriers'] == carr)].copy()
        import_df['import_from'] = import_df['techs'].apply(lambda x: x.split(':')[-1]) 
        import_to_loc = import_df.groupby(['timesteps', 'locs', 'import_from']).sum(numeric_only = True).reset_index()       
        import_to_loc.rename(columns={'carrier_prod': 'production'}, inplace=True)
        # Locs colum contains name of location where carrier is imported to
        #get export data
        export_df = self.carrier_con_df[(self.carrier_con_df['techs'].isin(transmission_techs)) & (self.carrier_con_df['carriers'] == carr)].copy()
        export_df['export_to'] = export_df['techs'].apply(lambda x: x.split(':')[-1]) 
        export_from_loc = export_df.groupby(['timesteps', 'locs', 'export_to']).sum(numeric_only = True).reset_index()
        export_from_loc.rename(columns={'carrier_con': 'production'}, inplace=True)
        # Locs colum contains name of location where carrier is exported from
        export_from_loc['year'] = pd.to_datetime(export_from_loc['timesteps']).dt.to_period('Y')
        export_from_loc = export_from_loc.groupby(['year', 'locs', 'export_to'])['production'].sum().reset_index()

        return export_from_loc

def assign_color(value):
    if pd.isna(value):  # Handle missing values
        return '#D3D3D3'  # Light grey (placeholder for missing)
    elif value > 0.75:  # More than 75% imported
        return '#D62727'  # Dark red
    elif value > 0.5:  # More than 50% imported
        return '#FF6F61'  # Red
    elif value > 0:  # Net Importer
        return '#F5A3A3'  # light red
    elif value < -1:  # More than 100% exported
        return '#3CB371'  # dark green
    elif value < -0.5:  # More than 50% exported
        return '#66CDAA'  # green
    else:  # Net exporter
        return '#A8E6A3'  # Light green

def calculate_net_export(folder_path, carr, data_path=None):

    results = Results_data(folder_path)
    export_df = results.get_export_data(carr)
    print("Dentro export")
    # Normalize the country pairs to calculate net export
    export_df['pair'] = export_df.apply(
        lambda row: tuple(sorted([row['locs'], row['export_to']])), axis=1)

    # Calculate net export as the difference for each pair
    net_export_pairs = []
    for pair, group in export_df.groupby('pair'):
        # Extract production values
        countries = list(pair)
        productions = group.set_index('locs')['production']

        # Find the difference between exports for the two countries
        if len(productions) == 2:
            diff = productions.iloc[0] - productions.iloc[1]
        else:
            # If only one entry exists, use its value (assume the other is 0)
            diff = productions.iloc[0]

        # Ensure order based on export dominance (always negative)
        if diff > 0:
            diff = -diff
            countries = countries[::-1]  # Reverse order of countries

        # Only append pairs with non-zero net exports
        if diff != 0:
            net_export_pairs.append({'country_1': countries[0], 'country_2': countries[1], 'net_export': diff})

    # Create a DataFrame from the results
    net_export_df = pd.DataFrame(net_export_pairs)

    net_export_df.rename(columns={'country_1': 'country'}, inplace=True)
    net_export_df.rename(columns={'country_2': 'export to'}, inplace=True)

    return net_export_df

year= '2040'

scenarios = {
    # "ResultsWAPP_2040_onlyRES_transmission_exp_BESS",
    # "ResultsWAPP_2040_onlyRES_transmission_exp_PHES",
    # "ResultsWAPP_2040_onlyRES_transmission_exp_NoStorage",
    "ResultsWAPP_2040_RES+GT_transmission_exp_NoStorage",

    # "ResultsWAPP_2040_onlyRES_transmission_BESS",
    # "ResultsWAPP_2040_onlyRES_transmission_PHES",
    #  "ResultsWAPP_2040_onlyRES_transmission_NoStorage",
    # "ResultsWAPP_2040_RES+GT_transmission_BESS",    
}

demand_df= pd.read_excel('Demand_2040.xlsx')

for scenario in scenarios:
    # Initialize a dictionary to store net export/import values
    net_trade_balance = {}

    folder= "C:/Users/user/OneDrive - Politecnico di Milano/DallaRiva - CalliopePowerPools/06-Results/Results_" + year + "/" + scenario
    
    # Obtain net export dataframe
    df= calculate_net_export(folder, 'power', data_path=None)
    print("Calculato net export")
    # Calculate net trade balance for each country
    for _, row in df.iterrows():
        country = row['country']
        export_to = row['export to']
        net_exp = row['net_export']

        # Add net_exp to the "country" value
        net_trade_balance[country] = net_trade_balance.get(country, 0) + net_exp

        # Subtract net_exp from the "export to" value
        net_trade_balance[export_to] = net_trade_balance.get(export_to, 0) - net_exp

    result_df = pd.DataFrame(list(net_trade_balance.items()), columns=['Country', 'Net Trade Balance'])
    result_df['Status'] = result_df['Net Trade Balance'].apply(lambda x: 'Net Exporter' if x < 0 else 'Net Importer')
    result_df['Net Trade Balance']=(result_df['Net Trade Balance']/1000000).round(0).astype(int) #To convert from kWh to GWh and round it

    # Sum up all the countries starting with "NGA" and consolidate them into a single row
    nga_sum = result_df[result_df['Country'].str.startswith("NGA")]['Net Trade Balance'].sum()
    nga_status = "Net Exporter" if nga_sum < 0 else "Net Importer"

    result_df = result_df[~result_df['Country'].str.startswith("NGA")]
    result_df = pd.concat([result_df, pd.DataFrame({"Country": ["NGA"], "Net Trade Balance": [nga_sum], "Status": [nga_status]})], ignore_index=True)
    result_df = pd.merge(result_df, demand_df, on='Country', how='outer')

    result_df['Percentage']=result_df['Net Trade Balance']/result_df['Demand']

    #Apply color coding
    result_df['color'] = result_df['Percentage'].apply(assign_color)
    result_df.to_csv("Export files.csv")
    print(result_df)



# # Define paths
# scenarios_folder = "path/to/scenarios_folder"  # Replace with your scenarios folder path
# shapefile_path = "path/to/shapefile.shp"  # Replace with your shapefile
# output_folder = "path/to/output/folder"  # Folder for saving the updated shapefiles

# # Load the shapefile
# gdf = gpd.read_file(shapefile_path)

# # Loop through all scenarios
# for scenario in os.listdir(scenarios_folder):
#     scenario_path = os.path.join(scenarios_folder, scenario)

#     if not os.path.isdir(scenario_path):
#         continue  # Skip if not a folder
    
#     # Read the exported CSV for the scenario
#     csv_path = os.path.join(scenario_path, "Export files.csv")  # Adjust filename if needed
#     if not os.path.exists(csv_path):
#         print(f"CSV not found for {scenario}. Skipping...")
#         continue

#     scenario_df = pd.read_csv(csv_path)
    
#     # Merge the scenario data with the shapefile
#     gdf_merged = gdf.merge(scenario_df, how="left", left_on="CountryField", right_on="Country")
    
#     # Apply color-coding logic to the GeoDataFrame
#     gdf_merged["color"] = gdf_merged["Net Trade Balance"]
    
#     # Save the merged shapefile
#     output_shapefile = os.path.join(output_folder, f"{scenario}_merged.shp")
#     gdf_merged.to_file(output_shapefile)
#     print(f"Saved merged shapefile for {scenario} at {output_shapefile}")

# print("All scenarios processed.")
