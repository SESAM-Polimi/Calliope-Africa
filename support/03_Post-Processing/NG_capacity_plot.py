import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_ng_capacity(csv_file, output_image, scenario_name):
    # Load the dataset
    df = pd.read_csv(csv_file)
    
    # Extracting data
    locations = df['locs']
    years = ['2030', '2035', '2040']
    values = [df[f"{year}[MW]"] for year in years]

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
    ax.set_ylabel("NG Capacity [MW]", fontsize=16, fontweight='bold')
    ax.set_title("Natural Gas Capacity - " + scenario_name, fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(locations, rotation=45, fontsize=12)
    ax.tick_params(axis='x', length=0)
    ax.legend(fontsize=12, loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Set a uniform Y-axis limit
    y_max= 3500
    ax.set_ylim(0, y_max)  # <-- Set max value for consistency

    # Apply tighter layout for aesthetics
    plt.tight_layout()
    plt.savefig(output_image, dpi=300)
    plt.close()

# Step 1: Load the CSV file with MSR data
folder_path = 'C:/Users/user/OneDrive - Politecnico di Milano/DallaRiva - CalliopePowerPools/06-Results/Results_'

# List of scenario names
scenario_names = [
    # '_RES+GT_autarky_BESS',
    # '_RES+GT_transmission_BESS',
    '_RES+GT_transmission_exp_BESS',
]

years = ['2030','2035','2040']

# Process each scenario
for scenario_name in scenario_names:

    ocgt_df= pd.DataFrame(columns=['locs','2030','2035','2040'])

    for year in years:
        # Step 1: Load the CSV file for the current scenario
        csv_path = folder_path + year + '/ResultsWAPP_'+ year + scenario_name + "/results_energy_cap.csv"
        ocgt_data = pd.read_csv(csv_path)

        # Filter rows where 'techs' contains "OCGT_pp_new"
        ocgt_data = ocgt_data[(ocgt_data['techs'].str.contains("OCGT_pp_New", na=False))]

        # Drop the 'techs' column and keep 'locs' and 'energy_cap'
        ocgt_data = ocgt_data[['locs', 'energy_cap']]
        # Divide the energy_cap values by 1000
        ocgt_data['energy_cap'] = ocgt_data['energy_cap'] / 1000
        ocgt_data = ocgt_data.groupby(['locs'])['energy_cap'].sum().reset_index()
        # Identify NGA-related rows
        nga_mask = ocgt_data['locs'].str.startswith("NGA_")

        # Sum the NGA regions and create a new row
        nga_sum = ocgt_data.loc[nga_mask, 'energy_cap'].sum()

        # Remove individual NGA rows
        ocgt_data = ocgt_data[~nga_mask]

        # Append the new summed NGA row
        ocgt_data = pd.concat([ocgt_data, pd.DataFrame({'locs': ['NGA'], 'energy_cap': [nga_sum]})], ignore_index=True)

        # Sort alphabetically by 'locs'
        ocgt_data = ocgt_data.sort_values(by='locs').reset_index(drop=True)

        # Rename the 'energy_cap' column to the current year
        ocgt_data.rename(columns={'energy_cap': year + '[MW]'}, inplace=True)

        # Merge the current year's data into the ocgt_df
        if ocgt_df.empty:
            ocgt_df = ocgt_data
        else:
            ocgt_df = pd.merge(ocgt_df, ocgt_data, on='locs', how='outer')

        parts = scenario_name.strip('_').split('_')
        if parts[2] == "exp":
            graph_title= "Transmission Expansion"
        else:
            if parts[1] == "autarky":
                graph_title= "Autarky"
            else: graph_title = "Existing Transmission"


        # Step 3: Write the consolidated data to a new CSV file
        output_csv_path = f'ocgt_{scenario_name.strip("_")}.csv'
        ocgt_df.to_csv(output_csv_path, index=False)

    print(f"Consolidated CSV file saved for scenario '{scenario_name.strip('_')}' at {output_csv_path}")

    csv_path=output_csv_path
    output_image_path = f'Ng_plot_{graph_title}.png'
    plot_ng_capacity(csv_path, output_image_path, graph_title)


print("Processing completed for all scenarios.")