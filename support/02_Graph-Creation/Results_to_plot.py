 
import matplotlib.pyplot as plt # type: ignore
import os

supply_techs_type = ['supply', 'supply_plus', 'conversion', 'conversion_plus', 'storage']


import pandas as pd # type: ignore

class Results_data:

    def __init__(self, path):
        self.carrier_prod_df = pd.read_csv(path + '/results_carrier_prod.csv')
        self.cap_df = pd.read_csv(path + '/results_energy_cap.csv')
        self.LCOE_df = pd.read_csv(path + '/results_total_levelised_cost.csv')
        self.cost_df = pd.read_csv(path + '/results_cost.csv')
        self.carrier_con_df = pd.read_csv(path + '/results_carrier_con.csv')
        self.inheritance_df = pd.read_csv(path + '/inputs_inheritance.csv')
        self.lookup_remotes_df = pd.read_csv(path + '/inputs_lookup_remotes.csv')
        self.colors_df = pd.read_csv(path + '/inputs_colors.csv')
        self.investment_df=pd.read_csv(path + '/results_cost_investment.csv')
        self.input_capacity_df=pd.read_csv(path + '/inputs_energy_cap_equals.csv')

    def get_PBI_cap(self):
        PBI_cap = self.cap_df.copy()
        return PBI_cap

    def get_generic_data(self):
        supply_techs = self.inheritance_df[self.inheritance_df['inheritance'].isin(supply_techs_type)]['techs'].values
        demand_tech = self.inheritance_df[self.inheritance_df['inheritance']=='demand']['techs'].values
        locs = self.lookup_remotes_df['locs'].unique()

        return supply_techs, demand_tech, locs

    def get_transmission_data(self, carr):

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

        #create transmission dataframe
        transmission = pd.concat([export_from_loc, import_to_loc])
        transmission.drop(columns=['export_to', 'import_from'], inplace=True)
        transmission['Type'] = 'transmission'
        transmission['Source'] = '---'
        transmission['techs'] = 'transmission'

        return transmission

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
        import_to_loc['year'] = pd.to_datetime(import_to_loc['timesteps']).dt.to_period('Y')

        #create transmission dataframe
        transmission = pd.concat([export_from_loc, import_to_loc])
        transmission['Type'] = 'transmission'
        transmission['Source'] = '---'
        transmission['techs'] = 'transmission'

        transmission['year'] = pd.to_datetime(transmission['timesteps']).dt.to_period('Y')
        transmission_monthly = transmission.groupby(['year', 'locs', 'export_to', 'import_from', 'Type', 'Source', 'techs'])['production'].sum().reset_index()

        return export_from_loc
    
    def get_generation_data(self, carr):
        
        supply_techs = self.inheritance_df[self.inheritance_df['inheritance'].isin(supply_techs_type)]['techs'].values

        #production data for supply technologies
        supply_prod_df = self.carrier_prod_df[(self.carrier_prod_df['techs'].isin(supply_techs))  & (self.carrier_prod_df['carriers'] == carr)].copy()
        #consmption data for supply technologies (storage_charge)
        supply_con_df = self.carrier_con_df[(self.carrier_con_df['techs'].isin(supply_techs))  & (self.carrier_con_df['carriers'] == carr)].copy()
        return supply_prod_df, supply_con_df

    def get_demand_data(self, carr):
        #identify demand technology from inheritance file
        demand_tech = self.inheritance_df[self.inheritance_df['inheritance']=='demand']['techs'].values
        #get demand data
        demand_df = self.carrier_con_df[(self.carrier_con_df['techs'].isin(demand_tech)) & (self.carrier_con_df['carriers'] == carr)].copy()
        demand_df['carrier_con'] = demand_df['carrier_con'].abs() #abs value of demand
        return demand_df

    def get_investment_data(self):
        investment_data=self.investment_df[self.investment_df['costs'] == 'monetary']
        investment= investment_data['cost_investment'].sum()*1e-9 #Convert the cost from $ to $B
        return investment

    def get_investment_by_tech(self):
        monetary_data=self.investment_df[self.investment_df['costs'] == 'monetary']
        investment=pd.DataFrame()
        # Extract cost data and sum only the 'cost_investment' column
        ocgt_data = monetary_data[monetary_data['techs'] == "OCGT_pp_New"]['cost_investment'].sum()*1e-6
        wind_data = monetary_data[monetary_data['techs'].str.contains("MSR", na=False) & monetary_data['techs'].str.contains("Wind", na=False) & ~monetary_data['techs'].str.contains("installed", na=False)]['cost_investment'].sum()*1e-6
        pv_data = monetary_data[monetary_data['techs'].str.contains("MSR", na=False) & monetary_data['techs'].str.contains("PV", na=False) & ~monetary_data['techs'].str.contains("installed", na=False)]['cost_investment'].sum()*1e-6
        storage_data = monetary_data[monetary_data['techs'].isin(["BESS", "PHES"])]["cost_investment"].sum()*1e-6
        line_data = monetary_data[monetary_data['techs'].str.contains("kV_new", na=False)]['cost_investment'].sum()*1e-6
        line_data=line_data/2
        
        # Create DataFrame properly
        investment = pd.DataFrame({
        'OCGT Investment [M$]': [ocgt_data],
        'PV Investment [M$]': [pv_data],
        'Wind Investment [M$]': [wind_data],
        'Storage Investment [M$]': [storage_data],
        'Transmission Investment [M$]' : [line_data]
        })
        return investment
    
    def create_supply_aggregation_file(self, agg_excel_path):

        supply_techs = self.inheritance_df[self.inheritance_df['inheritance'].isin(supply_techs_type)]['techs'].values
        tech_by_carriers = self.carrier_prod_df[['techs', 'carriers']].groupby('techs').first().reset_index()
        supply_techs_of_carr = tech_by_carriers[tech_by_carriers['techs'].isin(supply_techs)]
        supply_techs_of_carr['aggregation'] = supply_techs_of_carr['techs'].copy()
        supply_techs_of_carr['Type'] = 'supply or storage'
        supply_techs_of_carr['Source'] = 'fossil o renewable'
        supply_techs_of_carr.to_excel(agg_excel_path, index=False)
    
    def aggregate_supply_data(self, carr, agg_excel_path):
        aggregation_data = pd.read_excel(agg_excel_path)
        unique_aggregations = pd.DataFrame(aggregation_data['aggregation'].unique(), columns=['aggregation'])
        unique_aggregations.to_csv('set_techs_agg')
        supply_prod, supply_con = self.get_generation_data(carr)
        
        aggregation_dict = dict(zip(aggregation_data['techs'], aggregation_data['aggregation']))
        aggregation_dict_source = dict(zip(aggregation_data['techs'], aggregation_data['Source']))
        aggregation_dict_type = dict(zip(aggregation_data['techs'], aggregation_data['Type']))

        supply_prod['agg_tech'] = supply_prod['techs'].map(aggregation_dict)
        supply_prod['Source'] = supply_prod['techs'].map(aggregation_dict_source)
        supply_prod['Type'] = supply_prod['techs'].map(aggregation_dict_type)
        grouped_supply_prod = supply_prod.groupby([ 'timesteps','locs','agg_tech', 'Source', 'Type'])['carrier_prod'].sum().reset_index()
        grouped_supply_prod.rename(columns={'agg_tech': 'techs'}, inplace=True)

        supply_con['agg_tech'] = supply_con['techs'].map(aggregation_dict)
        supply_con['Source'] = supply_con['techs'].map(aggregation_dict_source)
        supply_con['Type'] = supply_con['techs'].map(aggregation_dict_type)
        grouped_supply_con = supply_con.groupby(['timesteps','locs', 'agg_tech', 'Source', 'Type'])['carrier_con'].sum().reset_index()
        grouped_supply_con.rename(columns={'agg_tech': 'techs'}, inplace=True)

        grouped_supply_con.rename(columns={'carrier_con': 'production'}, inplace=True)
        grouped_supply_prod.rename(columns={'carrier_prod': 'production'}, inplace=True)
        production = pd.concat([grouped_supply_con, grouped_supply_prod], ignore_index=False)
        return production
    
    def get_energy_stored(self, path):
        
        if os.path.exists(path + '/results_storage.csv'):
            storage_prod_df=pd.read_csv(path + '/results_storage.csv')
            storage_prod=storage_prod_df['storage'].sum()*1e-6 #convert from kWh to GWh
        else:
            storage_prod = 0

        return storage_prod

    def get_unmet_demand(self, path):
        
        if os.path.exists(path + '/results_unmet_demand.csv'):
            unmet_df=pd.read_csv(path + '/results_unmet_demand.csv')
            unmet_demand=unmet_df['unmet_demand'].sum()*1e-6 #convert from kWh to GWh
        else:
            unmet_demand = 0

        return unmet_demand

    def get_PBI_data_hourly(self, carr, agg_excel_path):
        
        transmission = self.get_transmission_data(carr)
        production = self.aggregate_supply_data(carr, agg_excel_path)
        PBI_data_hourly = pd.concat([transmission, production], ignore_index=False)
        return PBI_data_hourly

    def get_PBI_data_monthly(self, carr, agg_excel_path):
        
        PBI_data = self.get_PBI_data_hourly(carr, agg_excel_path)
        PBI_data['month'] = pd.to_datetime(PBI_data['timesteps']).dt.to_period('M')
        PBI_data_monthly = PBI_data.groupby(['month', 'locs', 'Type', 'Source', 'techs'])['production'].sum().reset_index()
        return PBI_data_monthly

    def aggregate_cap_data(self, agg_excel_path):
        aggregation_data = pd.read_excel(agg_excel_path)
        unique_aggregations = pd.DataFrame(aggregation_data['aggregation'].unique(), columns=['aggregation'])
        unique_aggregations.to_csv('set_techs_agg')
        cap_data = self.cap_df.copy()
        
        aggregation_dict = dict(zip(aggregation_data['techs'], aggregation_data['aggregation']))
        aggregation_dict_source = dict(zip(aggregation_data['techs'], aggregation_data['Source']))
        aggregation_dict_type = dict(zip(aggregation_data['techs'], aggregation_data['Type']))

        cap_data['agg_tech'] = cap_data['techs'].map(aggregation_dict)
        cap_data['Source'] = cap_data['techs'].map(aggregation_dict_source)
        cap_data['Type'] = cap_data['techs'].map(aggregation_dict_type)

        capacity = cap_data.groupby(['locs','agg_tech', 'Source', 'Type'])['energy_cap'].sum().reset_index()
        capacity.rename(columns={'agg_tech': 'techs'}, inplace=True)
        
        return capacity
    
    def get_LCOE(self, year):
        cost = self.cost_df[(self.cost_df['costs'] == 'monetary')]['cost'].sum()

        demand = ['138099172274.85','184807844583.60','247314584562.90'] #Demand in kWh
        if year == '2030':
            LCOE = cost/float(demand[0])
        else:
            if year == '2035':
                LCOE = cost/float(demand[1])
            else: LCOE = cost/float(demand[2])

        return LCOE
    
    def get_CO2(self, carr):
        PBI_CO2 = self.LCOE_df[(self.LCOE_df['carriers'] == carr) & (self.LCOE_df['costs'] == 'co2')].copy()
        return PBI_CO2

    def get_transmission_cap(self):
        #identify transmission technologies from lookup remotes file
        transmission_techs = self.lookup_remotes_df['techs']
        #get capacity data
        line_df = self.cap_df[(self.cap_df['techs'].isin(transmission_techs))].copy()
        line_df['To'] = line_df['techs'].str.split(':').str[-1]
        #Group capacity by connected countries (no distinction between Voltage/line)
        transmission_cap = line_df.groupby(['locs', 'To']).sum(numeric_only = True).reset_index()

        #Get existing capacity
        existing_df=self.input_capacity_df[(self.input_capacity_df['techs'].isin(transmission_techs))].copy()
        existing_df['To'] = existing_df['techs'].str.split(':').str[-1]
        #Group capacity by connected countries (no distinction between Voltage/line)
        existing = existing_df.groupby(['locs', 'To']).sum(numeric_only = True).reset_index()

        # Merge and calculate new columns
        transmission_cap = transmission_cap.merge(
            existing[['locs', 'To', 'energy_cap_equals']], 
            on=['locs', 'To'],
            how='left',
            suffixes=('', '_existing')
        ).fillna({'energy_cap_equals': 0})  # Replace missing values in 'energy_cap_equals' with 0
        
        transmission_cap['Added capacity [kW]'] = (transmission_cap['energy_cap'] - transmission_cap['energy_cap_equals'])
        transmission_cap.rename(columns={'energy_cap_equals': 'Existing [kW]'}, inplace=True)
        return transmission_cap


def get_PBI_data_hourly(path, carr, agg_excel_path, save_data=False, data_path=None):
    Results = Results_data(path)
    PBI_data_hourly = Results.get_PBI_data_hourly(carr, agg_excel_path)
    if save_data:
        PBI_data_hourly.to_csv(data_path + '/PBI_data_hourly.csv', index=False)
    return PBI_data_hourly

def get_PBI_data_monthly(path, carr, agg_excel_path, save_data=False, data_path=None):
    Results = Results_data(path)
    PBI_data_monthly = Results.get_PBI_data_monthly(carr, agg_excel_path)
    if save_data:
        PBI_data_monthly.to_csv(data_path + '/PBI_data_monthly.csv', index=False)
    return PBI_data_monthly


def get_results(folder_path, carr, agg_excel_path, year, data_path=None):

    paths = [os.path.join(folder_path, folder).replace('\\', '/') for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
    results_df = pd.DataFrame()
    agg_excel_path = agg_excel_path + '/aggregation_file.xlsx' 

    for path in paths:
        results = Results_data(path)

        
        #Get LCOE data
        LCOE = results.get_LCOE(year)
        scenario_name = path.split('/')[-1]  # Extract the scenario name from the path
        PBI_LCOE=pd.DataFrame({'LCOE [$/kWh]': [LCOE],'scenario': [scenario_name]})

        #Get CO2 data
        PBI_CO2 = results.get_CO2(carr)
        PBI_CO2.rename(columns={'total_levelised_cost': 'CO2 [kg/kWh]'}, inplace=True)
        # Combine LCOE and CO2 DataFrames row-wise
        combined_df = pd.concat([PBI_LCOE.reset_index(drop=True), PBI_CO2.reset_index(drop=True)], axis=1)

        #Get Total Investment Cost and Energy stored data
        inv_df=pd.DataFrame(columns=['Investment cost [B$]', 'Energy stored [GWh]'])
        investment_sum = results.get_investment_data() #Get data
        storage_sum = results.get_energy_stored(path) #Get data
        
        inv_df = pd.concat([inv_df, pd.DataFrame({'Investment cost [B$]': [investment_sum],'Energy stored [GWh]': [storage_sum]})],ignore_index=True)
        combined_df = pd.concat([combined_df, inv_df], axis=1)

        #Get Investment by tech
        inv_df = results.get_investment_by_tech()
        combined_df = pd.concat([combined_df, inv_df], axis=1)

        #Get Unmet demand
        unmet_df=pd.DataFrame(columns=['Unmet Demand [GWh]'])
        unmet_demand_sum = results.get_unmet_demand(path) #Get data
        unmet_df = pd.concat([unmet_df, pd.DataFrame({'Unmet Demand [GWh]': [unmet_demand_sum]})],ignore_index=True)
        combined_df = pd.concat([combined_df, unmet_df], axis=1)

        #New lines capacity
        line = results.get_transmission_cap()
        line_capacity=line['Added capacity [kW]'].sum()*1e-3
        line_capacity= line_capacity/2
        #Get Capacity Installed
        cap_df=pd.DataFrame(columns=['PV Capacity [MW]', 'Wind Capacity [MW]', 'NG Capacity [MW]', 'Existing Capacity [MW]', 'New Transmission cap [MW]'])
        Capacity = results.aggregate_cap_data(agg_excel_path)
        Solar_cap=(Capacity[Capacity['techs'] == 'PV']['energy_cap'].sum()*1e-3)-769.5 #Substracting already installed Capacity
        Wind_cap=(Capacity[Capacity['techs'] == 'Wind']['energy_cap'].sum()*1e-3)-159.75 #Substracting already installed Capacity
        NG_cap=(Capacity[Capacity['techs'] == 'Natural Gas']['energy_cap'].sum()*1e-3)-15873 #Substracting already installed Capacity
        exist_cap = float(29531.31) #Existing capacity
        
        cap_df = pd.concat([cap_df, pd.DataFrame({'PV Capacity [MW]': [Solar_cap],'Wind Capacity [MW]': [Wind_cap],'NG Capacity [MW]': [NG_cap], 'Existing Capacity [MW]': [exist_cap], 'New Transmission cap [MW]': [line_capacity]})],ignore_index=True)
        combined_df = pd.concat([combined_df, cap_df], axis=1)

        #Get VRES production share
        vres_techs=['PV', 'Wind']
        PBI_data = get_PBI_data_monthly(path, carr, agg_excel_path) #Get monthly data
        supply_prod_df=PBI_data[PBI_data['Type'] == 'supply'] #Filter for supply production
        total_production = supply_prod_df['production'].sum() #Calculate total production
        vres_prod_df = supply_prod_df[supply_prod_df['techs'].isin(vres_techs)] #Filter for VRES production
        
        #Calculate VRES shares
        VRES=vres_prod_df['production'].sum() 
        Solar= supply_prod_df[supply_prod_df['techs']=='PV']['production'].sum()
        Wind= supply_prod_df[supply_prod_df['techs']=='Wind']['production'].sum()
        percentage = VRES/total_production
        Solar_data=Solar/total_production
        Wind_data=Wind/total_production
        
        # Create a DataFrame for VRES shares
        VRES_percentage = pd.DataFrame({
            'VRES [%]': [percentage], 
            'Wind [%]': [Wind_data], 
            'Solar [%]': [Solar_data]})
        
        # Combine the VRES data with the existing combined DataFrame
        combined_df = pd.concat([combined_df.reset_index(drop=True), VRES_percentage.reset_index(drop=True)], axis=1)
        # Append combined data to results DataFrame
        results_df = pd.concat([results_df, combined_df], ignore_index=True)

    results_df.drop(columns=['carriers', 'costs'], inplace=True)
    
    # Move 'scenario' to the first position
    cols = ['scenario'] + [col for col in results_df.columns if col != 'scenario']
    results_df = results_df[cols]

    # Split the 'scenario' column into multiple columns
    scenario_split = results_df['scenario'].str.split('_', expand=True)

    # Rename the new columns based on their meaning
    scenario_split.columns = ['extra', 'Year', 'Technology', 'Scenario transmission', 'Storage' ,'Exception']
    
    # Combine the split columns with the original DataFrame
    results_df = pd.concat([results_df, scenario_split], axis=1)
    # Update the 'Scenario transmission' column based on the condition in the 'Storage' column
    results_df['Scenario transmission'] = results_df.apply(lambda row: 'expansion' if row['Storage'] == 'exp' else row['Scenario transmission'],axis=1)
    results_df['Storage'] = results_df.apply(lambda row: row['Exception'] if row['Storage'] == 'exp' else row['Storage'],axis=1)
    results_df.drop(columns=['Exception','extra'], inplace=True)

    results_df.to_csv(data_path + '/Results_to_plot_' + year + '.csv', index=False)
    return results_df

def get_capacity_lines(folder_path, data_path=None):

    paths = [os.path.join(folder_path, folder).replace('\\', '/') for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
    transmission_df = pd.DataFrame()
    for path in paths:
        results = Results_data(path)
        #Get Line data
        line = results.get_transmission_cap()
        scenario_name = path.split('/')[-1]  # Extract the scenario name from the path
        line['scenario'] = scenario_name
        transmission_df = pd.concat([transmission_df, line], ignore_index=True)

    transmission_df.to_csv(data_path + '/Transmission_capacity.csv', index=False)
    return transmission_df

def calculate_net_export(folder_path, carr, agg_excel_path, data_path=None):

    paths = [os.path.join(folder_path, folder).replace('\\', '/') for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
    transmission_multi_scenario = pd.DataFrame()
    
    for path in paths:

        results = Results_data(path)
        export_df = results.get_export_data(carr)
        scenario_name = path.split('/')[-1]  # Extract the scenario name from the path

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

        # Add scenario column
        net_export_df['scenario']= scenario_name
        net_export_df.rename(columns={'country_1': 'country'}, inplace=True)
        net_export_df.rename(columns={'country_2': 'export to'}, inplace=True)

        transmission_multi_scenario = pd.concat([transmission_multi_scenario, net_export_df], ignore_index=True)

    transmission_multi_scenario.to_csv(data_path + '/net_export.csv', index=False)
    return transmission_multi_scenario