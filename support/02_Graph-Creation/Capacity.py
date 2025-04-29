import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from itertools import cycle
from matplotlib.patches import Patch

def plot_Capacity_combined(data_path, output_folder, scenario_transmission):
    years = ["2030", "2035", "2040"]
    input_files = {year: pd.read_csv(f"{data_path}{year}/Results_to_plot_{year}.csv") for year in years}
    
    group_data = {}
    scenario = ['onlyRES', 'RES+GT']
    
    for year, df in input_files.items():
        df = df[df['Scenario transmission'] == scenario_transmission]
        
        data_NoStorage, data_BESS, data_PHES = [], [], []
        
        for val in scenario:
            for storage_type, storage_list in zip(["NoStorage", "BESS", "PHES"],
                                                  [data_NoStorage, data_BESS, data_PHES]):
                storage_list.append([
                    df[(df['Technology'] == val) & (df['Storage'] == storage_type)][col].sum() * 1e-3
                    for col in ['Existing Capacity [MW]', 'NG Capacity [MW]', 'Wind Capacity [MW]', 'PV Capacity [MW]']
                ])
        
        data_dict = {"NoStorage": data_NoStorage, "BESS": data_BESS, "PHES": data_PHES}
        for key in data_dict:
            data_dict[key] = {"Existing": [x[0] for x in data_dict[key]],
                              "OCGT": [x[1] for x in data_dict[key]],
                              "Wind": [x[2] for x in data_dict[key]],
                              "PV": [x[3] for x in data_dict[key]]}
        
        group_data[year] = data_dict
    
    # Define colors (maintaining the same color scheme)
    colors = ['#83629c', '#dc908c', '#AEC6CF', '#FFD966']  # Existing, OCGT, Wind, PV
    #hatch_patterns = ['//', '\\', '']  # Adjusting pattern order
    
    if scenario_transmission == "autarky":
        name = "Autarky:"
    else:
        if scenario_transmission == "transmission":
            name= "Existing Transmission:"
        else: name= "Expansion:"
    
    categories = ['Only-VRES', 'VRES+OCGT']
    storage_types = ['NoStorage', 'BESS', 'PHES']
    bar_width = 0.2  # Narrow bars to fit all years
    spacing = 1.0  # Ensure proper spacing between groups
    num_groups = len(categories) * len(storage_types)
    x_positions = np.arange(num_groups) * (bar_width * len(years) + spacing)
    
    fig, ax = plt.subplots(figsize=(25, 6))
    ax.set_ylim(0, 120)
    year_positions = np.array([])

    for year_idx, year in enumerate(years):
        year_offset = (year_idx - 1) * (bar_width + 0.15)
     
        for storage_idx, storage in enumerate(storage_types):
            bottoms = np.zeros(len(categories))
            for color_idx, (tech, color) in enumerate(zip(['Existing', 'OCGT', 'Wind', 'PV'], colors)):
                values = [group_data[year][storage][tech][i] for i in range(len(categories))]
                ax.bar(x_positions[storage_idx::3] + year_offset, values, width=bar_width, color=color,
                       bottom=bottoms, label=f"{tech}" if year_idx == 0 else "", edgecolor='black',)
                       #hatch=hatch_patterns[year_idx])
                bottoms += np.array(values)
            year_positions = np.concatenate((year_positions, np.array(x_positions[storage_idx::3] + year_offset)))

    # Formatting
    ax.set_xticks(year_positions)
    ax.set_xticklabels(
            ["2030"] * 6 + ["2035"] * 6 + ["2040"] * 6,
            fontsize=12, fontweight='bold'
        )
    ax.set_ylabel('Capacity [GW]', fontsize=16, fontweight='bold')
    ax.set_title(f"{name} Installed Capacity [GW]", fontsize=20, fontweight='bold')
    
    labels=["NoStorage", "BESS", "PHES", "NoStorage", "BESS", "PHES"]
    index=0
    for pos in x_positions:
        ax.text(pos, -12, labels[index], ha='center', fontsize=16, fontweight='bold')
        index=index+1

    # # Add VRES and VRES+GT labels below N, B, P labels
    # category_positions = [np.mean(x_positions[i * 3:(i + 1) * 3]) for i in range(len(categories))]
    # for pos, label in zip(category_positions, categories):
    #     ax.text(pos, -15, label, ha='center', fontsize=14, fontweight='bold', color='#213652')

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))

    legend_elements = [plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=colors[0], markersize=15, label='Existing 2025'),
                    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=colors[1], markersize=15, label='OCGT'),
                    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=colors[2], markersize=15, label='Wind'),
                    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=colors[3], markersize=15, label='PV')]
    
    # pattern_legend_elements = [
    #     Patch(facecolor='white', edgecolor='black', hatch='//', label='2030'),
    #     Patch(facecolor='white', edgecolor='black', hatch='\\', label='2035'),
    #     Patch(facecolor='white', edgecolor='black', hatch= '' , label='2040')
    # ]

    ax.add_artist(ax.legend(handles=legend_elements, loc='upper left', prop={'size': 15}))

    # ax.legend(handles=pattern_legend_elements, loc='upper right', prop={'size': 15})

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Save plot
    os.makedirs(output_folder, exist_ok=True)
    plt.savefig(os.path.join(output_folder, f"{scenario_transmission}_Capacity_combined_plot.png"), dpi=300, bbox_inches='tight')
    plt.show()