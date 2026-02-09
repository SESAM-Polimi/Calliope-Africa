import pandas as pd
import os
import geopandas as gpd

class Results_data:
    def __init__(self, path):
        self.carrier_prod_df   = pd.read_csv(os.path.join(path, 'results_carrier_prod.csv'))
        self.cap_df            = pd.read_csv(os.path.join(path, 'results_energy_cap.csv'))
        self.LCOE_df           = pd.read_csv(os.path.join(path, 'results_total_levelised_cost.csv'))
        self.carrier_con_df    = pd.read_csv(os.path.join(path, 'results_carrier_con.csv'))
        self.inheritance_df    = pd.read_csv(os.path.join(path, 'inputs_inheritance.csv'))
        self.lookup_remotes_df = pd.read_csv(os.path.join(path, 'inputs_lookup_remotes.csv'))
        self.colors_df         = pd.read_csv(os.path.join(path, 'inputs_colors.csv'))

    def get_export_data(self, carr):
        #identify transmission technologies from lookup remotes file
        transmission_techs = self.lookup_remotes_df['techs']
        #get import data
        import_df = self.carrier_prod_df[(self.carrier_prod_df['techs'].isin(transmission_techs)) & (self.carrier_prod_df['carriers'] == carr)].copy()
        import_df['import_from'] = import_df['techs'].apply(lambda x: x.split(':')[-1]) 
        import_to_loc = import_df.groupby(['timesteps', 'locs', 'import_from']).sum(numeric_only = True).reset_index()       
        import_to_loc.rename(columns={'carrier_prod': 'production'}, inplace=True)
        # Locs colum contains name of location where carrier is imported to 
        # get export data
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

def _assert_results_folder(folder):
    must = [
        'results_carrier_prod.csv',
        'results_energy_cap.csv',
        'results_total_levelised_cost.csv',
        'results_carrier_con.csv',
        'inputs_inheritance.csv',
        'inputs_lookup_remotes.csv',
        'inputs_colors.csv'
    ]
    missing = [f for f in must if not os.path.isfile(os.path.join(folder, f))]
    if missing:
        raise FileNotFoundError(
            "Missing these files in the folder:\n  - " + "\n  - ".join(missing) +
            f"\nChecked Folder: {folder}"
        )

def calculate_net_export(folder_path, carr, data_path=None):
    
    _assert_results_folder(folder_path)
    results = Results_data(folder_path)
    export_df = results.get_export_data(carr)
    print("Dentro export")

    for col in ['locs', 'export_to']:
        export_df[col] = (export_df[col].astype(str)
                          .str.strip()
                          .str.upper()
                          .str.replace('-', '_', regex=False))
    # Normalize the country pairs to calculate net export
    export_df['pair'] = export_df.apply(
        lambda row: tuple(sorted([row['locs'], row['export_to']])), axis=1
    )

    # Calculate net export as the difference for each pair
    net_export_pairs = []
    pair_trades_rows = []  # nuovo: per elenco “chi scambia con chi”
    # Somma per pair
    for pair, group in export_df.groupby('pair'):
        a, b = sorted(list(pair))
        by_locs = group.groupby('locs', as_index=True)['production'].sum()

        # export A->B = produzione registrata sul nodo A per il link verso B (carrier_con)
        e_ab = float(by_locs.get(a, 0.0))
        e_ba = float(by_locs.get(b, 0.0))
        diff = e_ab - e_ba  # >0 => A esportatore netto; <0 => B esportatore netto

        if diff < 0:
            # B è esportatore netto verso A
            net_export_pairs.append({'country_1': a, 'country_2': b, 'net_export': diff})      # compatibilità
            pair_trades_rows.append({'exporter': b, 'importer': a, 'net_flow_GWh': (-diff) / 1000000})
        elif diff > 0:
            # A è esportatore netto verso B
            net_export_pairs.append({'country_1': b, 'country_2': a, 'net_export': -diff})     # compatibilità (negativo)
            pair_trades_rows.append({'exporter': a, 'importer': b, 'net_flow_GWh': (diff) / 1000000})
        # diff == 0 -> nessuno scambio netto → niente riga

    # DF compatibile con il tuo flusso
    net_export_df = pd.DataFrame(net_export_pairs).rename(
        columns={'country_1': 'country', 'country_2': 'export to'}
    )

    # DF nuovo con “tra chi si scambiano” (GWh positivi)
    pair_trades_df = pd.DataFrame(pair_trades_rows)

    return net_export_df, pair_trades_df

def build_annual_demand_df(demand_csv_path):

    df = pd.read_csv(demand_csv_path)
    df = df.drop(columns=[df.columns[0]])
    df = df.apply(pd.to_numeric, errors='coerce')
    annual_kwh = (-df).sum(axis=0)
    annual_gwh = annual_kwh / 1000000

    demand_df = annual_gwh.reset_index()
    demand_df.columns = ['Country', 'Demand']
    demand_df['Country'] = demand_df['Country'].astype(str).str.strip()
    return demand_df

def normalize_country_code(s: pd.Series) -> pd.Series: # merge multinode countries
    return (
        s.astype(str)
         .str.strip()
         .str.upper()
         .str.replace(r'[^A-Z0-9_]', '_', regex=True)
    )

###########################################################################################################

group_name = 'Transmission_Expansion'

year = '2040'

scenarios = [
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

demand_csv = os.path.join(r'C:\Users\giorg\Desktop\PoliMi\Tesi\15_Input_Model_Config_&_Timeseries\Timeseries', year, 'Demand.csv')
demand_df = build_annual_demand_df(demand_csv)
demand_df['Country'] = normalize_country_code(demand_df['Country'])
demand_df['Country'] = demand_df['Country'].str.replace(r'^MOZ_.*$', 'MOZ', regex=True)  # 👈 aggiungi questa
demand_df = demand_df.groupby('Country', as_index=False).agg({'Demand': 'sum'})

base_results = r'C:\Users\giorg\Desktop\PoliMi\Tesi\20_RESULTS_Calliope'
output_folder = r'C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\Exports\Results'
os.makedirs(output_folder, exist_ok=True)

for scenario in scenarios:
    folder = os.path.join(base_results, group_name, year, f'Results_{group_name}{scenario}')
    # Obtain net export dataframe
    df, pair_trades = calculate_net_export(folder, 'electricity')
    print("Calculated net export")
    
    pair_trades['exporter'] = normalize_country_code(pair_trades['exporter']).str.replace(r'^MOZ_.*$', 'MOZ', regex=True)
    pair_trades['importer'] = normalize_country_code(pair_trades['importer']).str.replace(r'^MOZ_.*$', 'MOZ', regex=True)

    # saldo per Paese
    # saldo per Paese
    net_trade_balance = {}
    for _, row in df.iterrows():
        country = row['country']
        export_to = row['export to']
        net_exp = row['net_export']

        # FIX segno (vedi spiegazione)
        net_trade_balance[country]   = net_trade_balance.get(country, 0)   - net_exp
        net_trade_balance[export_to] = net_trade_balance.get(export_to, 0) + net_exp

    result_df = pd.DataFrame(list(net_trade_balance.items()), columns=['Country', 'Net Trade Balance'])

    result_df['Country'] = normalize_country_code(result_df['Country'])
    result_df['Country'] = result_df['Country'].str.replace(r'^MOZ_.*$', 'MOZ', regex=True)
    result_df = result_df.groupby('Country', as_index=False).agg({'Net Trade Balance':'sum'})

# (opzionale) sanity check prima di convertire in GWh
    print(f"Somma saldo mondiale (kWh): {result_df['Net Trade Balance'].sum():,.0f}")

# kWh → GWh (se serve)
    result_df['Net Trade Balance'] = (result_df['Net Trade Balance']/1_000_000).round(0).astype(int)
    result_df['Status'] = result_df['Net Trade Balance'].apply(lambda x: 'Net Exporter' if x < 0 else 'Net Importer')

    result_df = result_df.merge(demand_df, on='Country', how='outer')

# robustezza su NaN/zero
    result_df['Net Trade Balance'] = result_df['Net Trade Balance'].fillna(0)
    result_df['Percentage'] = result_df['Net Trade Balance'] / result_df['Demand'].replace({0: pd.NA})

    result_df['color'] = result_df['Percentage'].apply(assign_color)


    out_csv = os.path.join(output_folder, f'{group_name}_{year}{scenario}_ExportFiles.csv')
    result_df.to_csv(out_csv, index=False)
    pair_out = os.path.join(output_folder, f'{group_name}_{year}{scenario}_PairTrades.csv')
    pair_trades.to_csv(pair_out, index=False)
    print(f'Salvato: {out_csv}')
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
