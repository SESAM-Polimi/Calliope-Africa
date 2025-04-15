import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from itertools import cycle

def plot_Costs_combined(data_path, output_folder, scenario_transmission):
    years = ["2030", "2035", "2040"]
    input_files = {year: pd.read_csv(f"{data_path}{year}/Results_to_plot_{year}.csv") for year in years}

    scenario = ['onlyRES', 'RES+GT']
    group_data = {}

    for year, df in input_files.items():
        df = df[df['Scenario transmission'] == scenario_transmission]

        data_NoStorage, data_BESS, data_PHES = [], [], []

        for val in scenario:
            for storage_type, storage_list in zip(["NoStorage", "BESS", "PHES"],
                                                  [data_NoStorage, data_BESS, data_PHES]):
                sub_df = df[(df['Technology'] == val) & (df['Storage'] == storage_type)]
                row = [
                    sub_df['OCGT Investment [M$]'].sum() * 1e-3,
                    sub_df['Wind Investment [M$]'].sum() * 1e-3,
                    sub_df['PV Investment [M$]'].sum() * 1e-3,
                    sub_df['Storage Investment [M$]'].sum() * 1e-3,
                    sub_df['LCOE [$/MWh]'].sum()
                ]
                storage_list.append(row)

        def format_data(raw):
            return {
                "OCGT": [x[0] for x in raw],
                "Wind": [x[1] for x in raw],
                "PV": [x[2] for x in raw],
                "Storage": [x[3] for x in raw],
                "LCOE": [x[4] for x in raw],
            }

        group_data[year] = {
            "NoStorage": format_data(data_NoStorage),
            "BESS": format_data(data_BESS),
            "PHES": format_data(data_PHES),
        }

    # Plot setup
    storage_types = ['NoStorage', 'BESS', 'PHES']
    categories = ['Only-VRES', 'VRES+OCGT']
    bar_width = 0.2
    spacing = 1.0
    num_groups = len(categories) * len(storage_types)
    x_positions = np.arange(num_groups) * (bar_width * len(years) + spacing)

    if scenario_transmission == "autarky":
        title_prefix = "Autarky:"
        max_value = 30
        max_LCOE = 100
    elif scenario_transmission == "transmission":
        title_prefix = "Existing Transmission:"
        max_value = 10
        max_LCOE = 100
    else:
        title_prefix = "Expansion:"
        max_value = 30
        max_LCOE = 100

    colors = ['#dc908c', '#AEC6CF', '#FFD966', '#95c443']  # OCGT, Wind, PV, Storage
    fig, ax1 = plt.subplots(figsize=(25, 6))
    ax2 = ax1.twinx()
    ax1.set_ylim(0, max_value)
    ax2.set_ylim(0, max_LCOE)

    year_positions = np.array([])

    for year_idx, year in enumerate(years):
        year_offset = (year_idx - 1) * (bar_width + 0.15)

        for storage_idx, storage in enumerate(storage_types):
            bottoms = np.zeros(len(categories))

            for idx, tech in enumerate(["OCGT", "Wind", "PV", "Storage"]):
                values = [group_data[year][storage][tech][i] for i in range(len(categories))]
                ax1.bar(x_positions[storage_idx::3] + year_offset, values, width=bar_width,
                        color=colors[idx], bottom=bottoms, edgecolor='black',
                        label=tech if year_idx == 0 else "")
                bottoms += np.array(values)

            # Add LCOE markers
            lcoe_values = [group_data[year][storage]["LCOE"][i] for i in range(len(categories))]
            ax2.scatter(x_positions[storage_idx::3] + year_offset, lcoe_values, color='red', s=80, marker='o', zorder=5)

            year_positions = np.concatenate((year_positions, x_positions[storage_idx::3] + year_offset))

    # X-axis formatting
    ax1.set_xticks(year_positions)
    ax1.set_xticklabels(["2030"]*6 + ["2035"]*6 + ["2040"]*6, fontsize=12, fontweight='bold')
    ax1.set_ylabel("Investment [B$]", fontsize=16, fontweight='bold')
    ax2.set_ylabel("LCOE [$/MWh]", fontsize=16, fontweight='bold')
    ax1.set_title(f"{title_prefix} Investment and LCOE", fontsize=20, fontweight='bold')

    # Sub-labels (NoStorage, BESS, etc.)
    labels = ["NoStorage", "BESS", "PHES"] * 2
    for idx, pos in enumerate(x_positions):
        ax1.text(pos, -max_value*0.12, labels[idx], ha='center', fontsize=16, fontweight='bold')

    # # Category labels
    # category_positions = [np.mean(x_positions[i * 3:(i + 1) * 3]) for i in range(len(categories))]
    # for pos, label in zip(category_positions, categories):
    #     ax1.text(pos, -max_value*0.15, label, ha='center', fontsize=14, fontweight='bold', color='#213652')

    # Legends
    investment_legend = [
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=c, markersize=15, label=l)
        for c, l in zip(colors, ["OCGT", "Wind", "PV", "Storage"])
    ]
    lcoe_marker = plt.Line2D([0], [0], linestyle='None', marker='o', color='red', markersize=10, label='LCOE')

    ax1.legend(handles=investment_legend + [lcoe_marker], loc='upper left', prop={'size': 13})

    plt.grid(axis='y', linestyle='--', alpha=0.7)

    os.makedirs(output_folder, exist_ok=True)
    plt.savefig(os.path.join(output_folder, f"{scenario_transmission}_Investment_LCOE_combined_plot.png"), dpi=300, bbox_inches='tight')
    plt.show()