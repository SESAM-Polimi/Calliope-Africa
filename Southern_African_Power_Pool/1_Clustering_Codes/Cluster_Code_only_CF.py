# Clustering Code, Giorgio Traverso, POLIMI, July 2025
# %% # IMPORT NECESSARY LIBRARIES
import pandas as pd
import numpy as np
import os

import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

from sklearn.preprocessing import MinMaxScaler
from tslearn.clustering import TimeSeriesKMeans
from tslearn.utils import to_time_series_dataset
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm

import geopandas as gpd
from shapely.geometry import Point

# %% 
# IMPORT DATA FROM EXCEL, change country code based on interested one (done for single country to have faster execution)
# Need 2 files: CtryCode_PV/W_etc... in CSV format

CtryCode = "BWA"
base_dir = "C:/Users/giorg/Desktop/PoliMi/Tesi/9_Python_Mine_Clustering/InputFiles"

filename_PV = f"{CtryCode}_PV_BestMSRsToCover5%CountryArea.csv"
filename_W = f"{CtryCode}_Wind_BestMSRsToCover5%CountryArea.csv"
file_path_PV = os.path.join(base_dir, filename_PV)
file_path_W = os.path.join(base_dir, filename_W)

df_PV = pd.read_csv(file_path_PV, sep=';')
print(f" File Loaded PV: {df_PV.shape[0]} Rows x {df_PV.shape[1]} Columns")
df_W = pd.read_csv(file_path_W, sep=';')
print(f" File Loaded Wind: {df_W.shape[0]} Rows x {df_W.shape[1]} Columns")

def print_column_matrix(df, label):
    print(f"\n {label} Columns (Matrix View):")
    headers = list(df.columns)
    matrix = [list(range(len(headers))), headers]
    for row in matrix:
        print(" | ".join(f"{str(item):<15}" for item in row))

print_column_matrix(df_PV, "PV")
print_column_matrix(df_W, "Wind")

# %% DATA NORMALIZATION

columns_PV = list(range(29, 8789))  # Hourly CF
cf_PV = df_PV.iloc[:, columns_PV].copy()

columns_W = list(range(29, 8789))  # Hourly CF
cf_W = df_W.iloc[:, columns_W].copy()

scaler = MinMaxScaler()
cf_PV_norm = scaler.fit_transform(cf_PV)
cf_PV_norm[np.isnan(cf_PV_norm)] = 0
print(f"Normalized PV Matrix, shape: {cf_PV_norm.shape}")

cf_W_norm = scaler.fit_transform(cf_W)
cf_W_norm[np.isnan(cf_W_norm)] = 0 
print(f"Normalized Wind Matrix, shape:  {cf_W_norm.shape}")

print(" Shape PV:", cf_PV_norm.shape)
print(" Type PV:", type(cf_PV_norm))
print(" NaN present PV:", np.isnan(cf_PV_norm).sum())
print(" Check PV:\n", cf_PV_norm[:5, :5])

print(" Shape Wind:", cf_W_norm.shape)
print(" Type Wind:", type(cf_W_norm))
print(" NaN present Wind:", np.isnan(cf_W_norm).sum())
print(" Check Wind:\n", cf_W_norm[:5, :5])

# %% ELBOW METHOD: determine ideally, optimal number of clusters for TimeSeriesKMeans
#### OPTIONAL NOT NECESSARY ###

# k_max_PV = min(100, df_PV.shape[0])
# k_max_W = min(100, df_W.shape[0])

# ### Elbow Method for PV ###
# n_static_PV = cf_PV_norm.shape[1] - 8760
# static_PV = cf_PV_norm[:, :n_static_PV]
# temporal_PV = cf_PV_norm[:, n_static_PV:]

# var_static_PV = np.var(static_PV)
# var_temporal_PV = np.var(temporal_PV)
# scaling_factor_PV = np.sqrt(var_temporal_PV / var_static_PV)
# print("Scaling factor PV:", scaling_factor_PV)

# static_PV_scaled = static_PV * scaling_factor_PV
# combined_PV = np.hstack([static_PV_scaled, temporal_PV])
# combined_PV_ts = to_time_series_dataset(combined_PV)

# inertias_PV = []
# for k in tqdm(range(1, k_max_PV + 1), desc="Clustering PV"):
#     model = TimeSeriesKMeans(n_clusters=k, metric="euclidean", random_state=42, n_init=10)
#     model.fit(combined_PV_ts)
#     inertias_PV.append(model.inertia_)

# ### Elbow Method for Wind ###
# n_static_W = cf_W_norm.shape[1] - 8760
# static_W = cf_W_norm[:, :n_static_W]
# temporal_W = cf_W_norm[:, n_static_W:]

# var_static_W = np.var(static_W)
# var_temporal_W = np.var(temporal_W)
# scaling_factor_W = np.sqrt(var_temporal_W / var_static_W)
# print("Scaling factor Wind:", scaling_factor_W)

# static_W_scaled = static_W * scaling_factor_W
# combined_W = np.hstack([static_W_scaled, temporal_W])
# combined_W_ts = to_time_series_dataset(combined_W)

# inertias_W = []
# for k in tqdm(range(1, k_max_W + 1), desc="Clustering Wind"):
#     model = TimeSeriesKMeans(n_clusters=k, metric="euclidean", random_state=42, n_init=10)
#     model.fit(combined_W_ts)
#     inertias_W.append(model.inertia_)

# plt.figure(figsize=(8, 5))
# plt.plot(range(1, k_max_PV + 1), inertias_PV, marker='o', color='orange')
# plt.xlabel("Number of clusters (k)")
# plt.ylabel("Inertia")
# plt.title("Elbow Method for Optimal k - PV")
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# plt.figure(figsize=(8, 5))
# plt.plot(range(1, k_max_W + 1), inertias_W, marker='o', color='blue')
# plt.xlabel("Number of clusters (k)")
# plt.ylabel("Inertia")
# plt.title("Elbow Method for Optimal k - Wind")
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# %% Actual Clustering Procedure

k_PV = 3
k_W = 3

# PV Clustering
n_static_PV = cf_PV_norm.shape[1] - 8760
static_PV = cf_PV_norm[:, :n_static_PV]
temporal_PV = cf_PV_norm[:, n_static_PV:]
var_static_PV = np.var(static_PV)
var_temporal_PV = np.var(temporal_PV)
scaling_factor_PV = np.sqrt(var_temporal_PV / var_static_PV)
print(f"Scaling Factor PV: {scaling_factor_PV:.4f}")
static_PV_scaled = static_PV * scaling_factor_PV
combined_PV = np.hstack([static_PV_scaled, temporal_PV])
combined_PV_ts = to_time_series_dataset(combined_PV)

model_PV = TimeSeriesKMeans(n_clusters=k_PV, metric="euclidean", random_state=42, n_init=1, max_iter=1000)
labels_PV = model_PV.fit_predict(combined_PV_ts)
df_PV["Cluster"] = labels_PV + 1
print("[PV] Sites per Cluster:")
print(df_PV["Cluster"].value_counts().sort_index())

# Wind Clustering
n_static_W = cf_W_norm.shape[1] - 8760
static_W = cf_W_norm[:, :n_static_W]
temporal_W = cf_W_norm[:, n_static_W:]
var_static_W = np.var(static_W)
var_temporal_W = np.var(temporal_W)
scaling_factor_W = np.sqrt(var_temporal_W / var_static_W)
print(f"Scaling Factor Wind: {scaling_factor_W:.4f}")
static_W_scaled = static_W * scaling_factor_W
combined_W = np.hstack([static_W_scaled, temporal_W])
combined_W_ts = to_time_series_dataset(combined_W)

model_W = TimeSeriesKMeans(n_clusters=k_W, metric="euclidean", random_state=42, n_init=1, max_iter=1000)
labels_W = model_W.fit_predict(combined_W_ts)
df_W["Cluster"] = labels_W + 1
print("\n[WIND] Sitesb per Cluster:")
print(df_W["Cluster"].value_counts().sort_index())

# Plots
plt.figure(figsize=(8, 6))
coords_PV = df_PV[['Longitude', 'Latitude']].to_numpy()
scatter_PV = plt.scatter(coords_PV[:, 0], coords_PV[:, 1], c=df_PV["Cluster"], cmap='tab10', s=50, alpha=0.7)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('PV Sites Clustered by Location')
legend1 = plt.legend(*scatter_PV.legend_elements(), title="Cluster", loc="best")
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 6))
coords_W = df_W[['Longitude', 'Latitude']].to_numpy()
scatter_W = plt.scatter(coords_W[:, 0], coords_W[:, 1], c=df_W["Cluster"], cmap='tab10', s=50, alpha=0.7)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Wind Sites Clustered by Location')
legend2 = plt.legend(*scatter_W.legend_elements(), title="Cluster", loc="best")
plt.grid(True)
plt.tight_layout()
plt.show()

# Create Summary File in Excel Format
cluster_summary_PV = {}
for cluster_id in range(1, k_PV + 1):
    cluster_sites = df_PV[df_PV["Cluster"] == cluster_id]["MSR_ID"].tolist()
    cluster_summary_PV[cluster_id] = [cluster_id, len(cluster_sites)] + cluster_sites
max_msr_len = max(len(v) for v in cluster_summary_PV.values()) - 2
columns = ["ClusterID", "ZoneCount"] + [f"MSR_{i+1}" for i in range(max_msr_len)]
summary_df = pd.DataFrame(cluster_summary_PV.values(), columns=columns)
summary_df.to_excel("Clustered_PV_Summary.xlsx", index=False)
print(" 'Clustered_PV_Summary.xlsx' File Created Successfully")

cluster_summary_W = {}
for cluster_id in range(1, k_W + 1):
    cluster_sites = df_W[df_W["Cluster"] == cluster_id]["MSR_ID"].tolist()
    cluster_summary_W[cluster_id] = [cluster_id, len(cluster_sites)] + cluster_sites
max_msr_len = max(len(v) for v in cluster_summary_W.values()) - 2
columns = ["ClusterID", "ZoneCount"] + [f"MSR_{i+1}" for i in range(max_msr_len)]
summary_df = pd.DataFrame(cluster_summary_W.values(), columns=columns)
summary_df.to_excel("Clustered_W_Summary.xlsx", index=False)
print(" 'Clustered_W_Summary.xlsx' File Created Successfully")

# %% ############################################################################
# AVERAGE AND WEIGHTED AVERAGE CALCULATION FOR CLUSTERS

nHours = 8760
#### Average PV ###
cluster_stats_PV = []

for cluster_id in range(1, k_PV + 1):
    cluster_df = df_PV[df_PV["Cluster"] == cluster_id]
    if cluster_df.empty:
        continue
    lon = cluster_df["Longitude"].to_numpy()
    lat = cluster_df["Latitude"].to_numpy()
    cap = cluster_df["CapacityMW"].to_numpy()
    lcoe = cluster_df["LCOE-MWh"].to_numpy()
    trcapex = cluster_df["trCAPEX-kW"].to_numpy() + 1070
    hourly_CF = cluster_df.iloc[:, -8760:].to_numpy()
    total_cap = np.sum(cap)
    if total_cap == 0:
        continue
    weighted_lon = np.sum(lon * cap) / total_cap
    weighted_lat = np.sum(lat * cap) / total_cap
    weighted_lcoe = np.sum(lcoe * cap) / total_cap
    weighted_trcapex = np.sum(trcapex * cap) / total_cap
    weighted_hourly_CF = np.sum(hourly_CF * cap[:, np.newaxis], axis=0) / total_cap

    stats = {
        "ClusterID": cluster_id,
        "MeanLon": np.mean(lon),
        "MeanLat": np.mean(lat),
        "WeightedLon": weighted_lon,
        "WeightedLat": weighted_lat,
        "WeightedLCOE": weighted_lcoe,
        "Weighted_CAPEX": weighted_trcapex,
        "TotalCapacityMW": total_cap,
    }

    cluster_stats_PV.append(stats)

df_cluster_stats_PV = pd.DataFrame(cluster_stats_PV)
df_cluster_stats_PV.to_excel(f"{CtryCode}_Cluster_Stats_PV.xlsx", index=False)
print("Cluster Stats PV saved to Excel.")

df_hourly_CF_PV = pd.DataFrame([{
    **{"ClusterID": stats["ClusterID"]},
    **{f"H{h+1}": val for h, val in enumerate(weighted_hourly_CF)}
} for stats, weighted_hourly_CF in zip(cluster_stats_PV, 
    [np.sum(df_PV[df_PV["Cluster"] == s["ClusterID"]].iloc[:, -8761:-1].to_numpy() * 
            df_PV[df_PV["Cluster"] == s["ClusterID"]]["CapacityMW"].to_numpy()[:, np.newaxis], axis=0) / s["TotalCapacityMW"]
     for s in cluster_stats_PV]
)])

df_hourly_CF_PV.to_excel(f"{CtryCode}_Hourly_WeightedLF_PV.xlsx", index=False)
print("Hourly Weighted LF PV saved.")

#### Average Wind ###
class_to_capex = {
    "Class-1": 1338,
    "Class-2": 1552,
    "Class-3": 1819
}

cluster_stats_W = []

for cluster_id in range(1, k_W + 1):
    cluster_df = df_W[df_W["Cluster"] == cluster_id]
    if cluster_df.empty:
        continue
    lon = cluster_df["Longitude"].to_numpy()
    lat = cluster_df["Latitude"].to_numpy()
    cap = cluster_df["CapacityMW"].to_numpy()
    lcoe = cluster_df["LCOE-MWh"].to_numpy()
    
    base_trcapex = cluster_df["trCAPEX-kW"].to_numpy()
    turbine_class = cluster_df["IEC_Class"].astype(str)
    class_capex = turbine_class.map(class_to_capex).fillna(0).to_numpy()
    trcapex = base_trcapex + class_capex

    hourly_CF = cluster_df.iloc[:, -nHours:].to_numpy()
    total_cap = np.sum(cap)
    if total_cap == 0:
        continue

    weighted_lon = np.sum(lon * cap) / total_cap
    weighted_lat = np.sum(lat * cap) / total_cap
    weighted_lcoe = np.sum(lcoe * cap) / total_cap
    weighted_trcapex = np.sum(trcapex * cap) / total_cap
    weighted_hourly_CF = np.sum(hourly_CF * cap[:, np.newaxis], axis=0) / total_cap

    stats = {
        "ClusterID": cluster_id,
        "MeanLon": np.mean(lon),
        "MeanLat": np.mean(lat),
        "WeightedLon": weighted_lon,
        "WeightedLat": weighted_lat,
        "WeightedLCOE": weighted_lcoe,
        "Weighted_CAPEX": weighted_trcapex,
        "TotalCapacityMW": total_cap,
    }

    cluster_stats_W.append(stats)

df_cluster_stats_W = pd.DataFrame(cluster_stats_W)
df_cluster_stats_W.to_excel(f"{CtryCode}_Cluster_Stats_W.xlsx", index=False)
print("Cluster Stats WIND saved to Excel.")

df_hourly_CF_W = pd.DataFrame([{
    **{"ClusterID": stats["ClusterID"]},
    **{f"H{h+1}": val for h, val in enumerate(weighted_hourly_CF)}
} for stats, weighted_hourly_CF in zip(cluster_stats_W, 
    [np.sum(df_W[df_W["Cluster"] == s["ClusterID"]].iloc[:, -8761:-1].to_numpy() * 
            df_W[df_W["Cluster"] == s["ClusterID"]]["CapacityMW"].to_numpy()[:, np.newaxis], axis=0) / s["TotalCapacityMW"]
     for s in cluster_stats_W]
)])

df_hourly_CF_W.to_excel(f"{CtryCode}_Hourly_WeightedLF_W.xlsx", index=False)
print("Hourly Weighted LF WIND saved.")

# %% ############################################################################
### PLOTS ###

def plot_clusters(df, cluster_stats, tech_label):
    plt.figure(figsize=(10, 8))
    palette = sns.color_palette("tab10", len(set(df["Cluster"])))
    cluster_colors = {cluster_id: palette[i % len(palette)] for i, cluster_id in enumerate(sorted(df["Cluster"].unique()))}

    for cluster_id in sorted(df["Cluster"].unique()):
        cluster_df = df[df["Cluster"] == cluster_id]
        plt.scatter(
            cluster_df["Longitude"],
            cluster_df["Latitude"],
            s=40,
            color=cluster_colors[cluster_id],
            label=f"Cluster {cluster_id}",
            alpha=0.6,
            edgecolors='black'
        )
    for stat in cluster_stats:
        cid = stat["ClusterID"]
        color = cluster_colors.get(cid, "black")

        plt.scatter(stat["MeanLon"], stat["MeanLat"],
                    s=160, marker="o", color=color,
                    edgecolors="black", linewidths=1.2)

        plt.scatter(stat["WeightedLon"], stat["WeightedLat"],
                    s=220, marker="*", color=color,
                    edgecolors="black", linewidths=1.2)

    plt.title(f"{tech_label} Clusters with Average and Weighted Centroids")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Clusters")
    plt.tight_layout()
    plt.savefig(f"{CtryCode}_{tech_label}_Clusters.png", dpi=300)
    plt.show()

# Plots
plot_clusters(df_PV, cluster_stats_PV, "PV")
plot_clusters(df_W, cluster_stats_W, "Wind")

### PLOTS 3D ###

fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

colors = sns.color_palette("hsv", k_PV)

for i, row in df_cluster_stats_PV.iterrows():
    cluster_id = row["ClusterID"]
    color = colors[int(cluster_id) - 1]

    # Tutti i punti reali del cluster
    cluster_points = df_PV[df_PV["Cluster"] == cluster_id]
    ax.scatter(cluster_points["Longitude"], cluster_points["Latitude"], cluster_points["LCOE-MWh"],
               c=[color], alpha=0.5, s=15, label=f"Cluster {cluster_id}")

    # Punto medio semplice
    ax.scatter(row["MeanLon"], row["MeanLat"],
               np.mean(cluster_points["LCOE-MWh"]),
               c=[color], marker='o', s=120, edgecolors='black')

    # Punto medio ponderato
    ax.scatter(row["WeightedLon"], row["WeightedLat"],
               np.average(cluster_points["LCOE-MWh"], weights=cluster_points["CapacityMW"]),
               c=[color], marker='*', s=200, edgecolors='black')

ax.set_title("3D PV – LCOE effettivo")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_zlabel("LCOE [€/MWh]")
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.tight_layout()
plt.savefig(f"{CtryCode}_3D_PV_LCOE_Effettivo.png", dpi=300)
plt.show()

fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

colors = sns.color_palette("hsv", k_W)

for i, row in df_cluster_stats_W.iterrows():
    cluster_id = row["ClusterID"]
    color = colors[int(cluster_id) - 1]

    cluster_points = df_W[df_W["Cluster"] == cluster_id]
    ax.scatter(cluster_points["Longitude"], cluster_points["Latitude"], cluster_points["LCOE-MWh"],
               c=[color], alpha=0.5, s=15, label=f"Cluster {cluster_id}")

    ax.scatter(row["MeanLon"], row["MeanLat"],
               np.mean(cluster_points["LCOE-MWh"]),
               c=[color], marker='o', s=120, edgecolors='black')

    ax.scatter(row["WeightedLon"], row["WeightedLat"],
               np.average(cluster_points["LCOE-MWh"], weights=cluster_points["CapacityMW"]),
               c=[color], marker='*', s=200, edgecolors='black')

ax.set_title("3D WIND – LCOE effettivo")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_zlabel("LCOE [€/MWh]")
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.tight_layout()
plt.savefig(f"{CtryCode}_3D_WIND_LCOE_Effettivo.png", dpi=300)
plt.show()

# %% ###################################################################
# Save Output Shapefiles for QGIS

###  PV ###
gdf_means_PV = gpd.GeoDataFrame(df_cluster_stats_PV, geometry=gpd.points_from_xy(df_cluster_stats_PV["MeanLon"], df_cluster_stats_PV["MeanLat"]))
gdf_means_PV.to_file(f"{CtryCode}_PV_Centroids_Mean.shp")

gdf_weighted_PV = gpd.GeoDataFrame(df_cluster_stats_PV, geometry=gpd.points_from_xy(df_cluster_stats_PV["WeightedLon"], df_cluster_stats_PV["WeightedLat"]))
gdf_weighted_PV.to_file(f"{CtryCode}_PV_Centroids_Weighted.shp")

### Wind ###
gdf_means_W = gpd.GeoDataFrame(df_cluster_stats_W, geometry=gpd.points_from_xy(df_cluster_stats_W["MeanLon"], df_cluster_stats_W["MeanLat"]))
gdf_means_W.to_file(f"{CtryCode}_WIND_Centroids_Mean.shp")

gdf_weighted_W = gpd.GeoDataFrame(df_cluster_stats_W, geometry=gpd.points_from_xy(df_cluster_stats_W["WeightedLon"], df_cluster_stats_W["WeightedLat"]))
gdf_weighted_W.to_file(f"{CtryCode}_WIND_Centroids_Weighted.shp")

print("Shapefiles saved.")
# %%
