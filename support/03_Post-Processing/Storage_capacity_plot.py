import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_ng_capacity(csv_file, output_image, scenario_name):
    # Load the dataset
    df = pd.read_csv(csv_file)
    
    # Extracting data
    locations = df['locs']
    years = ['2030', '2035', '2040']
    values = [df[f"{year}[MWh]"] for year in years]

    # Set bar width and positions
    x = np.arange(len(locations))
    width = 0.2  # Reduced width for more spacing
    spacing = 0.05  # Additional spacing between bars
    # Define pastel colors
    colors = ['#6B91C9', '#E07B6C', '#73A88A']

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - (width + spacing), values[0], width, label='2030', color=colors[0])
    ax.bar(x, values[1], width, label='2035', color=colors[1])
    ax.bar(x + (width + spacing), values[2], width, label='2040', color=colors[2])

    # Formatting the chart to resemble thesis style
    ax.set_ylabel("Storage Capacity [MWh]", fontsize=16, fontweight='bold')
    ax.set_title(tech + " Installed Storage Capacity - " + scenario_name + " only-VRES ", fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(locations, rotation=45, fontsize=12)
    ax.tick_params(axis='x', length=0)
    ax.legend(fontsize=12, loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Set a uniform Y-axis limit
    y_max= 15000
    ax.set_ylim(0, y_max)  # <-- Set max value for consistency

    # Apply tighter layout for aesthetics
    plt.tight_layout()
    plt.savefig(output_image, dpi=300)
    plt.close()

# Step 1: Load the CSV file with MSR data
folder_path = 'C:/Users/user/OneDrive - Politecnico di Milano/DallaRiva - CalliopePowerPools/06-Results/Results_'
tech = "BESS"

# List of scenario names
# List of scenario names
scenario_names = [
    # '_onlyRES_autarky_',
    '_onlyRES_transmission_',   
    #    '_onlyRES_transmission_exp_',

]

years = ['2030','2035','2040']

# Process each scenario
for scenario_name in scenario_names:

    storage_df= pd.DataFrame(columns=['locs','2030','2035','2040'])

    for year in years:
        # Step 1: Load the CSV file for the current scenario
        csv_path = folder_path + year + '/ResultsWAPP_'+ year + scenario_name + tech + "/results_storage_cap.csv"
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
        storage_data = storage_data.sort_values(by='locs').reset_index(drop=True)
        # Merge the current year's data into the storage_df
        if storage_df.empty:
            storage_df = storage_data
        else:
            storage_df = pd.merge(storage_df, storage_data, on='locs', how='outer')

        parts = scenario_name.strip('_').split('_')
        # if parts[2] == "exp":
        #     graph_title= "Transmission Expansion"

        if parts[1] == "autarky":
            graph_title= "Autarky"
        else:
            graph_title = "Existing Transmission"

        # Step 3: Write the consolidated data to a new CSV file
        output_csv_path = f'Storage_{scenario_name.strip("_")}.csv'
        storage_df.to_csv(output_csv_path, index=False)
    print(f"Consolidated CSV file saved for scenario '{scenario_name.strip('_')}' at {output_csv_path}")

    csv_path=output_csv_path
    output_image_path = f'Storage_plot_{graph_title}_{tech}.png'
    plot_ng_capacity(csv_path, output_image_path, graph_title)


print("Processing completed for all scenarios.")