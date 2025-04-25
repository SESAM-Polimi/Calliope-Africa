import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from itertools import cycle

def plot_Capacity_transmission_combined(data_path, output_folder, scenario_transmission):
    years = ["2030", "2035", "2040"]
    input_files = {year: pd.read_csv(f"{data_path}{year}/Results_to_plot_{year}.csv") for year in years}
    
    scenario = ['onlyRES']  # Only keep Only-VRES
    group_data = {}

    for year, df in input_files.items():
        df = df[df['Scenario transmission'] == scenario_transmission]

        data_NoStorage, data_BESS, data_PHES = [], [], []

        for val in scenario:
            for storage_type, storage_list in zip(["NoStorage", "BESS", "PHES"],
                                                  [data_NoStorage, data_BESS, data_PHES]):
                cap = df[(df['Technology'] == val) & (df['Storage'] == storage_type)]['New Transmission cap [MW]'].sum() * 1e-3
                storage_list.append([cap])

        data_dict = {
            "NoStorage": {"Transmission": [x[0] for x in data_NoStorage]},
            "BESS": {"Transmission": [x[0] for x in data_BESS]},
            "PHES": {"Transmission": [x[0] for x in data_PHES]},
        }

        group_data[year] = data_dict

    colors = ['#D98845']  # Transmission
    storage_types = ['NoStorage', 'BESS', 'PHES']
    bar_width = 0.2
    spacing = 0.6
    num_groups = len(storage_types)
    x_positions = np.arange(num_groups) * (bar_width * len(years) + spacing)

    name = {
        "autarky": "Autarky:",
        "transmission": "Existing Transmission:",
    }.get(scenario_transmission, "Expansion:")

    fig, ax = plt.subplots(figsize=(15, 6))
    ax.set_ylim(0, 80)
    year_positions = np.array([])

    for year_idx, year in enumerate(years):
        year_offset = (year_idx - 1) * (bar_width + 0.1)
        for storage_idx, storage in enumerate(storage_types):
            val = group_data[year][storage]['Transmission'][0]
            ax.bar(x_positions[storage_idx] + year_offset, val, width=bar_width,
                   color=colors[0], edgecolor='black',
                   label='Transmission' if year_idx == 0 else "")
            year_positions = np.append(year_positions, x_positions[storage_idx] + year_offset)

    # X-ticks
    ax.set_xticks(year_positions)
    ax.set_xticklabels(["2030"] * 3 + ["2035"] * 3 + ["2040"] * 3, fontsize=12, fontweight='bold')
    ax.set_ylabel('Capacity [GW]', fontsize=16, fontweight='bold')
    ax.set_title(f"{name} New Transmission Capacity [GW]", fontsize=20, fontweight='bold')

    # Labels below x-axis
    labels = ["NoStorage", "BESS", "PHES"]
    for idx, pos in enumerate(x_positions):
        ax.text(pos, -12, labels[idx], ha='center', fontsize=14, fontweight='bold')

    # Legend
    legend_elements = [
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=colors[0],
                   markersize=15, label='Transmission')
    ]
    ax.legend(handles=legend_elements, loc='upper left', prop={'size': 15})

    plt.grid(axis='y', linestyle='--', alpha=0.7)

    os.makedirs(output_folder, exist_ok=True)
    plt.savefig(os.path.join(output_folder, f"{scenario_transmission}_OnlyVRES_New_Transmission_plot.png"),
                dpi=300, bbox_inches='tight')
    plt.show()
