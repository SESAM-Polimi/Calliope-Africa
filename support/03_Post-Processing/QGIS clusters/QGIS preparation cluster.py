import pandas as pd
import os
import re

#This script prepares solar and wind cluster data with visual attributes (color, size) to be used in QGIS maps. It use as input csv files specifying 
# - Cluster name
# - Clusters coordinates
# - Cluster Maximum capacity

#This data will then be matched with the installed capacity results to obtain a capacity saturation map of the VRES potential sites.

# Paths and scenario names
folder_path = 'C:/Users/user/OneDrive - Politecnico di Milano/DallaRiva - CalliopePowerPools/06-Results/Results_2040/ResultsWAPP_'
output_folder = 'C:/Users/user/OneDrive - Politecnico di Milano/DallaRiva - CalliopePowerPools/07-PostProcessing/QGIS clusters/2040_Clusters'
PV_input_path = "Solar_clusters_input.csv"
Wind_input_path = "Wind_clusters_input.csv"
scenario_names = [
    # '2040_onlyRES_autarky_NoStorage',
    # '2040_onlyRES_autarky_BESS',
    # '2040_onlyRES_autarky_PHES',
    # '2040_onlyRES_transmission_NoStorage',
    # '2040_onlyRES_transmission_BESS',
    # '2040_onlyRES_transmission_PHES',
    '2040_onlyRES_transmission_exp_NoStorage',
    '2040_onlyRES_transmission_exp_BESS',
    '2040_onlyRES_transmission_exp_PHES',
    # '2040_RES+GT_autarky_NoStorage',
    # '2040_RES+GT_autarky_BESS',
    # '2040_RES+GT_autarky_PHES',
    # '2040_RES+GT_transmission_NoStorage',
    # '2040_RES+GT_transmission_BESS',
    # '2040_RES+GT_transmission_PHES',
    '2040_RES+GT_transmission_exp_NoStorage',
    '2040_RES+GT_transmission_exp_BESS',
    '2040_RES+GT_transmission_exp_PHES'    
]

# Function to extract the base ID of the technology
def extract_base_tech(tech):
    return re.sub(r'_\d{4}_installed$', '', tech)  # Remove "_2040_installed" or "_2040_installed"

def assign_color(saturation):
    if pd.isna(saturation):  # Handle missing values
        return '#B0B0B0'  # Light gray for undefined saturation
    elif saturation <  0.00005:
        return '#808080'  # Gray
    elif saturation < 0.05:
        return '#00FF00'  # Green
    elif saturation < 0.15:
        return '#ADFF2F'  # Light Green
    elif saturation < 0.3:
        return '#FFFF00'  # Yellow
    elif saturation < 0.5:
        return '#FFD700'  # Orange-Yellow
    elif saturation < 0.75:
        return '#FFA500'  # Orange
    elif saturation < 1:
        return '#FF4500'  # Dark Orange
    elif saturation >= 1:
        return '#FF0000'  # Red (Fully saturated or over-utilized)

def assign_bubble_size(capacity):
    if pd.isna(capacity):  # Handle missing values
        return 2  # Default to smallest size for undefined capacity [MW]
    elif capacity <= 1000:
        return 2  # Very small bubble
    elif capacity <= 10000:
        return 4  # Small bubble
    elif capacity <= 30000:
        return 6  # Medium bubble
    elif capacity <= 50000:
        return 8  # Large bubble
    else:  # For capacities up to 72 GW or higher
        return 10  # Very large bubble
        
PV_input_data = pd.read_csv(PV_input_path)
Wind_input_data = pd.read_csv(Wind_input_path)
# Process each scenario
for scenario_name in scenario_names:
    csv_path = folder_path + scenario_name + "/results_resource_cap.csv"
    msr_data = pd.read_csv(csv_path)

    # Filter rows where 'techs' contains "MSR" and 'resource_cap' is not zero
    msr_data = msr_data[(msr_data['techs'].str.contains("MSR", na=False))]

    # Divide the 'resource_cap' column by 1000
    if 'resource_cap' in msr_data.columns:
        msr_data['resource_cap'] = msr_data['resource_cap'] / 1000

    # Extract the base tech ID
    msr_data['base_tech'] = msr_data['techs'].apply(extract_base_tech)

    # Group by the base_tech and sum resource_cap
    grouped_data = msr_data.groupby('base_tech', as_index=False)['resource_cap'].sum()
    # Separate PV and Wind data
    pv_data = grouped_data[grouped_data['base_tech'].str.contains("PV", na=False)]
    wind_data = grouped_data[grouped_data['base_tech'].str.contains("Wind", na=False)]

    # Merge the data 
    merged_PV = pd.merge(PV_input_data, pv_data, left_on="techs", right_on="base_tech", how="left")
    merged_Wind = pd.merge(Wind_input_data, wind_data, left_on="techs", right_on="base_tech", how="left")

    # Add the new column "Saturation" and apply color and dimensions
    merged_PV["Saturation"] = (merged_PV["resource_cap"] / merged_PV["Capacity [MW]"])
    merged_PV["Color"] = merged_PV["Saturation"].apply(assign_color)
    merged_PV["Bubble_Size"] = merged_PV["Capacity [MW]"].apply(assign_bubble_size)
    merged_Wind["Saturation"] = (merged_Wind["resource_cap"] / merged_Wind["Capacity [MW]"])
    merged_Wind["Color"] = merged_Wind["Saturation"].apply(assign_color)
    merged_Wind["Bubble_Size"] = merged_Wind["Capacity [MW]"].apply(assign_bubble_size)

    # Drop specified columns
    columns_to_drop = ["locs", "resource_cap", "cluster_color", "Capacity [MW]"]
    merged_PV = merged_PV.drop(columns=columns_to_drop, errors='ignore')
    merged_Wind = merged_Wind.drop(columns=columns_to_drop, errors='ignore')

    # Save the filtered MSR data to a new Excel file
    PV_output_file = os.path.join(output_folder, f"{scenario_name}_Solar_MSR.csv")
    merged_PV.to_csv(PV_output_file, index=False)

    Wind_output_file = os.path.join(output_folder, f"{scenario_name}_Wind_MSR.csv")
    merged_Wind.to_csv(Wind_output_file, index=False)

    # merged_PV.to_csv("PV for Maps.csv", index=False)
    # merged_Wind.to_csv("Wind for Maps.csv", index=False)

print("Done")
