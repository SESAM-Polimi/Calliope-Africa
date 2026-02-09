#%%
from pathlib import Path
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from pandas import ExcelWriter

#===================================================================================================================================================
#===================================================================================================================================================
#%%
# Define results/data input folder path and scenarios,groups,years and countries of interest
results_path = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\20_RESULTS_Calliope")
MSR_data_path = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\13_FinalClusteringTotalSAPP\4_FINAL_OUTPUT\4Calliope")
# Check if paths exist
assert results_path.exists(), f"Results Path Not Found: {results_path}"
assert MSR_data_path.exists(), f"MSR Folder Not Found: {MSR_data_path}"

country_code = ['AGO','BWA','DRC','LSO','MOZ_NC','MOZ_S','MWI','NAM','SWZ','TZA','ZAF','ZMB','ZWE']
techs_MSR = ['PV','W']

group_names = [
    'Autarky',
    'Existing_Transmission',
    'Transmission_Expansion'
]
years = [
    '2030',
    '2035',
    '2040'
]
scenario_names = [
    'VRES_BESS',
    'VRES_BESS+PHES',
    'VRES_no_Storage',    
    'VRES_PHES',  
    'VRES+Hydro4_BESS',
    'VRES+Hydro4_BESS+PHES',
    'VRES+Hydro4_no_Storage',    
    'VRES+Hydro4_PHES', 
    'VRES+Hydro4+NG_BESS',
    'VRES+Hydro4+NG_BESS+PHES',
    'VRES+Hydro4+NG_no_Storage',    
    'VRES+Hydro4+NG_PHES' 
]

#===================================================================================================================================================
#===================================================================================================================================================
# %%
# IMPORT MSR & RESULTS DATA
all_found = True

MSR_data = {}
energy_cap_data = {}
var_cost_data = {}

# Import MSR Cluster Data for PV and Wind
for country in country_code:
    for tech in techs_MSR:
        file_name = f"{country}_Cluster_Stats_{tech}.xlsx"
        file_path = MSR_data_path / country / file_name
        if file_path.exists():
            df_msr = pd.read_excel(file_path, engine="openpyxl")
            key_MSR = f"{country}_{tech}"
            MSR_data[key_MSR] = df_msr
            # print(f"\n===== {country} - {tech} =====")
            # print("Columns:", list(df_msr.columns))
            # print("Shape: ", df_msr.shape)
        else:
            print(f"File not found: {file_path}")
            all_found = False
# Import Energy Capacity Results from Calliope Outputs
for group in group_names:
    for year in years:
        for scenario in scenario_names:
            file_name = f"results_energy_cap.csv"  
            file_path = results_path / group / year / f"Results_{group}_{scenario}" / file_name
            if file_path.exists():
                df_energy_cap = pd.read_csv(file_path, low_memory=False)
                key_energy_cap = f"{group}_{year}_{scenario}"
                energy_cap_data[key_energy_cap] = df_energy_cap
            else:
                print(f"File not found: {file_path}")
                all_found = False
# Check if all files were found
print("\n================= SUMMARY =================")
print(f"MSR files imported: {len(MSR_data)} / {len(country_code) * len(techs_MSR)}")
print(f"EnergyCap files imported: {len(energy_cap_data)} / {len(group_names) * len(years) * len(scenario_names)}")
if all_found:
    print("\n====== ALL FILES FOUND AND IMPORTED ======")
else:
    print("\n!! MISSING FILES !! CHECK  CTRY CODES, PATHS, NAMES, SCENARIOS")

#===================================================================================================================================================
#===================================================================================================================================================
# %%
# TOTAL INVESTMENTS (NPC) (I_t) and Save in Output File 
# Define CAPEX, Lifetime for each technology (newly installed)
CAPEX_New = {'BESS': 1774.915,'PHES': 3794.006,'Hydro': 7697.638,'OCGT': 1000, 'Transmission': 17.35} # $/kW

# Info Transmission Lines
length_10km = {'AGO:DRC': 16,'AGO:NAM': 53.8,'AGO:ZMB': 105,'BWA:NAM': 74.5,'BWA:ZAF': 20,'BWA:ZMB': 33.95, 'BWA:ZWE': 21.1, 'DRC:TZA': 123,
             'DRC:ZMB': 18.1,'LSO:ZAF':6.64,'MOZ_NC:MOZ_S': 90.2,'MOZ_NC:MWI': 21.8,'MOZ_NC:TZA': 105.4,'MOZ_NC:ZMB': 45,'MOZ_NC:ZWE': 25.2,
             'MOZ_S:SWZ': 14.4,'MOZ_S:ZAF': 28.6,'MOZ_S:ZWE': 40.2,'MWI:TZA': 80.5,'MWI:ZMB': 16.9,'NAM:ZMB': 21.7,'NAM:ZWE': 25.7,'NAM:ZAF': 44.2,
             'SWZ:ZAF': 13.3, 'TZA:ZMB': 67.1, 'ZAF:ZWE': 27.5, 'ZMB:ZWE': 17.1}
CAPEX_per_distance_New = 40.64 # $/kW/10km

I_t = {}              # Investment Cost
# Temporary storages
edges_400kV = {}      # Transmission Lines
PV_cap_by_msr = {}    # PV Capacity by MSR
W_cap_by_msr = {}     # Wind Capacity by MSR

for group in group_names:
    for year in years:
        for scenario in scenario_names:
            key_energy_cap = f"{group}_{year}_{scenario}"
            df_energy_cap = energy_cap_data[key_energy_cap]

            ##### PV Investment Calculation #####
            pv_total_scenario = 0
            pv_moz_partial = 0
            for ctry in country_code:
                # Filter Techs called PV_{ctry}_MSR{number}
                mask_ctry_pv = df_energy_cap['techs'].astype(str).str.match(fr'^PV_{ctry}_MSR\d+$')
                if not mask_ctry_pv.any():
                    I_t[f"{group}_{year}_{scenario}_{ctry}_PV_New"] = 0
                    continue
                pv_ctry = df_energy_cap.loc[(df_energy_cap['locs'] == ctry) & mask_ctry_pv,['techs', 'energy_cap']].copy()
                pv_ctry['msr_id'] = pv_ctry['techs'].astype(str).str.extract(r'_MSR(\d+)$')[0].astype('Int64')
                pv_by_msr = (pv_ctry.groupby('msr_id', as_index=False)['energy_cap'].sum().rename(columns={'energy_cap': 'cap_kw'}))
                PV_cap_by_msr[f"{group}_{year}_{scenario}_{ctry}_PV"] = pv_by_msr
                # Get MSR CAPEX Data
                msr_df = MSR_data.get(f"{ctry}_PV")
                if msr_df is None:
                    print(f"!!![WARNING] MSR Cluster Stats PV not found {ctry}!!!")
                    I_t[f"{group}_{year}_{scenario}_{ctry}_PV_New"] = 0
                else:
                    capex_cols = msr_df[['ClusterID', 'Weighted_CAPEX']].copy()
                    capex_cols['ClusterID'] = pd.to_numeric(capex_cols['ClusterID'], errors='coerce').astype('Int64')
                    capex_cols['Weighted_CAPEX'] = pd.to_numeric(capex_cols['Weighted_CAPEX'], errors='coerce')
                    
                    pv_join = pv_by_msr.merge(capex_cols, left_on='msr_id', right_on='ClusterID', how='left')
                    
                    miss = pv_join[pv_join['Weighted_CAPEX'].isna()]
                    if not miss.empty:
                        print(f"!!![WARNING] PV: CAPEX missing for {ctry}, MSR {miss['msr_id'].dropna().astype(int).tolist()}")
                    
                    pv_join['invest_M$'] = (pv_join['cap_kw'] * pv_join['Weighted_CAPEX']) / 1e6
                    ctry_total_pv = pv_join['invest_M$'].sum(skipna=True)
                    
                    I_t[f"{group}_{year}_{scenario}_{ctry}_PV_New"] = float(ctry_total_pv)
                    pv_total_scenario += float(ctry_total_pv)
                    
                    if ctry in ('MOZ_NC', 'MOZ_S'):
                        pv_moz_partial += float(ctry_total_pv)  
            I_t[f"{group}_{year}_{scenario}_MOZ_PV_New"] = float(pv_moz_partial)
            I_t[f"{group}_{year}_{scenario}_SAPP_PV_New"] = float(pv_total_scenario)

            ##### Wind Investment Calculation #####
            w_total_scenario = 0
            w_moz_partial = 0
            for ctry in country_code:
                # Filter Techs called Wind_{ctry}_MSR{number}
                mask_ctry_w = df_energy_cap['techs'].astype(str).str.match(fr'^Wind_{ctry}_MSR\d+$')
                if not mask_ctry_w.any():
                    I_t[f"{group}_{year}_{scenario}_{ctry}_W_New"] = 0
                    continue
                w_ctry = df_energy_cap.loc[(df_energy_cap['locs'] == ctry) & mask_ctry_w,['techs', 'energy_cap']].copy()
                w_ctry['msr_id'] = w_ctry['techs'].astype(str).str.extract(r'_MSR(\d+)$')[0].astype('Int64')
                w_by_msr = (w_ctry.groupby('msr_id', as_index=False)['energy_cap'].sum().rename(columns={'energy_cap': 'cap_kw'}))
                W_cap_by_msr[f"{group}_{year}_{scenario}_{ctry}_W"] = w_by_msr
                # Get MSR CAPEX Data
                msr_df = MSR_data.get(f"{ctry}_W")
                if msr_df is None:
                    print(f"!!![WARNING] MSR Cluster Stats W not found {ctry}!!!")
                    I_t[f"{group}_{year}_{scenario}_{ctry}_W_New"] = 0
                else:
                    capex_cols = msr_df[['ClusterID', 'Weighted_CAPEX']].copy()
                    capex_cols['ClusterID'] = pd.to_numeric(capex_cols['ClusterID'], errors='coerce').astype('Int64')
                    capex_cols['Weighted_CAPEX'] = pd.to_numeric(capex_cols['Weighted_CAPEX'], errors='coerce')
                    
                    w_join = w_by_msr.merge(capex_cols, left_on='msr_id', right_on='ClusterID', how='left')
                    
                    miss = w_join[w_join['Weighted_CAPEX'].isna()]
                    if not miss.empty:
                        print(f"!!![WARNING] W: CAPEX missing for {ctry}, MSR {miss['msr_id'].dropna().astype(int).tolist()}")
                    
                    w_join['invest_M$'] = (w_join['cap_kw'] * w_join['Weighted_CAPEX']) / 1e6
                    ctry_total_w = w_join['invest_M$'].sum(skipna=True)
                    
                    I_t[f"{group}_{year}_{scenario}_{ctry}_W_New"] = float(ctry_total_w)
                    w_total_scenario += float(ctry_total_w)
                    
                    if ctry in ('MOZ_NC', 'MOZ_S'):
                        w_moz_partial += float(ctry_total_w)   
            I_t[f"{group}_{year}_{scenario}_MOZ_W_New"] = float(w_moz_partial)
            I_t[f"{group}_{year}_{scenario}_SAPP_W_New"] = float(w_total_scenario)
            
            ##### BESS Investment Calculation #####
            if 'BESS_New' in df_energy_cap['techs'].values:
                total_investment = 0
                moz_partial = 0
                for ctry in country_code:
                    cap_kw = df_energy_cap.loc[(df_energy_cap['techs'] == 'BESS_New') & (df_energy_cap['locs'] == ctry),'energy_cap'].sum()
                    invest = CAPEX_New['BESS'] * cap_kw / 1e6 # M$
                    I_t[f"{group}_{year}_{scenario}_{ctry}_BESS_New"] = invest
                    total_investment += invest
                    if ctry in ['MOZ_NC', 'MOZ_S']:
                        moz_partial += invest
                I_t[f"{group}_{year}_{scenario}_MOZ_BESS_New"] = moz_partial
                I_t[f"{group}_{year}_{scenario}_SAPP_BESS_New"] = total_investment
            
            ##### PHES Investment Calculation #####
            if 'PHES_New' in df_energy_cap['techs'].values:
                total_investment = 0
                moz_partial = 0
                for ctry in country_code:
                    cap_kw = df_energy_cap.loc[(df_energy_cap['techs'] == 'PHES_New') & (df_energy_cap['locs'] == ctry),'energy_cap'].sum()
                    invest = CAPEX_New['PHES'] * cap_kw / 1e6 # M$
                    I_t[f"{group}_{year}_{scenario}_{ctry}_PHES_New"] = invest
                    total_investment += invest
                    if ctry in ['MOZ_NC', 'MOZ_S']:
                        moz_partial += invest
                I_t[f"{group}_{year}_{scenario}_MOZ_PHES_New"] = moz_partial
                I_t[f"{group}_{year}_{scenario}_SAPP_PHES_New"] = total_investment
            
            ##### OCGT Investment Calculation #####
            if 'OCGT_pp_New' in df_energy_cap['techs'].values:
                total_investment = 0
                moz_partial = 0
                for ctry in country_code:
                    cap_kw = df_energy_cap.loc[(df_energy_cap['techs'] == 'OCGT_pp_New') & (df_energy_cap['locs'] == ctry),'energy_cap'].sum()
                    invest = CAPEX_New['OCGT'] * cap_kw / 1e6 # M$
                    I_t[f"{group}_{year}_{scenario}_{ctry}_OCGT_New"] = invest
                    total_investment += invest
                    if ctry in ['MOZ_NC', 'MOZ_S']:
                        moz_partial += invest
                I_t[f"{group}_{year}_{scenario}_MOZ_OCGT_New"] = moz_partial
                I_t[f"{group}_{year}_{scenario}_SAPP_OCGT_New"] = total_investment
            
            ##### Hydro Investment Calculation #####
            mask_hydro = df_energy_cap['techs'].astype(str).str.match(r'^Hydro_Large_New(\b|_)')
            if mask_hydro.any():
                total_investment = 0
                moz_partial = 0
                for ctry in country_code:
                    cap_kw = df_energy_cap.loc[mask_hydro & (df_energy_cap['locs'] == ctry), 'energy_cap'].sum()
                    invest = CAPEX_New['Hydro'] * cap_kw / 1e6  # M$
                    I_t[f"{group}_{year}_{scenario}_{ctry}_Hydro_New"] = invest
                    total_investment += invest
                    if ctry in ['MOZ_NC', 'MOZ_S']:
                        moz_partial += invest
                I_t[f"{group}_{year}_{scenario}_MOZ_Hydro_New"] = moz_partial
                I_t[f"{group}_{year}_{scenario}_SAPP_Hydro_New"] = total_investment
            
            ##### Transmission Investment Calculation #####
            mask_transmission = df_energy_cap['techs'].astype(str).str.match(r'^400_kV_New(\b|_)')
            if mask_transmission.any():
                tx = df_energy_cap.loc[mask_transmission, ['locs', 'techs', 'energy_cap']].copy()
                # Create CTRY Code couples
                parts = tx['techs'].astype(str).str.partition(':')
                tx['peer'] = parts[2]  # tutto ciò che viene dopo i due punti
                tx['n1'] = tx['locs'].astype(str).str.strip()
                tx['n2'] = tx['peer'].astype(str).str.strip()
                uv = np.sort(tx[['n1', 'n2']].to_numpy(), axis=1)
                tx['u'] = uv[:, 0]
                tx['v'] = uv[:, 1]
                tx['edge'] = tx['u'] + ':' + tx['v']
                edges = (
                    tx.groupby('edge', as_index=False)
                    .agg(u=('u', 'first'),
                         v=('v', 'first'),
                         energy_cap_sum=('energy_cap', 'sum'),   # somma (tipicamente doppia)
                         energy_cap_mean=('energy_cap', 'mean'), # media (tipicamente uguale al valore per direzione)
                         n_dirs=('energy_cap', 'size'))          # quante direzioni viste (di solito 2)
                         )
                edges_400kV[key_energy_cap] = edges
                
                edges['cap_edge_kw'] = edges['energy_cap_sum'] / edges['n_dirs']
                edges['edge_key'] = edges['u'] + ':' + edges['v']
                edges['length_10km'] = edges['edge_key'].map(length_10km)
                missing_len = edges[edges['length_10km'].isna()]
                if not missing_len.empty:
                    print(f"[WARN] Mancano length_10km per: {missing_len['edge_key'].tolist()}")
                edges['unit_cost_per_kw_$'] = (CAPEX_New['Transmission'] + CAPEX_per_distance_New * (edges['length_10km']))
                edges['cost_line_M$']  = (edges['cap_edge_kw'] * edges['unit_cost_per_kw_$'])/1e6

                per_country = {ctry: 0 for ctry in country_code}
                scenario_total = 0
                
                for _, r in edges.iterrows():
                    if pd.isna(r['length_10km']):
                        continue
                    cost_line_M = float(r['cost_line_M$'])
                    I_t[f"{group}_{year}_{scenario}_{r.u}:{r.v}_Transmission_New"] = cost_line_M
                    share = cost_line_M / 2
                    per_country[r['u']] += share
                    per_country[r['v']] += share
                
                    scenario_total += cost_line_M

                for ctry, costM in per_country.items():
                    I_t[f"{group}_{year}_{scenario}_{ctry}_Transmission_New"] = float(costM)
                moz_partial = per_country.get('MOZ_NC', 0) + per_country.get('MOZ_S', 0)
                I_t[f"{group}_{year}_{scenario}_MOZ_Transmission_New"] = float(moz_partial)
                I_t[f"{group}_{year}_{scenario}_SAPP_Transmission_New"] = float(scenario_total)
                edges_400kV[key_energy_cap] = edges

tech_suffixes = ["BESS_New", "PHES_New", "OCGT_New", "Hydro_New","Transmission_New", "PV_New", "W_New"]

rows = []
for group in group_names:
    for year in years:
        for scenario in scenario_names:
            prefix = f"{group}_{year}_{scenario}_"
            for k, v in I_t.items():
                if not k.startswith(prefix):
                    continue
                suffix = k[len(prefix):]
                tech = next((t for t in tech_suffixes if suffix.endswith(t)), None)
                if tech is None:
                    continue
                loc = suffix[:-(len(tech) + 1)] if len(suffix) > len(tech) else ""
                if ":" in loc:
                    continue
                rows.append({"group": group,"year": year,"scenario": scenario,"location": loc,"tech": tech,"invest_M$": float(v)})
invest_df = pd.DataFrame(rows)

tech_order = ["PV_New", "W_New", "Hydro_New", "OCGT_New", "BESS_New", "PHES_New", "Transmission_New"]
output_dir = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\Results")
output_dir.mkdir(parents=True, exist_ok=True)

for group in group_names:
    out_xlsx = output_dir / f"Investments_{group}.xlsx"
    with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        for scenario in scenario_names:
            sub = invest_df[(invest_df["group"] == group) & (invest_df["scenario"] == scenario)]
            if sub.empty:
                continue

            # pivot: righe=(location, tech), colonne=year
            pivot = (sub.pivot_table(index=["location", "tech"],
                                     columns="year",
                                     values="invest_M$",
                                     aggfunc="sum",
                                     fill_value=0.0)
                         .reindex(columns=years))  # 2030/2035/2040

            # ---- ORDINE RIGHE: alfabetico per paese, con SAPP in coda ----
            locs = sorted(sub["location"].unique().tolist())
            if "SAPP" in locs:
                locs.remove("SAPP")
            loc_order = locs + ["SAPP"]  # SAPP per ultimo

            # applica ordinamento per location e per tecnologia
            tmp = pivot.reset_index()
            tmp["location"] = pd.Categorical(tmp["location"], categories=loc_order, ordered=True)
            tmp["tech"] = pd.Categorical(tmp["tech"], categories=tech_order, ordered=True)
            pivot_sorted = tmp.sort_values(["location", "tech"]).set_index(["location", "tech"])

            # scrivi sullo sheet (nome <= 31 char)
            sheet_name = scenario[:31]
            pivot_sorted.to_excel(writer, sheet_name=sheet_name)

    print(f"[OK] Esportato: {out_xlsx}")

#===================================================================================================================================================
#===================================================================================================================================================
#%%
# ANNUALIZED INVESTMENT COSTS (A_t) and Save in Output File
r = 0.10  # discount rate
lifetime_years = {'PV_New': 25,'W_New': 25,'BESS_New': 15,'PHES_New': 40,'Hydro_New': 50,'OCGT_New': 30, 'Transmission_New': 40}

invest_ann = invest_df.copy()
invest_ann["lifetime"] = invest_ann["tech"].map(lifetime_years)

missing = invest_ann[invest_ann["lifetime"].isna()]["tech"].unique().tolist()
if missing:
    print(f"[WARN] Lifetime missing for: {missing}")

invest_ann["CRF"] = (r * ((1 + r)**invest_ann["lifetime"])) / (((1 + r)**invest_ann["lifetime"]) - 1)
invest_ann["annual_M$"] = invest_ann["invest_M$"] * invest_ann["CRF"]

tech_order = ["PV_New", "W_New", "Hydro_New", "OCGT_New", "BESS_New", "PHES_New", "Transmission_New"]

for group in group_names:
    out_xlsx = output_dir / f"Annualized_Investments_{group}.xlsx"
    with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        for scenario in scenario_names:
            sub = invest_ann[(invest_ann["group"] == group) & (invest_ann["scenario"] == scenario)]
            if sub.empty:
                continue

            # pivot: righe = (location, tech), colonne = year, valori = annual_M$
            pivot = (sub.pivot_table(index=["location", "tech"],
                                     columns="year",
                                     values="annual_M$",
                                     aggfunc="sum",
                                     fill_value=0.0)
                         .reindex(columns=years))

            # — ordinamento righe: alfabetico per paese, SAPP in coda —
            locs = sorted(sub["location"].unique().tolist())
            if "SAPP" in locs:
                locs.remove("SAPP")
            loc_order = locs + ["SAPP"]

            tmp = pivot.reset_index()
            tmp["location"] = pd.Categorical(tmp["location"], categories=loc_order, ordered=True)
            tmp["tech"] = pd.Categorical(tmp["tech"], categories=tech_order, ordered=True)
            pivot_sorted = tmp.sort_values(["location", "tech"]).set_index(["location", "tech"])

            sheet_name = scenario[:31]
            pivot_sorted.to_excel(writer, sheet_name=sheet_name)

    print(f"[OK] Esportato annualizzato: {out_xlsx}")

#===================================================================================================================================================
#===================================================================================================================================================    
#%%
# FIXED ANNUAL O&M Costs (F_t) and Save in Output File
OPEX_New = {'PV_New': 20,'W_New': 28,'BESS_New': 40.309,'PHES_New': 20.15,'Hydro_New': 42.5,'OCGT_New': 40} # $/kW/year

# Calculate Fixed O&M Costs
F_t = {}  # M$/yr
for group in group_names:
    for year in years:
        for scenario in scenario_names:
            key_energy_cap = f"{group}_{year}_{scenario}"
            df_energy_cap = energy_cap_data[key_energy_cap]

            # ---------------- PV ----------------
            total_sc = 0.0; moz_partial = 0.0
            for ctry in country_code:
                mask_ctry_pv = df_energy_cap['techs'].astype(str).str.match(fr'^PV_{ctry}_MSR\d+$')
                cap_kw = df_energy_cap.loc[(df_energy_cap['locs'] == ctry) & mask_ctry_pv, 'energy_cap'].sum()
                cost = (OPEX_New['PV_New'] * cap_kw) / 1e6
                F_t[f"{group}_{year}_{scenario}_{ctry}_PV_New"] = float(cost)
                total_sc += cost
                if ctry in ('MOZ_NC', 'MOZ_S'): moz_partial += cost
            F_t[f"{group}_{year}_{scenario}_MOZ_PV_New"] = float(moz_partial)
            F_t[f"{group}_{year}_{scenario}_SAPP_PV_New"] = float(total_sc)

            # ---------------- Wind ----------------
            total_sc = 0.0; moz_partial = 0.0
            for ctry in country_code:
                mask_ctry_w = df_energy_cap['techs'].astype(str).str.match(fr'^(W|Wind)_{ctry}_MSR\d+$')
                cap_kw = df_energy_cap.loc[(df_energy_cap['locs'] == ctry) & mask_ctry_w, 'energy_cap'].sum()
                cost = (OPEX_New['W_New'] * cap_kw) / 1e6
                F_t[f"{group}_{year}_{scenario}_{ctry}_W_New"] = float(cost)
                total_sc += cost
                if ctry in ('MOZ_NC', 'MOZ_S'): moz_partial += cost
            F_t[f"{group}_{year}_{scenario}_MOZ_W_New"] = float(moz_partial)
            F_t[f"{group}_{year}_{scenario}_SAPP_W_New"] = float(total_sc)
            # ---------------- BESS ----------------
            total_sc = 0.0; moz_partial = 0.0
            for ctry in country_code:
                cap_kw = df_energy_cap.loc[
                    (df_energy_cap['techs'] == 'BESS_New') & (df_energy_cap['locs'] == ctry), 'energy_cap'
                ].sum()
                cost = (OPEX_New['BESS_New'] * cap_kw) / 1e6  # M$/yr
                F_t[f"{group}_{year}_{scenario}_{ctry}_BESS_New"] = float(cost)
                total_sc += cost
                if ctry in ('MOZ_NC', 'MOZ_S'): moz_partial += cost
            F_t[f"{group}_{year}_{scenario}_MOZ_BESS_New"] = float(moz_partial)
            F_t[f"{group}_{year}_{scenario}_SAPP_BESS_New"] = float(total_sc)

            # ---------------- PHES ----------------
            total_sc = 0.0; moz_partial = 0.0
            for ctry in country_code:
                cap_kw = df_energy_cap.loc[
                    (df_energy_cap['techs'] == 'PHES_New') & (df_energy_cap['locs'] == ctry), 'energy_cap'
                ].sum()
                cost = (OPEX_New['PHES_New'] * cap_kw) / 1e6
                F_t[f"{group}_{year}_{scenario}_{ctry}_PHES_New"] = float(cost)
                total_sc += cost
                if ctry in ('MOZ_NC', 'MOZ_S'): moz_partial += cost
            F_t[f"{group}_{year}_{scenario}_MOZ_PHES_New"] = float(moz_partial)
            F_t[f"{group}_{year}_{scenario}_SAPP_PHES_New"] = float(total_sc)

            # ---------------- OCGT ----------------
            total_sc = 0.0; moz_partial = 0.0
            for ctry in country_code:
                cap_kw = df_energy_cap.loc[
                    (df_energy_cap['techs'] == 'OCGT_pp_New') & (df_energy_cap['locs'] == ctry), 'energy_cap'
                ].sum()
                cost = (OPEX_New['OCGT_New'] * cap_kw) / 1e6
                F_t[f"{group}_{year}_{scenario}_{ctry}_OCGT_New"] = float(cost)
                total_sc += cost
                if ctry in ('MOZ_NC', 'MOZ_S'): moz_partial += cost
            F_t[f"{group}_{year}_{scenario}_MOZ_OCGT_New"] = float(moz_partial)
            F_t[f"{group}_{year}_{scenario}_SAPP_OCGT_New"] = float(total_sc)

            # ---------------- Hydro_Large_New ----------------
            mask_hydro = df_energy_cap['techs'].astype(str).str.match(r'^Hydro_Large_New(\b|_)')
            total_sc = 0.0; moz_partial = 0.0
            for ctry in country_code:
                cap_kw = df_energy_cap.loc[mask_hydro & (df_energy_cap['locs'] == ctry), 'energy_cap'].sum()
                cost = (OPEX_New['Hydro_New'] * cap_kw) / 1e6
                F_t[f"{group}_{year}_{scenario}_{ctry}_Hydro_New"] = float(cost)
                total_sc += cost
                if ctry in ('MOZ_NC', 'MOZ_S'): moz_partial += cost
            F_t[f"{group}_{year}_{scenario}_MOZ_Hydro_New"] = float(moz_partial)
            F_t[f"{group}_{year}_{scenario}_SAPP_Hydro_New"] = float(total_sc)

# Save in Output FIle
tech_suffixes_fixed = ["PV_New", "W_New", "Hydro_New", "OCGT_New", "BESS_New", "PHES_New"]
F_rows = []
for group in group_names:
    for year in years:
        for scenario in scenario_names:
            prefix = f"{group}_{year}_{scenario}_"
            for k, v in F_t.items():
                if not k.startswith(prefix):
                    continue
                suffix = k[len(prefix):]
                tech = next((t for t in tech_suffixes_fixed if suffix.endswith(t)), None)
                if tech is None:
                    continue
                loc = suffix[:-(len(tech) + 1)] if len(suffix) > len(tech) else ""
                if ":" in loc:
                    continue
                F_rows.append({
                    "group": group, "year": year, "scenario": scenario,
                    "location": loc, "tech": tech, "F_M$yr": float(v)
                })
omfix_df = pd.DataFrame(F_rows)
tech_order = ["PV_New", "W_New", "Hydro_New", "OCGT_New", "BESS_New", "PHES_New"]
for group in group_names:
    out_xlsx = output_dir / f"O&M_Fixed_Yearly_Costs_{group}.xlsx"
    with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        for scenario in scenario_names:
            sub = omfix_df[(omfix_df["group"] == group) & (omfix_df["scenario"] == scenario)]
            if sub.empty:
                continue

            pivot = (sub.pivot_table(index=["location", "tech"],
                                     columns="year",
                                     values="F_M$yr",
                                     aggfunc="sum",
                                     fill_value=0.0)
                         .reindex(columns=years))

            locs = sorted(sub["location"].unique().tolist())
            if "SAPP" in locs:
                locs.remove("SAPP")
            loc_order = locs + ["SAPP"]

            tmp = pivot.reset_index()
            tmp["location"] = pd.Categorical(tmp["location"], categories=loc_order, ordered=True)
            tmp["tech"] = pd.Categorical(tmp["tech"], categories=tech_order, ordered=True)
            pivot_sorted = tmp.sort_values(["location", "tech"]).set_index(["location", "tech"])

            sheet_name = scenario[:31]
            pivot_sorted.to_excel(writer, sheet_name=sheet_name)

    print(f"[OK] Exported fixed O&M: {out_xlsx}")

#===================================================================================================================================================
#===================================================================================================================================================
#%%
# VARIABLE ANNUAL O&M Costs (V_t) and Save in Output File
import re
from collections import defaultdict

# Calcola SOLO PHES_New e OCGT_New. Le altre tecnologie verranno impostate a 0 in fase di output.
def accumulate_var_costs_csv_phes_ocgt(csv_path: Path, country_code: list[str], chunksize: int = 1_000_000):
    acc_usd = defaultdict(float)

    usecols = ['costs', 'locs', 'techs', 'timesteps', 'cost_var']  # read just what is needed
    dtypes  = {
        'costs': 'category',
        'locs': 'string',
        'techs': 'string',
        'timesteps': 'string',     # sommiamo su tutti i timesteps
        'cost_var': 'float64',
    }

    try:
        reader = pd.read_csv(csv_path, usecols=usecols, dtype=dtypes,
                             engine='pyarrow', chunksize=chunksize)
    except Exception:
        reader = pd.read_csv(csv_path, usecols=usecols, dtype=dtypes,
                             chunksize=chunksize)

    for chunk in reader:
        # filtra solo i costi monetari
        chunk = chunk[chunk['costs'] == 'monetary']
        if chunk.empty:
            continue

        locs = chunk['locs']  # string

        # ===== PHES_New =====
        m = (chunk['techs'] == 'PHES_New')
        if m.any():
            g = chunk.loc[m].groupby(locs[m])['cost_var'].sum()
            for ct, val in g.items():
                acc_usd[(str(ct), 'PHES_New')] += float(val)

        # ===== OCGT_pp_New → OCGT_New =====
        m = (chunk['techs'] == 'OCGT_pp_New')
        if m.any():
            g = chunk.loc[m].groupby(locs[m])['cost_var'].sum()
            for ct, val in g.items():
                acc_usd[(str(ct), 'OCGT_New')] += float(val)

    # Derivati: MOZ (MOZ_NC + MOZ_S) e SAPP (somma di tutti i paesi)
    for bk in ['PHES_New', 'OCGT_New']:
        moz = acc_usd.get(('MOZ_NC', bk), 0.0) + acc_usd.get(('MOZ_S', bk), 0.0)
        sapp = sum(acc_usd[(ct, bk)] for ct in country_code if (ct, bk) in acc_usd)
        acc_usd[('MOZ', bk)] = moz
        acc_usd[('SAPP', bk)] = sapp

    # USD → M$
    return {(ct, bk): val / 1e6 for (ct, bk), val in acc_usd.items()}

tech_order = ["PV_New", "W_New", "Hydro_New", "OCGT_New", "BESS_New", "PHES_New"]  # stesso ordine degli altri export
all_locations = country_code + ['MOZ', 'SAPP']  # includiamo sempre anche MOZ e SAPP

V_rows = []
missing_any = False

for group in group_names:
    for year in years:
        for scenario in scenario_names:
            file_name = "results_cost_var.csv"
            file_path = results_path / group / year / f"Results_{group}_{scenario}" / file_name
            if not file_path.exists():
                print(f"[MISS] {file_path}")
                missing_any = True
                continue

            acc = accumulate_var_costs_csv_phes_ocgt(file_path, country_code, chunksize=1_000_000)

            for loc in all_locations:
                for bucket in tech_order:
                    musd = acc.get((loc, bucket), 0.0)
                    V_rows.append({
                        "group": group,
                        "year": year,
                        "scenario": scenario,
                        "location": str(loc),
                        "tech": bucket,
                        "VarCost_M$": float(musd)
                    })

var_df = pd.DataFrame(V_rows)

expected_cols = {"group","year","scenario","location","tech","VarCost_M$"}
missing_cols = expected_cols - set(var_df.columns)
assert not missing_cols, f"Mancano colonne in var_df: {missing_cols}"

output_dir = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\Results")
output_dir.mkdir(parents=True, exist_ok=True)

for group in group_names:
    out_xlsx = output_dir / f"O&M_Variable_Costs_{group}.xlsx"
    with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        for scenario in scenario_names:
            sub = var_df[(var_df["group"] == group) & (var_df["scenario"] == scenario)]
            if sub.empty:
                continue

            pivot = (sub.pivot_table(index=["location","tech"],
                                     columns="year",
                                     values="VarCost_M$",
                                     aggfunc="sum",
                                     fill_value=0.0)
                         .reindex(columns=years))

            # ordine paesi alfabetico con SAPP in coda
            locs = sorted(sub["location"].unique().tolist())
            if "SAPP" in locs:
                locs.remove("SAPP")
            loc_order = locs + ["SAPP"]

            tmp = pivot.reset_index()
            tmp["location"] = pd.Categorical(tmp["location"], categories=loc_order, ordered=True)
            tmp["tech"] = pd.Categorical(tmp["tech"], categories=tech_order, ordered=True)
            pivot_sorted = tmp.sort_values(["location","tech"]).set_index(["location","tech"])

            sheet_name = scenario[:31]  # limite Excel
            pivot_sorted.to_excel(writer, sheet_name=sheet_name)

    print(f"[OK] Exported variable O&M: {out_xlsx}")

if missing_any:
    print("\n[WARN] Alcuni results_cost_var.csv non trovati. Verifica paths/scenari.")

#===================================================================================================================================================
#===================================================================================================================================================
#%%
# YEARLY MWh ELECTRICITY PRODUCTION [GWh] (E_t) and Save in Output File
import re
from collections import defaultdict

PAT_MSR = re.compile(r'^(PV|W|Wind)_([A-Z_]+)_MSR\d+$')

def accumulate_prod_csv(csv_path: Path, country_code: list[str], chunksize: int = 1_000_000):
    acc_kwh = defaultdict(float)

    usecols = ['carriers', 'locs', 'techs', 'timesteps', 'carrier_prod']  # dati in kWh
    dtypes  = {
        'carriers': 'category',
        'locs': 'string',
        'techs': 'string',
        'timesteps': 'string',
        'carrier_prod': 'float64',
    }
    try:
        reader = pd.read_csv(csv_path, usecols=usecols, dtype=dtypes,
                             engine='pyarrow', chunksize=chunksize)
    except Exception:
        reader = pd.read_csv(csv_path, usecols=usecols, dtype=dtypes,
                             chunksize=chunksize)
    for chunk in reader:
        chunk = chunk[chunk['carriers'] == 'electricity']
        if chunk.empty:
            continue
        # ===== PV / W  MSR =====
        mw = chunk['techs'].str.extract(PAT_MSR)
        mask_pvw = mw[0].notna()
        if mask_pvw.any():
            base = mw.loc[mask_pvw, 0]     # 'PV' | 'W' | 'Wind'
            ctry = mw.loc[mask_pvw, 1]     # es. ZAF, MOZ_NC, MOZ_S, ...
            bucket = pd.Series('W_New', index=base.index)
            bucket[base == 'PV'] = 'PV_New'
            sub = pd.DataFrame({
                '_ctry': ctry.astype('string'),
                '_bucket': bucket,
                'carrier_prod': chunk.loc[mask_pvw, 'carrier_prod'].to_numpy()
            })
            g = sub.groupby(['_ctry', '_bucket'], observed=True)['carrier_prod'].sum()
            for (ct, bk), val in g.items():
                acc_kwh[(str(ct), str(bk))] += float(val)
        # ===== BESS / PHES / OCGT / Hydro (paese = locs) =====
        locs = chunk['locs']  # string
        # BESS
        m = (chunk['techs'] == 'BESS_New')
        if m.any():
            g = chunk.loc[m].groupby(locs[m])['carrier_prod'].sum()
            for ct, val in g.items():
                acc_kwh[(str(ct), 'BESS_New')] += float(val)
        # PHES
        m = (chunk['techs'] == 'PHES_New')
        if m.any():
            g = chunk.loc[m].groupby(locs[m])['carrier_prod'].sum()
            for ct, val in g.items():
                acc_kwh[(str(ct), 'PHES_New')] += float(val)
        # OCGT (rinomina a OCGT_New)
        m = (chunk['techs'] == 'OCGT_pp_New')
        if m.any():
            g = chunk.loc[m].groupby(locs[m])['carrier_prod'].sum()
            for ct, val in g.items():
                acc_kwh[(str(ct), 'OCGT_New')] += float(val)
        # Hydro (prefisso)
        m = chunk['techs'].str.startswith('Hydro_Large_New', na=False)
        if m.any():
            g = chunk.loc[m].groupby(locs[m])['carrier_prod'].sum()
            for ct, val in g.items():
                acc_kwh[(str(ct), 'Hydro_New')] += float(val)

    for bk in ['PV_New', 'W_New', 'BESS_New', 'PHES_New', 'OCGT_New', 'Hydro_New']:
        moz = acc_kwh.get(('MOZ_NC', bk), 0.0) + acc_kwh.get(('MOZ_S', bk), 0.0)
        sapp = sum(acc_kwh[(ct, bk)] for ct in country_code if (ct, bk) in acc_kwh)
        acc_kwh[('MOZ', bk)] = moz
        acc_kwh[('SAPP', bk)] = sapp

    return {(ct, bk): val / 1e6 for (ct, bk), val in acc_kwh.items()} # kWh to GWh

tech_order = ["PV_New", "W_New", "Hydro_New", "OCGT_New", "BESS_New", "PHES_New"]  # stesso ordine degli altri export
all_locations = country_code + ['MOZ', 'SAPP']

PROD_rows = []
missing_any = False

for group in group_names:
    for year in years:
        for scenario in scenario_names:
            file_name = "results_carrier_prod.csv"
            file_path = results_path / group / year / f"Results_{group}_{scenario}" / file_name
            if not file_path.exists():
                print(f"[MISS] {file_path}")
                missing_any = True
                continue

            acc = accumulate_prod_csv(file_path, country_code, chunksize=1_000_000)

            for loc in all_locations:
                for bucket in tech_order:
                    gwh = acc.get((loc, bucket), 0.0)
                    PROD_rows.append({
                        "group": group,
                        "year": year,
                        "scenario": scenario,
                        "location": str(loc),
                        "tech": bucket,
                        "Prod_GWh": float(gwh)
                    })

prod_df = pd.DataFrame(PROD_rows)

expected_cols = {"group","year","scenario","location","tech","Prod_GWh"}
missing_cols = expected_cols - set(prod_df.columns)
assert not missing_cols, f"Mancano colonne in prod_df: {missing_cols}"

output_dir = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\Results")
output_dir.mkdir(parents=True, exist_ok=True)

for group in group_names:
    out_xlsx = output_dir / f"Electricity_Production_GWh_{group}.xlsx"
    with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        for scenario in scenario_names:
            sub = prod_df[(prod_df["group"] == group) & (prod_df["scenario"] == scenario)]
            if sub.empty:
                continue

            pivot = (sub.pivot_table(index=["location","tech"],
                                     columns="year",
                                     values="Prod_GWh",
                                     aggfunc="sum",
                                     fill_value=0.0)
                         .reindex(columns=years))

            locs = sorted(sub["location"].unique().tolist())
            if "SAPP" in locs:
                locs.remove("SAPP")
            loc_order = locs + ["SAPP"]

            tmp = pivot.reset_index()
            tmp["location"] = pd.Categorical(tmp["location"], categories=loc_order, ordered=True)
            tmp["tech"] = pd.Categorical(tmp["tech"], categories=tech_order, ordered=True)
            pivot_sorted = tmp.sort_values(["location","tech"]).set_index(["location","tech"])

            sheet_name = scenario[:31]
            pivot_sorted.to_excel(writer, sheet_name=sheet_name)

    print(f"[OK] Exported electricity production (GWh): {out_xlsx}")

if missing_any:
    print("\n[WARN] Alcuni results_carrier_prod.csv non trovati. Verifica paths/scenari.")

#===================================================================================================================================================
#===================================================================================================================================================
# %%
# UNMET DEMAND (U_t) and Save in Output File
from collections import defaultdict
import math

def accumulate_unmet_csv(csv_path: Path, country_code: list[str], chunksize: int = 1000000):
    acc_peak = defaultdict(lambda: -math.inf)  # kWh
    acc_pos  = defaultdict(float)              # kWh
    acc_neg  = defaultdict(float)              # kWh

    usecols = ['carriers', 'locs', 'timesteps', 'unmet_demand']  # kWh
    dtypes  = {
        'carriers': 'category',
        'locs': 'string',
        'timesteps': 'string',
        'unmet_demand': 'float64',
    }

    try:
        reader = pd.read_csv(csv_path, usecols=usecols, dtype=dtypes,
                             engine='pyarrow', chunksize=chunksize)
    except Exception:
        reader = pd.read_csv(csv_path, usecols=usecols, dtype=dtypes, chunksize=chunksize)

    for chunk in reader:
        # solo electricity (come da specifica: carriers contiene solo 'electricity', ma filtriamo per robustezza)
        chunk = chunk[chunk['carriers'] == 'electricity']
        if chunk.empty:
            continue

        # per efficienza, calcolo per loc direttamente sul chunk
        for loc, s in chunk.groupby('locs')['unmet_demand']:
            # s è una Serie in kWh
            vmax = s.max() if not s.empty else float('-inf')
            vpos = s[s > 0].sum() if not s.empty else 0.0
            vneg = s[s < 0].sum() if not s.empty else 0.0

            # peak = max globale su tutti i chunk
            if vmax > acc_peak[loc]:
                acc_peak[loc] = float(vmax)
            acc_pos[loc] += float(vpos)
            acc_neg[loc] += float(vneg)

    # Assicura che tutti i paesi esistano anche se non trovati
    for ct in country_code:
        _ = acc_peak[ct]; _ = acc_pos[ct]; _ = acc_neg[ct]

    # MOZ = MOZ_NC + MOZ_S (somma delle metriche finali)
    moz_peak = (acc_peak.get('MOZ_NC', -math.inf) if acc_peak.get('MOZ_NC', -math.inf) != -math.inf else 0.0) \
             + (acc_peak.get('MOZ_S',  -math.inf) if acc_peak.get('MOZ_S',  -math.inf)  != -math.inf else 0.0)
    moz_pos  = acc_pos.get('MOZ_NC', 0.0) + acc_pos.get('MOZ_S', 0.0)
    moz_neg  = acc_neg.get('MOZ_NC', 0.0) + acc_neg.get('MOZ_S', 0.0)

    # SAPP = somma di tutti i paesi della lista (inclusi MOZ_NC e MOZ_S, NON aggiungere il MOZ aggregato)
    sapp_peak = 0.0; sapp_pos = 0.0; sapp_neg = 0.0
    for ct in country_code:
        pk = acc_peak.get(ct, -math.inf)
        pk = 0.0 if pk == -math.inf else pk
        sapp_peak += pk
        sapp_pos  += acc_pos.get(ct, 0.0)
        sapp_neg  += acc_neg.get(ct, 0.0)

    # conversione kWh → GWh
    def kwh_to_gwh(x): return x / 1e6

    out = {}
    # paesi base
    for ct in country_code:
        pk = acc_peak.get(ct, -math.inf)
        pk = 0.0 if pk == -math.inf else pk
        out[ct] = {
            "Peak_Unmet":    kwh_to_gwh(pk),
            "Total_Unmet":   kwh_to_gwh(acc_pos.get(ct, 0.0)),
            "Total_Surplus": kwh_to_gwh(acc_neg.get(ct, 0.0)),
        }
    # MOZ e SAPP
    out['MOZ']  = {"Peak_Unmet": kwh_to_gwh(moz_peak),  "Total_Unmet": kwh_to_gwh(moz_pos),  "Total_Surplus": kwh_to_gwh(moz_neg)}
    out['SAPP'] = {"Peak_Unmet": kwh_to_gwh(sapp_peak), "Total_Unmet": kwh_to_gwh(sapp_pos), "Total_Surplus": kwh_to_gwh(sapp_neg)}
    return out

# ordine metriche e locations per export
metric_order = ["Peak_Unmet", "Total_Unmet", "Total_Surplus"]
all_locations = country_code + ['MOZ', 'SAPP']

UNMET_rows = []
missing_any = False

for group in group_names:
    for year in years:
        for scenario in scenario_names:
            file_name = "results_unmet_demand.csv"
            file_path = results_path / group / year / f"Results_{group}_{scenario}" / file_name
            if not file_path.exists():
                print(f"[MISS] {file_path}")
                missing_any = True
                # anche se manca, inseriamo righe zero per coerenza
                for loc in all_locations:
                    for metric in metric_order:
                        UNMET_rows.append({
                            "group": group, "year": year, "scenario": scenario,
                            "location": str(loc), "metric": metric, "value": 0.0
                        })
                continue

            acc = accumulate_unmet_csv(file_path, country_code, chunksize=1_000_000)

            for loc in all_locations:
                vals = acc.get(loc, {"Peak_Unmet": 0.0, "Total_Unmet": 0.0, "Total_Surplus": 0.0})
                for metric in metric_order:
                    UNMET_rows.append({
                        "group": group,
                        "year": year,
                        "scenario": scenario,
                        "location": str(loc),
                        "metric": metric,
                        "value": float(vals.get(metric, 0.0))
                    })

unmet_df = pd.DataFrame(UNMET_rows)

# controllo colonne
expected_cols = {"group","year","scenario","location","metric","value"}
missing_cols = expected_cols - set(unmet_df.columns)
assert not missing_cols, f"Mancano colonne in unmet_df: {missing_cols}"

# export XLSX: un file per group, uno sheet per scenario; righe=(location, metric), colonne=year
for group in group_names:
    out_xlsx = output_dir / f"Unmet_Demand_GWh_{group}.xlsx"
    with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        for scenario in scenario_names:
            sub = unmet_df[(unmet_df["group"] == group) & (unmet_df["scenario"] == scenario)]
            if sub.empty:
                # comunque crea uno sheet vuoto coerente
                pd.DataFrame(columns=years).to_excel(writer, sheet_name=scenario[:31])
                continue

            pivot = (sub.pivot_table(index=["location","metric"],
                                     columns="year",
                                     values="value",
                                     aggfunc="sum",
                                     fill_value=0.0)
                         .reindex(columns=years))

            # ordine: paesi alfabetici con SAPP in coda; metriche nell'ordine definito
            locs = sorted(sub["location"].unique().tolist())
            if "SAPP" in locs:
                locs.remove("SAPP")
            loc_order = locs + ["SAPP"]

            tmp = pivot.reset_index()
            tmp["location"] = pd.Categorical(tmp["location"], categories=loc_order, ordered=True)
            tmp["metric"]   = pd.Categorical(tmp["metric"],   categories=metric_order, ordered=True)
            pivot_sorted = tmp.sort_values(["location","metric"]).set_index(["location","metric"])

            sheet_name = scenario[:31]
            pivot_sorted.to_excel(writer, sheet_name=sheet_name)

    print(f"[OK] Exported unmet demand (GWh): {out_xlsx}")

if missing_any:
    print("\n[WARN] Alcuni results_unmet_demand.csv non trovati. Verifica paths/scenari.")
#===================================================================================================================================================
#===================================================================================================================================================
# %%
# TRANSMISSION LINES DATA, SPECIFIC TO EACH PAIR OF COUNTRIES (INVESTMENTS + OPEX + ELECTRICITY OUTPUT)
from collections import defaultdict
from openpyxl.styles import Alignment

output_dir = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\Results")
output_dir.mkdir(parents=True, exist_ok=True)

TX_TECH_NAME = "Transmission_New"
OPEX_PER_KWH = 0.0076        # USD per kWh
GROUP_TX     = "Transmission_Expansion"

# fallback per length_10km se esegui solo questa sezione
try:
    _ = length_10km
except NameError:
    length_10km = {
        'AGO:DRC': 16,'AGO:NAM': 53.8,'AGO:ZMB': 105,'BWA:NAM': 74.5,'BWA:ZAF': 20,'BWA:ZMB': 33.95,'BWA:ZWE': 21.1,
        'DRC:TZA': 123,'DRC:ZMB': 18.1,'LSO:ZAF': 6.64,'MOZ_NC:MOZ_S': 90.2,'MOZ_NC:MWI': 21.8,'MOZ_NC:TZA': 105.4,
        'MOZ_NC:ZMB': 45,'MOZ_NC:ZWE': 25.2,'MOZ_S:SWZ': 14.4,'MOZ_S:ZAF': 28.6,'MOZ_S:ZWE': 40.2,'MWI:TZA': 80.5,
        'MWI:ZMB': 16.9,'NAM:ZMB': 21.7,'NAM:ZWE': 25.7,'NAM:ZAF': 44.2,'SWZ:ZAF': 13.3,'TZA:ZMB': 67.1,
        'ZAF:ZWE': 27.5,'ZMB:ZWE': 17.1
    }
    print("[INFO][TX] length_10km fallback attivato.")

def edges_from_energy_cap(df_energy_cap: pd.DataFrame) -> pd.DataFrame:
    """Restituisce DF con colonne: u, v, cap_edge_kw, cost_line_M$ (investment totale per linea)"""
    m = df_energy_cap['techs'].astype(str).str.match(r'^400_kV_New(\b|_)', na=False)
    if not m.any():
        return pd.DataFrame(columns=['u','v','cap_edge_kw','cost_line_M$'])
    tx = df_energy_cap.loc[m, ['locs','techs','energy_cap']].copy()
    parts = tx['techs'].astype(str).str.partition(':')
    tx['peer'] = parts[2].astype(str).str.strip()
    tx['n1']  = tx['locs'].astype(str).str.strip()
    tx['n2']  = tx['peer']
    uv = np.sort(tx[['n1','n2']].to_numpy(), axis=1)
    tx['u'] = uv[:,0]; tx['v'] = uv[:,1]
    edges = (tx.groupby(['u','v'], as_index=False)
               .agg(energy_cap_sum=('energy_cap','sum'),
                    n_dirs=('energy_cap','size')))
    edges['cap_edge_kw'] = edges['energy_cap_sum'] / edges['n_dirs']

    # CAPEX unitario
    CAPEX_BASE_PER_KW = 17.35
    CAPEX_PER_DISTANCE_PER_KW_PER_10KM = 40.64
    edges['edge_key'] = edges['u'] + ':' + edges['v']
    edges['length_10km'] = edges['edge_key'].map(length_10km)
    miss = edges['length_10km'].isna()
    if miss.any():
        print(f"[WARN][TX] mancanti length_10km per: {edges.loc[miss,'edge_key'].tolist()} → investment=0")
    unit_cost = (CAPEX_BASE_PER_KW + CAPEX_PER_DISTANCE_PER_KW_PER_10KM * edges['length_10km']).fillna(0.0)
    edges['cost_line_M$'] = (edges['cap_edge_kw'] * unit_cost) / 1e6
    return edges[['u','v','cap_edge_kw','cost_line_M$']]

def kwh_out_on_edge(csv_path: Path, u: str, v: str, chunksize: int = 1_000_000) -> float:
    """kWh totali sulla linea u–v (somma delle due direzioni). Ritorna kWh (non GWh)."""
    usecols=['carriers','locs','techs','carrier_prod']
    dtypes = {'carriers':'category','locs':'string','techs':'string','carrier_prod':'float64'}
    tot = 0.0
    try:
        reader = pd.read_csv(csv_path, usecols=usecols, dtype=dtypes, engine='pyarrow', chunksize=chunksize)
    except Exception:
        reader = pd.read_csv(csv_path, usecols=usecols, dtype=dtypes, chunksize=chunksize)
    patt_uv = f"400_kV_New:{v}"
    patt_vu = f"400_kV_New:{u}"
    for ch in reader:
        ch = ch[ch['carriers']=='electricity']
        if ch.empty: continue
        m_uv = (ch['locs']==u) & (ch['techs']==patt_uv)
        m_vu = (ch['locs']==v) & (ch['techs']==patt_vu)
        if m_uv.any(): tot += float(ch.loc[m_uv,'carrier_prod'].sum())
        if m_vu.any(): tot += float(ch.loc[m_vu,'carrier_prod'].sum())
    return tot

# ===== Prepara tabelle per scenario (prima di aprire l'ExcelWriter) =====
scenario_tables: dict[str, pd.DataFrame] = {}

for scenario in scenario_names:
    records = []
    # per anno: costruisci edges
    per_year_edges = {}
    for year in years:
        key_energy = f"{GROUP_TX}_{year}_{scenario}"
        df_energy_cap = energy_cap_data.get(key_energy)
        if df_energy_cap is None or df_energy_cap.empty:
            per_year_edges[year] = pd.DataFrame(columns=['u','v','cap_edge_kw','cost_line_M$'])
            print(f"[WARN][TX] energy_cap mancante per {key_energy}")
        else:
            per_year_edges[year] = edges_from_energy_cap(df_energy_cap)

    # set di tutte le coppie presenti in almeno un anno (ordinate)
    pairs = set()
    for edf in per_year_edges.values():
        for _, r in edf.iterrows():
            pairs.add( (str(r['u']), str(r['v'])) )
    pairs = sorted(list(pairs), key=lambda t: (t[0], t[1]))

    # costruisci righe: per coppia 3 parametri
    for (u, v) in pairs:
        row_inv   = {"Country 1": u, "Country 2": v, "Parameter": "Investment"}
        row_omfix = {"Country 1": u, "Country 2": v, "Parameter": "Fixed_O&M"}
        row_energy= {"Country 1": u, "Country 2": v, "Parameter": "Energy"}

        for year in years:
            edf = per_year_edges[year]
            r = edf[(edf['u']==u) & (edf['v']==v)]

            # Investment (M$) — split 50/50
            inv_M = float(r['cost_line_M$'].iloc[0]) / 2.0 if not r.empty else 0.0
            row_inv[year] = inv_M

            # Energy (GWh) e Fixed_O&M (M$/yr) da results_carrier_prod
            csv_prod = results_path / GROUP_TX / year / f"Results_{GROUP_TX}_{scenario}" / "results_carrier_prod.csv"
            if csv_prod.exists():
                kwh = kwh_out_on_edge(csv_prod, u, v)  # kWh tot
            else:
                print(f"[MISS][TX] {csv_prod} → Energy/O&M=0 per {u}:{v} {year}")
                kwh = 0.0
            gwh = kwh / 1e6
            row_energy[year] = gwh
            row_omfix[year]  = (kwh * OPEX_PER_KWH) / 1e6 / 2.0  # USD→M$ e split 50/50

        records.extend([row_inv, row_omfix, row_energy])

    scenario_tables[scenario] = pd.DataFrame(records, columns=["Country 1","Country 2","Parameter"] + years)

# ===== Scrivi Excel: 1 foglio per scenario =====
out_xlsx = output_dir / "Transmission_Costs_Transmission_Expansion.xlsx"
with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
    for scenario, df_out in scenario_tables.items():
        sheet_name = scenario[:31]
        df_out.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"[OK] Exported pair table: {out_xlsx}")
#===================================================================================================================================================
#===================================================================================================================================================
# %%  ==================================================================================
# SEZIONE — PRODUZIONE ELETTRICA PER FONTE (PV/Wind/CSP/Hydro/PHES/Gas/Coal/Oil/Bio/Geo/Nuclear/Other)
# ======================================================================================
from pathlib import Path
import pandas as pd
import numpy as np
import re
from pandas import ExcelWriter
from collections import defaultdict

# Richiede: results_path, group_names, years, scenario_names, country_code, output_dir
# già definiti in alto nel tuo script.
output_dir = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\Results")
output_dir.mkdir(parents=True, exist_ok=True)

# ---------- UTIL: normalizzazione nome tecnologia ----------
def normalize_tech(tech: str) -> str:
    """
    Normalizza il nome tecnologia per match 'contains':
    - minuscole
    - rimuove parte dopo ':' (peer di trasmissione, es. '400_kV_New:ZMB')
    - rimuove suffissi comuni: _new/_existing, _pp, _msr\d+
    - compatta spazi e caratteri non alfabetici in '_'
    """
    t = str(tech).strip().lower()
    t = t.split(':', 1)[0]                           # es. 400_kV_New:ZMB -> 400_kV_New
    t = re.sub(r'\b(new|existing)\b', '', t)         # _new/_existing
    t = re.sub(r'_pp\b', '', t)                      # _pp
    t = re.sub(r'_msr\d+\b', '', t)                  # _MSR#
    t = re.sub(r'\s+', '_', t)                       # spazi -> _
    t = re.sub(r'[^a-z0-9]+', '_', t)                # non alfanumerici -> _
    t = re.sub(r'_+', '_', t).strip('_')             # compatta/rifila
    return t

# ---------- MAPPATURA TECNOLOGIA → FONTE (contains; ordine intenzionale) ----------
def tech_to_source_label(tech: str) -> str:
    """
    Converte il nome tech Calliope in fonte aggregata.
    Copre varianti viste nei tuoi YAML (PV/CPV, Wind, CSP, Hydro_Large/Small/ROR,
    BESS, PHES, CCGT/OCGT/Gas_Engine/NG/LNG, Coal_pp, Diesel/HFO/Oil, Bioenergy/Biogas/Biomass/Bagasse, Nuclear).
    Esclude Transmission e Demand.
    """
    if tech is None or (isinstance(tech, float) and np.isnan(tech)):
        return "Other"

    raw = str(tech)
    t = normalize_tech(raw)

    # ---- Esclusioni robuste ----
    if '400_kv' in t or 'transmission' in t:
        return "EXCLUDE"       # niente linee
    if 'demand' in t:
        return "EXCLUDE"       # niente domanda

    # ---- Storage prima (prende anche eventuali naming 'charging') ----
    if 'bess' in t:
        return "BESS"
    if 'phes' in t or 'pumped' in t:
        return "PHES"

    # ---- CSP prima di PV (evita che 'solar csp' cada in PV) ----
    if 'csp' in t or 'solarthermal' in t or 'solar_thermal' in t:
        return "CSP"

    # ---- PV (copre PV*, CPV*, Solar PV...) ----
    if t.startswith('pv') or 'cpv' in t or ('solar' in t and 'csp' not in t):
        return "PV"

    # ---- Wind (copre Wind*, W*, ecc.) ----
    if t == 'w' or t.startswith('w_') or 'wind' in t:
        return "Wind"

    # ---- Bioenergy prima di Gas (per evitare che 'biogas' finisca in Gas) ----
    if 'biomass' in t or 'biogas' in t or 'bioenergy' in t or 'bagasse' in t:
        return "Bioenergy"

    # ---- Hydro (Large/Small/ROR) ----
    if 'hydro' in t or 'run_of_river' in t or '_ror' in t or t.endswith('_ror'):
        return "Hydro"

    # ---- Gas (CCGT/OCGT/NG/LNG/Gas_Engine) ----
    if 'ocgt' in t or 'ccgt' in t or '_gt' in t or 'gas_engine' in t or re.search(r'\bgas\b', t) or 'ng' in t or 'lng' in t:
        return "Gas"

    # ---- Coal / Lignite ----
    if 'coal' in t or 'lignite' in t:
        return "Coal"

    # ---- Oil / Diesel / HFO ----
    if 'diesel' in t or 'hfo' in t or re.search(r'\boil\b', t):
        return "Oil"

    # ---- Geothermal ----
    if 'geothermal' in t or t.startswith('geo_') or t == 'geo':
        return "Geothermal"

    # ---- Nuclear ----
    if 'nuclear' in t:
        return "Nuclear"

    # Fallback (dovrebbe rimanere vuoto coi tuoi file, ma lo lasciamo per sicurezza)
    return "Other"

# ---------- ACCUMULO PER FILE CSV (chunked) ----------
def accumulate_prod_by_source(csv_path: Path,
                              country_code: list[str],
                              chunksize: int = 1_000_000) -> dict[tuple[str, str], float]:
    """
    Legge results_carrier_prod.csv in chunk e accumula la produzione annua per (location, fonte) in GWh.
    Include tutte le tecnologie che producono electricity (nuove+esistenti), esclude Transmission e Demand.
    Ritorna {(loc, source): GWh}.
    """
    acc_kwh = defaultdict(float)

    usecols = ['carriers', 'locs', 'techs', 'timesteps', 'carrier_prod']  # kWh
    dtypes  = {
        'carriers': 'category',
        'locs': 'string',
        'techs': 'string',
        'timesteps': 'string',
        'carrier_prod': 'float64',
    }

    try:
        reader = pd.read_csv(csv_path, usecols=usecols, dtype=dtypes,
                             engine='pyarrow', chunksize=chunksize)
    except Exception:
        reader = pd.read_csv(csv_path, usecols=usecols, dtype=dtypes,
                             chunksize=chunksize)

    for chunk in reader:
        # solo elettricità
        chunk = chunk[chunk['carriers'] == 'electricity']
        if chunk.empty:
            continue

        # mappa tech → source ed escludi EXCLUDE
        sources = chunk['techs'].map(tech_to_source_label)
        mask = sources != "EXCLUDE"
        chunk = chunk[mask].copy()
        sources = sources[mask]
        if chunk.empty:
            continue
        chunk['_source'] = sources.astype('string')

        # somma kWh per (loc, source)
        g = (chunk
             .groupby(['locs', '_source'], observed=True)['carrier_prod']
             .sum())
        for (loc, src), val in g.items():
            acc_kwh[(str(loc), str(src))] += float(val)

    # Aggiungi aggregati MOZ e SAPP
    all_sources = {src for (_, src) in acc_kwh.keys()}
    for src in all_sources:
        moz = acc_kwh.get(('MOZ_NC', src), 0.0) + acc_kwh.get(('MOZ_S', src), 0.0)
        sapp = sum(acc_kwh.get((ct, src), 0.0) for ct in country_code)
        acc_kwh[('MOZ', src)] = moz
        acc_kwh[('SAPP', src)] = sapp

    # kWh → GWh
    return {(ct, src): val / 1e6 for (ct, src), val in acc_kwh.items()}

# ---------- COSTRUZIONE TABELLONE E EXPORT ----------
SOURCE_ORDER = [
    "PV", "CSP", "Wind", "Hydro", "PHES",
    "Gas", "Coal", "Oil", "Bioenergy", "Geothermal", "Nuclear", "Other"
]
all_locations_for_export = country_code + ['MOZ', 'SAPP']

rows = []
missing_any = False

for group in group_names:
    for year in years:
        for scenario in scenario_names:
            csv_path = results_path / group / year / f"Results_{group}_{scenario}" / "results_carrier_prod.csv"
            if not csv_path.exists():
                print(f"[MISS] {csv_path}")
                missing_any = True
                # righe zero per struttura coerente
                for loc in all_locations_for_export:
                    for src in SOURCE_ORDER:
                        rows.append({
                            "group": group, "year": year, "scenario": scenario,
                            "location": loc, "source": src, "Prod_GWh": 0.0
                        })
                continue

            acc = accumulate_prod_by_source(csv_path, country_code, chunksize=1_000_000)

            for loc in all_locations_for_export:
                for src in SOURCE_ORDER:
                    gwh = acc.get((loc, src), 0.0)
                    rows.append({
                        "group": group, "year": year, "scenario": scenario,
                        "location": loc, "source": src, "Prod_GWh": float(gwh)
                    })

prod_by_source_df = pd.DataFrame(rows)

# sanity check
expected = {"group", "year", "scenario", "location", "source", "Prod_GWh"}
missing_cols = expected - set(prod_by_source_df.columns)
assert not missing_cols, f"Mancano colonne in prod_by_source_df: {missing_cols}"

# --- EXPORT: un file per group, uno sheet per scenario; righe=(location, source), colonne=year ---
out_dir_sources = output_dir
out_dir_sources.mkdir(parents=True, exist_ok=True)

for group in group_names:
    out_xlsx = out_dir_sources / f"Electricity_Production_BySource_GWh_{group}.xlsx"
    with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        for scenario in scenario_names:
            sub = prod_by_source_df[(prod_by_source_df["group"] == group) &
                                    (prod_by_source_df["scenario"] == scenario)]
            if sub.empty:
                pd.DataFrame(columns=years).to_excel(writer, sheet_name=scenario[:31])
                continue

            pivot = (sub.pivot_table(index=["location", "source"],
                                     columns="year",
                                     values="Prod_GWh",
                                     aggfunc="sum",
                                     fill_value=0.0)
                         .reindex(columns=years))

            # ordine location: alfabetico + SAPP in coda
            locs = sorted(sub["location"].unique().tolist())
            if "SAPP" in locs:
                locs.remove("SAPP")
            loc_order = locs + ["SAPP"]

            tmp = pivot.reset_index()
            tmp["location"] = pd.Categorical(tmp["location"], categories=loc_order, ordered=True)
            tmp["source"]   = pd.Categorical(tmp["source"],   categories=SOURCE_ORDER, ordered=True)
            pivot_sorted = tmp.sort_values(["location", "source"]).set_index(["location", "source"])

            sheet_name = scenario[:31]
            pivot_sorted.to_excel(writer, sheet_name=sheet_name)

    print(f"[OK] Exported production by source: {out_xlsx}")

if missing_any:
    print("\n[WARN] Alcuni results_carrier_prod.csv non trovati. Verifica paths/scenari.")
# ======================================================================================
# ======================================================================================
# END