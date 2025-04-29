import pandas as pd
import yaml
import os

# Specify the Excel file path (single file with all countries' data)
input_file = "Solar_clusters.csv"  # Replace with your actual file name

# Read the entire input file
df = pd.read_csv(input_file)

# Create the output folder
output_folder = "YAML output"
os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't exist

# Predefined list of country codes
country_code_mapping = {
    "Benin": "BEN",
    "BurkinaFaso": "BFA",
    "IvoryCoast": "CIV",
    "Gambia": "GMB",
    "Ghana": "GHA",
    "Guinea": "GIN",
    "Guinea-Bissau": "GNB",
    "Liberia": "LBR",
    "Mali": "MLI",
    "Niger": "NER",
    "Nigeria_East": "NGA_E",
    "Nigeria_North": "NGA_CNW",
    "Senegal": "SEN",
    "SierraLeone": "SLE",
    "Togo": "TGO"
    # Add other countries and their codes here
}

# Unified YAML file for all countries
yaml_tech_file = os.path.join(output_folder, "Solar_Tech.yaml")

# Unified timeseries output file
timeseries_name = "Solar_WAPP_MSR.csv"
timeseries_file = os.path.join(output_folder, timeseries_name)

# Function to handle custom YAML formatting (preserves empty lines and right indentation)
class CustomDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(CustomDumper, self).increase_indent(flow, False)

# Function to create a dictionary representing each solar plant in the required format
def create_yaml_tech(row, country_code):
    entry = {
        f"PV_{country_code}_MSR{row['MSR_ID']}": {
            "essentials": {
                "color": "#FFA52B",
                "name": f"PV Power Plant {country_code} {row['MSR_ID']}",
                "parent": "supply_plus",
                "carrier_out": "power"
            },
            "constraints": {
                "resource": "inf",
                "lifetime": 25,
                "force_resource": True
            },
            "costs": {
                "monetary": {
                    "energy_cap": 1070 + row['trCAPEX-kW'],
                    "om_annual": 20,
                    "interest_rate": 0.10
                },
                "co2": {
                    "om_prod": 0
                }
            }
        }
    }
    return entry

# Function to create a dictionary for location data
def create_yaml_location(row, country_code, timeseries_name):
    location = {
        f"PV_{country_code}_MSR{row['MSR_ID']}": {
            "constraints": {
                "energy_cap_min": 0,
                "energy_cap_max": row['CapacityMW'] * 1000,  # Convert MW to kW
                "resource": f"file={timeseries_name}:{country_code}{row['MSR_ID']}",
                "resource_unit": "energy_per_cap"
            }
        }
    }
    return location

# Function to handle the YAML dumping and format the output
def yaml_with_tab_indentation(data):
    yaml_string = yaml.dump(data, Dumper=CustomDumper, default_flow_style=False, sort_keys=False)
    lines = yaml_string.splitlines()
    formatted_lines = []
    for line in lines:
        if not line.startswith(" "):
            formatted_lines.append("")
            formatted_lines.append("    " + line)
        elif line.startswith("  ") and not line.startswith("    "):
            formatted_lines.append("        " + line.strip())
        elif line.startswith("    ") and not line.startswith("        "):
            formatted_lines.append("            " + line.strip())
    return "\n".join(formatted_lines)

def append_yaml_tech_to_file(df, country_code, yaml_file):
    # Open the file in append mode
    with open(yaml_file, 'a') as file:
        for idx, row in df.iterrows():
            # Generate the YAML entry for the power plant
            entry = create_yaml_tech(row, country_code)
            # Convert the entry to YAML format
            yaml_entry = yaml_with_tab_indentation(entry)
            # Write the YAML entry followed by an empty line
            file.write(yaml_entry + "\n")
            
def append_timeseries_to_file(df, country_code, file_path):
    # Identify hourly data columns
    hourly_data_columns = df.columns[-8760:]  # Assuming the last 8760 columns are hourly data
    
    # Prepare a DataFrame to hold new time series data
    time_series_df = pd.DataFrame()

    # Populate time series with headers as `CountryCode_MSRID`
    for idx, row in df.iterrows():
        header = f"{country_code}{row['MSR_ID']}"  # Format: CountryCode_MSRID
        time_series_df[header] = row[hourly_data_columns].values

    # Check if the timeseries file exists
    if os.path.exists(file_path):
        # Load the existing timeseries file
        existing_df = pd.read_csv(file_path)

        # Ensure proper alignment and avoid duplicates
        for column in time_series_df.columns:
            if column in existing_df.columns:
                print(f"Warning: Column '{column}' already exists in {file_path}. Skipping...")
            else:
                existing_df[column] = time_series_df[column]

        # Save the updated DataFrame back to the file
        existing_df.to_csv(file_path, index=False)
    else:
        # Create a new timeseries file with the current data
        time_series_df.to_csv(file_path, index=False)

# Process each country in the dataset
for country_name, country_df in df.groupby("CtryName"):
    # Get the predefined country code from the mapping
    country_code = country_code_mapping.get(country_name, "UNK")  # Default to "UNK" if not found in mapping
    
    if country_code == "UNK":
        print(f"Warning: Country code for {country_name} is not defined.")
        continue

    # Append `yaml_tech` entries to the unified YAML file
    append_yaml_tech_to_file(country_df, country_code, yaml_tech_file)

    # Define YAML location output filename
    yaml_location_file = os.path.join(output_folder, f"Solar_{country_name}_location.yaml")

    # Process location data for the current country
    yaml_location = {}

    for idx, row in country_df.iterrows():
        # Create YAML entries

        location_entry = create_yaml_location(row, country_code, timeseries_name)
        yaml_location.update(location_entry)

    # Save YAML file
    formatted_yaml_location_string = yaml_with_tab_indentation(yaml_location)
    with open(yaml_location_file, 'w') as file:
        file.write(formatted_yaml_location_string)

    # Append timeseries data to the unified file
    append_timeseries_to_file(country_df, country_code, timeseries_file)

    print(f"Processed data for {country_name}: YAML files saved in {output_folder}, timeseries updated in {timeseries_file}.")