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
input_path = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\Results")
output_path = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\LCOE")

assert input_path.exists(), f"Results Path Not Found: {input_path}"

country_code = ['AGO','BWA','DRC','LSO','MOZ_NC','MOZ_S','MWI','NAM','SWZ','TZA','ZAF','ZMB','ZWE', 'MOZ', 'SAPP']
techs = ['PV_New','W_New', 'Hydro_New', 'OCGT_New', 'BESS_New', 'PHES_New', 'Transmission_New']

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
#%%
# DIESEL COSTS CALCULATION (based on unmet demand values) - Parameters same as Input in Calliope Model

def load_unmet_long_for_group(group: str, input_dir: Path) -> pd.DataFrame:
    xlsx_path = input_dir / f"Unmet_Demand_GWh_{group}.xlsx"
    if not xlsx_path.exists():
        raise FileNotFoundError(f"Unmet file not found: {xlsx_path}")

    sheets = pd.read_excel(xlsx_path, sheet_name=None, engine="openpyxl")
    out = []
    for scenario, df_wide in sheets.items():
        if df_wide is None or df_wide.empty:
            continue

        # Assicura intestazioni attese
        if not {"location", "metric"}.issubset(set(df_wide.columns)):
            df_wide = df_wide.copy()
            df_wide.rename(columns={df_wide.columns[0]: "location",
                                    df_wide.columns[1]: "metric"}, inplace=True)

        df_wide = df_wide.copy()

        # >>> FIX 1: forward-fill della location per gestire celle merge/blank
        df_wide["location"] = df_wide["location"].astype("string")
        df_wide["location"] = df_wide["location"].where(df_wide["location"].notna(), None)
        df_wide["location"] = df_wide["location"].ffill()

        # Normalizza metric per sicurezza (spazi, ecc.)
        df_wide["metric"] = df_wide["metric"].astype(str).str.strip()

        # >>> FIX 2: se esistono due righe 'Peak_Unmet' per la stessa location,
        #            tutte le occorrenze dalla 2ª in poi diventano 'Total_Unmet'
        df_wide["metric_occ"] = df_wide.groupby(["location", "metric"]).cumcount() + 1
        if not (df_wide["metric"] == "Total_Unmet").any():
            mask_second_peak = (df_wide["metric"] == "Peak_Unmet") & (df_wide["metric_occ"] >= 2)
            df_wide.loc[mask_second_peak, "metric"] = "Total_Unmet"
        df_wide.drop(columns=["metric_occ"], inplace=True)

        # Melt anni → long
        years_in_sheet = [c for c in df_wide.columns if str(c) in years]
        long = (df_wide[["location", "metric"] + years_in_sheet]
                  .melt(id_vars=["location", "metric"],
                        var_name="year", value_name="value_GWh"))
        long["group"] = group
        long["scenario"] = scenario
        out.append(long)

    return (pd.concat(out, ignore_index=True)
            if out else pd.DataFrame(columns=["group","scenario","year","location","metric","value_GWh"]))

CAPEX_Diesel = 708.0    # $/kW
F_OPEX_Diesel = 24.0    # $/kW/year
V_OPEX_Diesel = 0.003   # $/kWh
Fuel_Diesel   = 0.0493  # $/kWh
Eta_Diesel    = 0.35    # -
LT_Diesel  = 30         # years
# assicura esistenza cartella output
output_path.mkdir(parents=True, exist_ok=True)

# Carica e unisce tutti i group (ogni file sta sotto la cartella del group)
unmet_long_list = []
for g in group_names:
    input_files_path = input_path / g  # <— come richiesto
    unmet_long_list.append(load_unmet_long_for_group(g, input_files_path))
unmet_long = pd.concat(unmet_long_list, ignore_index=True)

# Pivot → colonne metriche
unmet_pvt = (unmet_long
             .pivot_table(index=["group","scenario","year","location"],
                          columns="metric", values="value_GWh",
                          aggfunc="sum", fill_value=0.0)
             .reset_index())

# Rinomina/garantisce colonne attese
if "Peak_Unmet" not in unmet_pvt.columns:
    unmet_pvt["Peak_Unmet"] = 0.0
if "Total_Unmet" not in unmet_pvt.columns:
    unmet_pvt["Total_Unmet"] = 0.0
unmet_pvt = unmet_pvt.rename(columns={
    "Peak_Unmet": "Peak_Unmet_GWh",
    "Total_Unmet": "Total_Unmet_GWh"
})

print(unmet_pvt.query("scenario=='VRES_no_Storage' and location=='AGO'")[["year","Peak_Unmet_GWh","Total_Unmet_GWh"]].head())

# Calcoli Diesel (M$)
diesel_df = unmet_pvt.copy()
diesel_df["Investment_M$"] = diesel_df["Peak_Unmet_GWh"]  * CAPEX_Diesel
diesel_df["Fixed_M$yr"]    = diesel_df["Peak_Unmet_GWh"]  * F_OPEX_Diesel
diesel_df["Variable_M$"]   = diesel_df["Total_Unmet_GWh"] * V_OPEX_Diesel
diesel_df["Fuel_M$"]       = diesel_df["Total_Unmet_GWh"] * (Fuel_Diesel / Eta_Diesel)

diesel_df = (diesel_df[[
    "group","scenario","year","location",
    "Peak_Unmet_GWh","Total_Unmet_GWh",
    "Investment_M$","Fixed_M$yr","Variable_M$","Fuel_M$"
]].sort_values(["group","scenario","year","location"]).reset_index(drop=True))

print("[OK] Diesel params computed in memory. Rows:", len(diesel_df))

# #%%
# # === Diesel TEST export: only scenario "VRES_no_Storage" ===
# test_scenario = "VRES+Hydro+NG_BESS+PHES"

# for group in group_names:
#     sub = diesel_df[(diesel_df["group"] == group) & (diesel_df["scenario"] == test_scenario)]
#     if sub.empty:
#         print(f"[WARN] Nessun dato per {group} - {test_scenario}")
#         continue

#     out_xlsx = output_path / f"Diesel_Test_{group}_{test_scenario}.xlsx"
#     with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
#         for col in ["Peak_Unmet_GWh","Total_Unmet_GWh","Investment_M$","Fixed_M$yr","Variable_M$","Fuel_M$"]:
#             pivot = (sub.pivot_table(index="location", columns="year", values=col,
#                                      aggfunc="sum", fill_value=0.0)
#                          .reindex(columns=years))
#             pivot.to_excel(writer, sheet_name=col[:31])

#     print(f"[OK] Salvato test Diesel: {out_xlsx}")
#===================================================================================================================================
#===================================================================================================================================
# %%
# LOAD ALL INPUTS FOR LCOE CALCULATION

# --- helper comuni ---
def _read_group_file(input_dir: Path, group: str, filename: str) -> dict[str, pd.DataFrame]:
    """Legge xlsx in input_dir/<group>/<filename> e ritorna dict {sheet_name: df}."""
    path = input_dir / group / filename
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")
    return pd.read_excel(path, sheet_name=None, engine="openpyxl")

def _ffill_location(df: pd.DataFrame, loc_col="location") -> pd.DataFrame:
    """Forward-fill di 'location' per gestire celle merge/vuote; se manca, assume prima colonna."""
    df = df.copy()
    if loc_col not in df.columns:
        df.rename(columns={df.columns[0]: loc_col}, inplace=True)
    df[loc_col] = df[loc_col].astype("string")
    df[loc_col] = df[loc_col].where(df[loc_col].notna(), None).ffill()
    return df

def _melt_years(df: pd.DataFrame, id_vars: list[str], years: list[str], value_name: str) -> pd.DataFrame:
    year_cols = [c for c in df.columns if str(c) in years]
    if not year_cols:
        # meglio fallire esplicitamente se non trova colonne anno attese
        raise ValueError(f"Nessuna colonna anno tra {years} trovata nelle colonne: {list(df.columns)}")
    return df[id_vars + year_cols].melt(id_vars=id_vars, var_name="year", value_name=value_name)

def _norm_line_key(s: str) -> str:
    """Normalizza 'AGO-DRC'/'DRC:AGO' ecc. → 'AGO:DRC' (nodi in ordine alfabetico)."""
    s = str(s).strip()
    # uniforma vari separatori a ':'
    for dash in ["–","—","-","/","\\"]:
        s = s.replace(dash, ":")
    s = re.sub(r"\s*", "", s)  # rimuovi spazi
    if ":" not in s:
        return s
    a, b = s.split(":", 1)
    a, b = a.strip(), b.strip()
    a, b = sorted([a, b])
    return f"{a}:{b}"

def _load_tx_costs_energy(input_dir: Path, group: str, filename: str, years: list[str]) -> pd.DataFrame:
    """
    Legge Transmission_Costs_Transmission_Expansion.xlsx (uno sheet per scenario) con colonne:
      - 'Country 1', 'Country 2', 'Parameter', e gli anni (2030, 2035, 2040)
    Restituisce: group, scenario, year, location_norm (A:B), inv_M$, fom_M$/yr, energy_GWh
    """
    sheets = _read_group_file(input_dir, group, filename)
    out = []
    for scenario, df in sheets.items():
        if df is None or df.empty:
            continue

        df = df.copy()

        # colonne attese nel file reale
        cols = [c.strip() for c in df.columns]
        df.columns = cols

        # rinomina robusta
        col_c1 = next((c for c in df.columns if c.lower().replace(" ", "") in ("country1","node1","from","country_1")), None)
        col_c2 = next((c for c in df.columns if c.lower().replace(" ", "") in ("country2","node2","to","country_2")), None)
        col_par = next((c for c in df.columns if c.strip().lower() in ("parameter","metric","measure")), None)

        if col_c1 is None or col_c2 is None or col_par is None:
            raise ValueError(
                f"Colonne attese non trovate in {filename} / sheet '{scenario}'. "
                f"Trovate: {list(df.columns)} — servono 'Country 1','Country 2','Parameter'."
            )

        # costruiamo 'location' = A:B (normalizzata)
        df = df.rename(columns={col_c1: "country1", col_c2: "country2", col_par: "parameter"})
        df["location"] = (df["country1"].astype(str).str.strip() + ":" + df["country2"].astype(str).str.strip())
        df["location_norm"] = df["location"].apply(_norm_line_key)

        # melt anni → long
        year_cols = [c for c in df.columns if str(c) in years]
        if not year_cols:
            raise ValueError(f"Nessuna colonna anno {years} trovata in {filename} / sheet '{scenario}'.")
        long = df[["location_norm", "parameter"] + year_cols].melt(
            id_vars=["location_norm","parameter"], var_name="year", value_name="value"
        )
        long["group"] = group
        long["scenario"] = scenario

        # mappa parameter → metrica standard
        def _metric_std(m: str) -> str | None:
            m0 = str(m).strip().lower().replace(" ", "").replace("-", "").replace("_", "")
            if "energy" in m0:
                return "energy_GWh"
            if "fixedo&m" in m0 or "fixedom" in m0 or ("fixed" in m0 and ("om" in m0 or "o&m" in m0)):
                return "fom_M$/yr"
            if "invest" in m0 or "capex" in m0:
                return "inv_M$"
            # ignora altro (es. annualized invest per il metodo classico)
            return None

        long["metric_std"] = long["parameter"].map(_metric_std)
        long = long[long["metric_std"].notna()].copy()

        out.append(long)

    if not out:
        return pd.DataFrame(columns=["group","scenario","year","location_norm","inv_M$","fom_M$/yr","energy_GWh"])

    full = pd.concat(out, ignore_index=True)

    # pivot metriche → colonne
    pvt = (full.pivot_table(index=["group","scenario","year","location_norm"],
                            columns="metric_std", values="value",
                            aggfunc="sum", fill_value=0.0)
                .reset_index())

    # garantisci colonne
    for col in ["inv_M$","fom_M$/yr","energy_GWh"]:
        if col not in pvt.columns:
            pvt[col] = 0.0

    return pvt
# --- loader generici per tabelle per-tech e unmet ---
def _load_per_tech(input_dir: Path, group: str, filename: str, years: list[str], value_name: str) -> pd.DataFrame:
    """Carica tabelle con colonne: location, tech, <years...> (uno sheet per scenario)."""
    sheets = _read_group_file(input_dir, group, filename)
    out = []
    for scenario, df in sheets.items():
        if df is None or df.empty:
            continue
        df = _ffill_location(df, "location")
        # normalizza nome colonna tech se diverso
        if "tech" not in df.columns:
            cand = [c for c in df.columns if c.lower() in ("tech","technology")]
            if cand:
                df = df.rename(columns={cand[0]: "tech"})
            else:
                raise ValueError(f"Colonna 'tech' assente in {filename} / sheet '{scenario}'")
        # keep solo le righe con le tech richieste
        df = df[df["tech"].isin(techs)].copy()
        long = _melt_years(df, ["location","tech"], years, value_name)
        long["group"] = group
        long["scenario"] = scenario
        out.append(long)
    if not out:
        return pd.DataFrame(columns=["group","scenario","year","location","tech", value_name])
    return pd.concat(out, ignore_index=True)

def _load_unmet(input_dir: Path, group: str, filename: str, years: list[str]) -> pd.DataFrame:
    """Carica unmet con colonne: location, metric, <years...> (uno sheet per scenario)."""
    sheets = _read_group_file(input_dir, group, filename)
    out = []
    for scenario, df in sheets.items():
        if df is None or df.empty:
            continue
        df = _ffill_location(df, "location")
        if "metric" not in df.columns:
            # assume la seconda colonna sia 'metric' se i header sono strani
            df = df.rename(columns={df.columns[1]: "metric"})
        df["metric"] = df["metric"].astype(str).str.strip()
        long = _melt_years(df, ["location","metric"], years, "value")
        long["group"] = group
        long["scenario"] = scenario
        out.append(long)
    if not out:
        return pd.DataFrame(columns=["group","scenario","year","location","metric","value"])
    return pd.concat(out, ignore_index=True)

# --- funzione principale: carica TUTTO per tutti i group ---
def load_all_inputs_for_lcoe(input_path: Path, group_names: list[str], years: list[str]):
    FILENAMES = {
        "annualized_invest": "Annualized_Investments_{g}.xlsx",     # M$/yr attesi
        "invest":            "Investments_{g}.xlsx",                 # M$    attesi
        "fixed_opex":        "O&M_Fixed_Yearly_Costs_{g}.xlsx",      # M$/yr attesi
        "variable_opex":     "O&M_Variable_Costs_{g}.xlsx",          # M$    attesi (per anno)
        "production":        "Electricity_Production_GWh_{g}.xlsx",  # GWh   attesi
        "unmet":             "Unmet_Demand_GWh_{g}.xlsx"             # GWh   attesi
    }

    frames = {k: [] for k in FILENAMES}

    for g in group_names:
        frames["annualized_invest"].append(
            _load_per_tech(input_path, g, FILENAMES["annualized_invest"].format(g=g), years, "annualized_invest_M$/yr")
        )
        frames["invest"].append(
            _load_per_tech(input_path, g, FILENAMES["invest"].format(g=g), years, "invest_M$")
        )
        frames["fixed_opex"].append(
            _load_per_tech(input_path, g, FILENAMES["fixed_opex"].format(g=g), years, "fixed_opex_M$/yr")
        )
        frames["variable_opex"].append(
            _load_per_tech(input_path, g, FILENAMES["variable_opex"].format(g=g), years, "var_opex_M$")
        )
        frames["production"].append(
            _load_per_tech(input_path, g, FILENAMES["production"].format(g=g), years, "prod_GWh")
        )
        frames["unmet"].append(
            _load_unmet(input_path, g, FILENAMES["unmet"].format(g=g), years)
        )

    # concat e typing base
    out = {}
    for k, parts in frames.items():
        out[k] = (pd.concat(parts, ignore_index=True) if parts else pd.DataFrame())
        if not out[k].empty:
            out[k]["year"] = out[k]["year"].astype(str)
            out[k]["group"] = out[k]["group"].astype("category")
            out[k]["scenario"] = out[k]["scenario"].astype("category")

    # typing ulteriori
    for k in ["annualized_invest","invest","fixed_opex","variable_opex","production"]:
        if not out[k].empty:
            out[k]["tech"] = out[k]["tech"].astype("category")

    if not out["unmet"].empty:
        out["unmet"]["metric"] = out["unmet"]["metric"].astype("category")

    return out

def _load_transmission_costs(input_dir: Path, group: str, filename: str, years: list[str]) -> pd.DataFrame:
    """
    Carica Transmission_Costs_Transmission_Expansion.xlsx da input_dir/<group>/...
    Se la colonna 'tech' manca, la imposta a 'Transmission_New'.
    Ritorna long: group, scenario, year, location, tech, transmission_costs_M$.
    """
    sheets = _read_group_file(input_dir, group, filename)
    out = []
    for scenario, df in sheets.items():
        if df is None or df.empty:
            continue
        df = _ffill_location(df, "location")

        # tech: se non esiste, crea colonna costante 'Transmission_New'
        if "tech" not in df.columns and "Technology" not in [c.capitalize() for c in df.columns]:
            df = df.copy()
            df["tech"] = "Transmission_New"
            print(f"[INFO] '{filename}' / '{scenario}': colonna 'tech' assente — imposto 'Transmission_New'.")
        else:
            # normalizza eventuale 'technology'
            if "tech" not in df.columns:
                cand = [c for c in df.columns if c.lower() in ("tech","technology")]
                df = df.rename(columns={cand[0]: "tech"})
            # filtra Transmission_New se nel file ci sono più righe
            df = df[df["tech"].astype(str) == "Transmission_New"].copy()

        long = _melt_years(df, ["location","tech"], years, "transmission_costs_M$")
        long["group"] = group
        long["scenario"] = scenario
        out.append(long)

    if not out:
        return pd.DataFrame(columns=["group","scenario","year","location","tech","transmission_costs_M$"])
    return pd.concat(out, ignore_index=True)

# Integra nel loader principale: AGGIUNGI una chiave 'transmission_costs'
def load_all_inputs_for_lcoe_with_tx(input_path: Path, group_names: list[str], years: list[str]):
    base = load_all_inputs_for_lcoe(input_path, group_names, years)

    # === transmission_costs (com'era prima) — opzionale se ti serve ancora
    tx_frames = []
    for g in group_names:
        if g != "Transmission_Expansion":
            continue
        tx_frames.append(
            _load_transmission_costs(
                input_path, g,
                "Transmission_Costs_Transmission_Expansion.xlsx",
                years
            )
        )
    base["transmission_costs"] = (
        pd.concat(tx_frames, ignore_index=True) if tx_frames else
        pd.DataFrame(columns=["group","scenario","year","location","tech","transmission_costs_M$"])
    )
    if not base["transmission_costs"].empty:
        base["transmission_costs"]["year"] = base["transmission_costs"]["year"].astype(str)
        base["transmission_costs"]["group"] = base["transmission_costs"]["group"].astype("category")
        base["transmission_costs"]["scenario"] = base["transmission_costs"]["scenario"].astype("category")
        base["transmission_costs"]["tech"] = base["transmission_costs"]["tech"].astype("category")

    # === NUOVO: tx_costs_energy (INV/FOM/Energy per linea dal file 'Transmission_Costs_Transmission_Expansion.xlsx')
    tx_ce_frames = []
    for g in group_names:
        if g != "Transmission_Expansion":
            continue
        tx_ce_frames.append(
            _load_tx_costs_energy(
                input_path, g,
                "Transmission_Costs_Transmission_Expansion.xlsx",
                years
            )
        )
    base["tx_costs_energy"] = (
        pd.concat(tx_ce_frames, ignore_index=True) if tx_ce_frames else
        pd.DataFrame(columns=["group","scenario","year","location_norm","inv_M$","fom_M$/yr","energy_GWh"])
    )
    if not base["tx_costs_energy"].empty:
        base["tx_costs_energy"]["year"] = base["tx_costs_energy"]["year"].astype(str)
        base["tx_costs_energy"]["group"] = base["tx_costs_energy"]["group"].astype("category")
        base["tx_costs_energy"]["scenario"] = base["tx_costs_energy"]["scenario"].astype("category")

    return base

def pvaf(r: float, N: int) -> float:
    r = float(r)
    return (1 - (1 + r) ** (-N)) / r

#===================================================================================================================================
#===================================================================================================================================
datasets = load_all_inputs_for_lcoe_with_tx(input_path, group_names, years)
techs = ['PV_New','W_New', 'Hydro_New', 'OCGT_New', 'BESS_New', 'PHES_New', 'Transmission_New']
discount_rate = 0.1
lifetime_years = {'PV_New': 25,'W_New': 25,'BESS_New': 15,'PHES_New': 40,'Hydro_New': 50,'OCGT_New': 30, 'Transmission_New': 40}

print("[OK] Inputs loaded for LCOE:")
for name, df in datasets.items():
    print(f"  - {name}: {len(df):,} righe")

#===================================================================================================================================
#===================================================================================================================================
# # %% LCOE for every TRANSMISSION LINE — Transmission_Expansion ONLY

# line_pairs_list = ['AGO:DRC','AGO:NAM','AGO:ZMB','BWA:NAM','BWA:ZAF','BWA:ZMB','BWA:ZWE','DRC:TZA','DRC:ZMB','LSO:ZAF','MOZ_NC:MOZ_S',
#                    'MOZ_NC:MWI','MOZ_NC:TZA','MOZ_NC:ZMB','MOZ_NC:ZWE','MOZ_S:SWZ','MOZ_S:ZAF','MOZ_S:ZWE','MWI:TZA','MWI:ZMB',
#                    'NAM:ZMB','NAM:ZWE','NAM:ZAF','SWZ:ZAF','TZA:ZMB','ZAF:ZWE','ZMB:ZWE']

# # normalizza chiavi linea per confronto
# line_pairs_norm_list = [_norm_line_key(k) for k in line_pairs_list]
# line_keys = set(line_pairs_norm_list)

# TX_GROUP = "Transmission_Expansion"
# TX_N     = lifetime_years["Transmission_New"]  # 40
# TX_PVAF  = pvaf(discount_rate, TX_N)

# tx_ce = datasets["tx_costs_energy"].copy()
# if tx_ce.empty:
#     print("[INFO] tx_costs_energy è vuoto: verifica il parsing del file Transmission_Costs_Transmission_Expansion.xlsx (metriche/anni).")

# rows_tx = []

# # scenari presenti
# sc_in_g = sorted(
#     tx_ce["scenario"].astype(str).unique(),
#     key=lambda s: scenario_names.index(s) if s in scenario_names else 999
# )

# for sc in sc_in_g:
#     for yr in years:
#         sub = tx_ce[
#             (tx_ce["group"] == TX_GROUP) &
#             (tx_ce["scenario"].astype(str) == sc) &
#             (tx_ce["year"].astype(str) == yr)
#         ].copy()

#         if sub.empty:
#             continue

#         # tieni solo le linee presenti nella lista (normalizzate)
#         sub = sub[sub["location_norm"].isin(line_keys)].copy()
#         if sub.empty:
#             continue

#         for loc in sorted(sub["location_norm"].unique()):
#             inv_val = float(sub.loc[sub["location_norm"] == loc, "inv_M$"].sum())
#             fom_val = float(sub.loc[sub["location_norm"] == loc, "fom_M$/yr"].sum())
#             e_val   = float(sub.loc[sub["location_norm"] == loc, "energy_GWh"].sum())

#             if e_val <= 0:
#                 lcoe = np.nan
#             else:
#                 pv_costs  = inv_val + fom_val * TX_PVAF         # M$
#                 pv_energy = (e_val / 2.0) * TX_PVAF             # GWh
#                 lcoe      = (pv_costs / pv_energy) * 1000.0     # $/MWh

#             rows_tx.append({
#                 "group": TX_GROUP, "scenario": sc, "year": yr,
#                 "location": loc, "tech": "Transmission_New",
#                 "LCOE_$_per_MWh": lcoe
#             })

# lcoe_tx_df = pd.DataFrame(rows_tx)

# # EXPORT: dedicated file
# if not lcoe_tx_df.empty:
#     out_xlsx = output_path / f"LCOE_TransmissionLines_{TX_GROUP}.xlsx"
#     with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
#         for sc in sc_in_g:
#             sub = lcoe_tx_df[lcoe_tx_df["scenario"] == sc][["location","tech","year","LCOE_$_per_MWh"]].copy()
#             if sub.empty:
#                 pd.DataFrame(columns=["location","tech"] + years).to_excel(writer, sheet_name=sc[:31], index=False)
#                 continue
#             pivot = (sub.pivot_table(index=["location","tech"], columns="year", values="LCOE_$_per_MWh",
#                                      aggfunc="mean").reindex(columns=years))
#             # ordina secondo la lista
#             ordered_index = []
#             for key in line_pairs_norm_list:
#                 ordered_index += [idx for idx in pivot.index if isinstance(idx, tuple) and idx[0] == key]
#             residual = [i for i in pivot.index if i not in ordered_index]
#             pivot = pivot.loc[ordered_index + residual]
#             pivot.to_excel(writer, sheet_name=sc[:31])
#     print(f"[OK] Salvato Transmission lines LCOE: {out_xlsx}")
# else:
#     print("[INFO] Nessun dato per Transmission lines LCOE (tx_costs_energy vuoto o linee non trovate).")

#===================================================================================================================================
#===================================================================================================================================
# # %% === LCOE Transmission a livello di PAESE (allocazione 50/50 per ciascun paese) ===

# TX_GROUP = "Transmission_Expansion"
# TX_N     = lifetime_years["Transmission_New"]  # 40
# TX_PVAF  = pvaf(discount_rate, TX_N)

# tx_ce = datasets["tx_costs_energy"].copy()

# if tx_ce.empty:
#     print("[INFO] tx_costs_energy vuoto: niente LCOE di trasmissione per paese.")
# else:
#     # prendi solo il group Transmission_Expansion e normalizza i nomi
#     tx_ce = tx_ce[tx_ce["group"] == TX_GROUP].copy()
#     tx_ce["scenario"] = tx_ce["scenario"].astype(str)
#     tx_ce["year"]     = tx_ce["year"].astype(str)

#     # helper: controlla se il paese è presente nella chiave 'A:B'
#     def _line_has_country(line_key: str, country: str) -> bool:
#         a, b = str(line_key).split(":")
#         return (a == country) or (b == country)

#     rows_tx_country = []

#     # scenari in questo group (ordinati come scenario_names)
#     sc_in_g = sorted(tx_ce["scenario"].unique(),
#                      key=lambda s: scenario_names.index(s) if s in scenario_names else 999)

#     # Paesi target (usiamo direttamente country_code fornito)
#     target_countries = list(country_code)

#     for sc in sc_in_g:
#         for yr in years:
#             sub = tx_ce[(tx_ce["scenario"] == sc) & (tx_ce["year"] == yr)].copy()
#             if sub.empty:
#                 continue

#             # per ogni paese somma i contributi 50/50 di tutte le linee che lo coinvolgono
#             for ctry in target_countries:
#                 # filtra linee che includono il paese come primo o secondo nodo
#                 sub_ctry = sub[sub["location_norm"].apply(lambda k: _line_has_country(k, ctry))]
#                 if sub_ctry.empty:
#                     continue

#                 # allocazione metà costi e metà energia al paese
#                 inv_alloc  = float(sub_ctry["inv_M$"].sum())              # M$
#                 fom_alloc  = float(sub_ctry["fom_M$/yr"].sum())           # M$/yr
#                 enr_alloc  = float(sub_ctry["energy_GWh"].sum())  * 0.5   # GWh/yr

#                 if enr_alloc <= 0:
#                     lcoe_tx_ctry = np.nan
#                 else:
#                     pv_costs  = inv_alloc + fom_alloc * TX_PVAF     # M$
#                     pv_energy = enr_alloc * TX_PVAF                 # GWh
#                     lcoe_tx_ctry = (pv_costs / pv_energy) * 1000.0  # $/MWh

#                 rows_tx_country.append({
#                     "group": TX_GROUP,
#                     "scenario": sc,
#                     "year": yr,
#                     "location": ctry,
#                     "tech": "Transmission_New",
#                     "INV_alloc_M$": inv_alloc,
#                     "FOM_alloc_M$/yr": fom_alloc,
#                     "E_alloc_GWh/yr": enr_alloc,
#                     "LCOE_$_per_MWh": lcoe_tx_ctry
#                 })

#     lcoe_tx_country_df = pd.DataFrame(rows_tx_country)

#     if lcoe_tx_country_df.empty:
#         print("[INFO] Nessun paese con linee associate per il calcolo LCOE di trasmissione a livello paese.")
#     else:
#         # === EXPORT: file dedicato per verifica
#         out_xlsx = output_path / f"LCOE_Transmission_ByCountry_{TX_GROUP}.xlsx"
#         with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
#             for sc in sc_in_g:
#                 sub = lcoe_tx_country_df[lcoe_tx_country_df["scenario"] == sc][
#                     ["location","tech","year","LCOE_$_per_MWh"]
#                 ].copy()
#                 if sub.empty:
#                     pd.DataFrame(columns=["location","tech"] + years).to_excel(writer, sheet_name=sc[:31], index=False)
#                     continue
#                 pivot = (sub.pivot_table(index=["location","tech"], columns="year", values="LCOE_$_per_MWh",
#                                          aggfunc="mean").reindex(columns=years))
#                 # ordina righe secondo l’ordine country_code
#                 ordered_index = []
#                 for c in country_code:
#                     ordered_index += [idx for idx in pivot.index if isinstance(idx, tuple) and idx[0] == c]
#                 residual = [i for i in pivot.index if i not in ordered_index]
#                 pivot = pivot.loc[ordered_index + residual]
#                 pivot.to_excel(writer, sheet_name=sc[:31])

#             # (Facoltativo) foglio con i totali allocati per debug/validazione
#             totals = lcoe_tx_country_df.groupby(["scenario","year","location"], as_index=False)[
#                 ["INV_alloc_M$","FOM_alloc_M$/yr","E_alloc_GWh/yr"]
#             ].sum()
#             # ordina per scenario e location
#             totals = totals.sort_values(["scenario","year","location"])
#             totals.to_excel(writer, sheet_name="ALLOC_TOTALS", index=False)

#         print(f"[OK] Salvato Transmission-by-country LCOE: {out_xlsx}")

#===================================================================================================================================
#===================================================================================================================================
# %%
# LCOE ALL TECHS CALCULATION (Traditional Calculation --> Investment at year 0 and assume E_t equal for every lifetime year)

# PV, Wind, Hydro, OCGT, BESS, PHES
# set tecnologie (escludo Transmission_New)
target_techs = ['PV_New','W_New','Hydro_New','OCGT_New','BESS_New','PHES_New']
pvaf_cache = {t: pvaf(discount_rate, lifetime_years[t]) for t in target_techs}

# dataset con nomi uniformi
df_inv  = datasets["invest"].rename(columns={"invest_M$": "INV_M$"})
df_fom  = datasets["fixed_opex"].rename(columns={"fixed_opex_M$/yr": "FOM_M$/yr"})
df_vom  = datasets["variable_opex"].rename(columns={"var_opex_M$": "VOM_M$"})
df_prod = datasets["production"].rename(columns={"prod_GWh": "E_GWh/yr"})

rows_all = []  # accumula tutte le tech

for g in group_names:
    # scenari presenti davvero per il group (unione sui dataset)
    sc_all = set()
    for dfn in (df_inv, df_fom, df_vom, df_prod):
        sc_all |= set(dfn.loc[dfn["group"] == g, "scenario"].astype(str).unique())
    sc_in_g = sorted(sc_all, key=lambda s: scenario_names.index(s) if s in scenario_names else 999)

    for sc in sc_in_g:
        for yr in years:
            for tech in target_techs:
                N = lifetime_years[tech]
                pvaf_val = pvaf_cache[tech]

                # trova le location per cui esiste almeno 1 dato (tra inv/fom/vom/prod) per questa chiave
                locs = set()
                for dfn in (df_inv, df_fom, df_vom, df_prod):
                    sub = dfn[
                        (dfn["group"] == g) &
                        (dfn["scenario"].astype(str) == sc) &
                        (dfn["year"].astype(str) == yr) &
                        (dfn["tech"].astype(str) == tech)
                    ]
                    if not sub.empty:
                        locs.update(sub["location"].astype(str).unique().tolist())

                if not locs:
                    continue

                # tieni solo le location “note” (includono MOZ e SAPP già presenti nei file)
                locs = [l for l in sorted(locs) if l in country_code]

                for loc in locs:
                    inv_val = df_inv.loc[
                        (df_inv["group"] == g) & (df_inv["scenario"].astype(str) == sc) &
                        (df_inv["year"].astype(str) == yr) & (df_inv["location"].astype(str) == loc) &
                        (df_inv["tech"].astype(str) == tech),
                        "INV_M$"
                    ].sum()

                    fom_val = df_fom.loc[
                        (df_fom["group"] == g) & (df_fom["scenario"].astype(str) == sc) &
                        (df_fom["year"].astype(str) == yr) & (df_fom["location"].astype(str) == loc) &
                        (df_fom["tech"].astype(str) == tech),
                        "FOM_M$/yr"
                    ].sum()

                    vom_val = df_vom.loc[
                        (df_vom["group"] == g) & (df_vom["scenario"].astype(str) == sc) &
                        (df_vom["year"].astype(str) == yr) & (df_vom["location"].astype(str) == loc) &
                        (df_vom["tech"].astype(str) == tech),
                        "VOM_M$"
                    ].sum()

                    e_val = df_prod.loc[
                        (df_prod["group"] == g) & (df_prod["scenario"].astype(str) == sc) &
                        (df_prod["year"].astype(str) == yr) & (df_prod["location"].astype(str) == loc) &
                        (df_prod["tech"].astype(str) == tech),
                        "E_GWh/yr"
                    ].sum()

                    # DCF classico: INV a t=0; (FOM+VOM) per N anni; energia per N anni
                    if pd.isna(e_val) or float(e_val) <= 0:  # safe guard
                        lcoe = np.nan
                    else:
                        pv_costs  = float(inv_val) + (float(fom_val) + float(vom_val)) * pvaf_val  # M$
                        pv_energy = float(e_val) * pvaf_val                                       # GWh
                        lcoe      = (pv_costs / pv_energy) * 1000.0                              # $/MWh
                    
                    rows_all.append({
                        "group": g, "scenario": sc, "year": yr,
                        "location": loc, "tech": tech,
                        "LCOE_$_per_MWh": lcoe
                    })

# risultati in tabella
lcoe_all_df = pd.DataFrame(rows_all)

# TRANSMISSION
TX_GROUP = "Transmission_Expansion"
TX_N     = lifetime_years["Transmission_New"]
TX_PVAF  = pvaf(discount_rate, TX_N)

tx_ce = datasets["tx_costs_energy"].copy()
if tx_ce.empty:
    print("[INFO] tx_costs_energy vuoto: nessuna riga Transmission_New da accodare.")
else:
    # Considera solo Transmission_Expansion
    tx_ce = tx_ce[tx_ce["group"] == TX_GROUP].copy()
    tx_ce["scenario"] = tx_ce["scenario"].astype(str)
    tx_ce["year"]     = tx_ce["year"].astype(str)

    # Assunzioni (come richiesto):
    # - Investimenti e FOM sono già ripartiti 50/50 nel file => NON li dimezzo di nuovo.
    # - L'energia annuale la attribuisco 50/50 ai due paesi.
    HALVE_COSTS  = False
    HALVE_ENERGY = True

    def _line_has_country(line_key: str, country: str) -> bool:
        a, b = str(line_key).split(":")
        return (a == country) or (b == country)

    tx_rows_country = []

    # scenari ordinati
    sc_in_tx = sorted(tx_ce["scenario"].unique(),
                      key=lambda s: scenario_names.index(s) if s in scenario_names else 999)

    for sc in sc_in_tx:
        for yr in years:
            sub = tx_ce[(tx_ce["scenario"] == sc) & (tx_ce["year"] == yr)].copy()
            if sub.empty:
                continue

            # 1) LCOE per ciascun paese in country_code (incl. MOZ_NC, MOZ_S, MOZ, SAPP li gestiamo sotto)
            base_countries = [c for c in country_code if c not in ("MOZ", "SAPP")]
            for ctry in base_countries:
                sub_ctry = sub[sub["location_norm"].apply(lambda k: _line_has_country(k, ctry))]
                if sub_ctry.empty:
                    continue

                inv_sum = float(sub_ctry["inv_M$"].sum())
                fom_sum = float(sub_ctry["fom_M$/yr"].sum())
                eng_sum = float(sub_ctry["energy_GWh"].sum())

                inv_alloc = inv_sum * (0.5 if HALVE_COSTS else 1.0)     # M$
                fom_alloc = fom_sum * (0.5 if HALVE_COSTS else 1.0)     # M$/yr
                enr_alloc = eng_sum * (0.5 if HALVE_ENERGY else 1.0)    # GWh/yr

                if enr_alloc <= 0:
                    lcoe_tx_ctry = np.nan
                else:
                    pv_costs  = inv_alloc + fom_alloc * TX_PVAF
                    pv_energy = enr_alloc * TX_PVAF
                    lcoe_tx_ctry = (pv_costs / pv_energy) * 1000.0

                tx_rows_country.append({
                    "group": TX_GROUP,
                    "scenario": sc,
                    "year": yr,
                    "location": ctry,
                    "tech": "Transmission_New",
                    "LCOE_$_per_MWh": lcoe_tx_ctry,
                    # utili per le aggregazioni MOZ/SAPP:
                    "_pv_costs": pv_costs if enr_alloc > 0 else np.nan,
                    "_pv_energy": pv_energy if enr_alloc > 0 else 0.0
                })

            # 2) MOZ = MOZ_NC + MOZ_S (somma pv_costs e pv_energy delle due)
            moz_parts = ["MOZ_NC", "MOZ_S"]
            moz_rows = [r for r in tx_rows_country if (r["group"]==TX_GROUP and r["scenario"]==sc and r["year"]==yr and r["location"] in moz_parts)]
            if moz_rows:
                pv_costs_moz  = np.nansum([r["_pv_costs"] for r in moz_rows])
                pv_energy_moz = np.nansum([r["_pv_energy"] for r in moz_rows])
                lcoe_moz = np.nan if pv_energy_moz <= 0 else (pv_costs_moz / pv_energy_moz) * 1000.0
                tx_rows_country.append({
                    "group": TX_GROUP, "scenario": sc, "year": yr,
                    "location": "MOZ", "tech": "Transmission_New",
                    "LCOE_$_per_MWh": lcoe_moz,
                    "_pv_costs": pv_costs_moz, "_pv_energy": pv_energy_moz
                })

            # 3) SAPP = somma su TUTTI i paesi; “due volte” (×2) per contare entrambi i paesi
            #    Nota: il ×2 non cambia l'LCOE (si cancella), ma lo applichiamo per coerenza con la tua contabilità.
            rows_this_sy = [r for r in tx_rows_country if (r["group"]==TX_GROUP and r["scenario"]==sc and r["year"]==yr and r["location"] not in ("MOZ","SAPP"))]
            if rows_this_sy:
                pv_costs_sapp  = np.nansum([r["_pv_costs"]  for r in rows_this_sy]) * 2.0
                pv_energy_sapp = np.nansum([r["_pv_energy"] for r in rows_this_sy]) * 2.0
                lcoe_sapp = np.nan if pv_energy_sapp <= 0 else (pv_costs_sapp / pv_energy_sapp) * 1000.0
                tx_rows_country.append({
                    "group": TX_GROUP, "scenario": sc, "year": yr,
                    "location": "SAPP", "tech": "Transmission_New",
                    "LCOE_$_per_MWh": lcoe_sapp,
                    "_pv_costs": pv_costs_sapp, "_pv_energy": pv_energy_sapp
                })

    # drop colonne helper e converti in DF compatibile con lcoe_all_df
    lcoe_tx_country_for_merge = pd.DataFrame(tx_rows_country)[
        ["group","scenario","year","location","tech","LCOE_$_per_MWh"]
    ].copy()

    # Accoda alla tabella generale
    lcoe_all_df = pd.concat([lcoe_all_df, lcoe_tx_country_for_merge], ignore_index=True)

    print(f"[OK] Accodate {len(lcoe_tx_country_for_merge)} righe Transmission_New a lcoe_all_df.")

# Diesel For Unmet Demand
pvaf_diesel = pvaf(discount_rate, LT_Diesel)

diesel_rows = []
for g in group_names:
    # scenari effettivamente presenti nello stesso group anche in diesel_df
    sc_in_g = sorted(
        diesel_df.loc[diesel_df["group"] == g, "scenario"].astype(str).unique(),
        key=lambda s: scenario_names.index(s) if s in scenario_names else 999
    )
    for sc in sc_in_g:
        for yr in years:
            sub = diesel_df[
                (diesel_df["group"] == g) &
                (diesel_df["scenario"].astype(str) == sc) &
                (diesel_df["year"].astype(str) == yr)
            ].copy()
            if sub.empty:
                continue

            # tieni solo location “note”
            sub = sub[sub["location"].astype(str).isin(country_code)].copy()
            if sub.empty:
                continue

            for _, r in sub.iterrows():
                loc = str(r["location"])
                total_gwh = float(r["Total_Unmet_GWh"])
                if total_gwh <= 0:
                    lcoe_d = np.nan
                else:
                    inv_M  = float(r["Investment_M$"])
                    fom_My = float(r["Fixed_M$yr"])
                    vom_M  = float(r["Variable_M$"])
                    fuel_M = float(r["Fuel_M$"])

                    pv_costs  = inv_M + (fom_My + vom_M + fuel_M) * pvaf_diesel   # M$
                    pv_energy = total_gwh * pvaf_diesel                            # GWh
                    lcoe_d    = (pv_costs / pv_energy) * 1000.0                    # $/MWh

                diesel_rows.append({
                    "group": g, "scenario": str(sc), "year": str(yr),
                    "location": loc, "tech": "Diesel_Backup",
                    "LCOE_$_per_MWh": lcoe_d
                })

lcoe_diesel_df = pd.DataFrame(diesel_rows)
lcoe_all_df = pd.concat([lcoe_all_df, lcoe_diesel_df], ignore_index=True)
print(f"[OK] Accodate {len(lcoe_diesel_df)} righe Diesel_Backup a lcoe_all_df.")

# EXPORT: 1 file per group, 1 sheet per scenario, righe = location, tech; colonne = anni
for g in group_names:
    sub_g = lcoe_all_df[lcoe_all_df["group"] == g].copy()
    out_xlsx = output_path / f"LCOE_AllTechs_{g}.xlsx"
    with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        sc_in_g = sorted(sub_g["scenario"].astype(str).unique(), key=lambda s: scenario_names.index(s) if s in scenario_names else 999)
        for sc in sc_in_g:
            sub = sub_g[sub_g["scenario"] == sc][["location","tech","year","LCOE_$_per_MWh"]].copy()
            if sub.empty:
                pd.DataFrame(columns=["location","tech"] + years).to_excel(writer, sheet_name=sc[:31], index=False)
                continue
            pivot = (sub.pivot_table(index=["location","tech"], columns="year", values="LCOE_$_per_MWh",
                                     aggfunc="mean").reindex(columns=years))
            # ordina righe secondo l’ordine country_code (MOZ e SAPP inclusi)
            ordered_index = []
            for c in country_code:
                ordered_index += [idx for idx in pivot.index if isinstance(idx, tuple) and idx[0] == c]
            residual = [i for i in pivot.index if i not in ordered_index]
            pivot = pivot.loc[ordered_index + residual]
            pivot.to_excel(writer, sheet_name=sc[:31])
    print(f"[OK] Salvato: {out_xlsx}")

#===================================================================================================================================
#===================================================================================================================================
# %%
# SYSTEM LCOE (All technologies together) per paese + MOZ + SAPP

# --- setup
TARGET_TECHS = ['PV_New','W_New','Hydro_New','OCGT_New','BESS_New','PHES_New']  # gen+storage
TX_GROUP     = "Transmission_Expansion"
TX_N         = lifetime_years["Transmission_New"]
TX_PVAF      = pvaf(discount_rate, TX_N)
PVAF_TECH    = {t: pvaf(discount_rate, lifetime_years[t]) for t in TARGET_TECHS}
PVAF_DIESEL  = pvaf(discount_rate, LT_Diesel)

# --- dataset uniformati
df_inv  = datasets["invest"].rename(columns={"invest_M$": "INV_M$"})
df_fom  = datasets["fixed_opex"].rename(columns={"fixed_opex_M$/yr": "FOM_M$/yr"})
df_vom  = datasets["variable_opex"].rename(columns={"var_opex_M$": "VOM_M$"})
df_prod = datasets["production"].rename(columns={"prod_GWh": "E_GWh/yr"})

# --- raccoglitore componenti (per poi sommare PV costs/energy su tutto)
components = []  # [{'group','scenario','year','location','component','pv_costs','pv_energy'}]

# GEN/STORAGE tech (PV_New, W_New, Hydro_New, OCGT_New, BESS_New, PHES_New)
for g in group_names:
    # scenari effettivamente presenti
    sc_all = set()
    for dfn in (df_inv, df_fom, df_vom, df_prod):
        sc_all |= set(dfn.loc[dfn["group"] == g, "scenario"].astype(str).unique())
    sc_in_g = sorted(sc_all, key=lambda s: scenario_names.index(s) if s in scenario_names else 999)

    for sc in sc_in_g:
        for yr in years:
            for tech in TARGET_TECHS:
                pvaf_val = PVAF_TECH[tech]
                # individua location presenti in almeno un dataset
                locs = set()
                for dfn in (df_inv, df_fom, df_vom, df_prod):
                    sub = dfn[
                        (dfn["group"] == g) &
                        (dfn["scenario"].astype(str) == sc) &
                        (dfn["year"].astype(str) == yr) &
                        (dfn["tech"].astype(str) == tech)
                    ]
                    if not sub.empty:
                        locs.update(sub["location"].astype(str).unique().tolist())
                locs = [l for l in sorted(locs) if l in country_code]
                if not locs:
                    continue

                for loc in locs:
                    inv_val = df_inv.loc[
                        (df_inv["group"] == g) & (df_inv["scenario"].astype(str) == sc) &
                        (df_inv["year"].astype(str) == yr) & (df_inv["location"].astype(str) == loc) &
                        (df_inv["tech"].astype(str) == tech), "INV_M$"
                    ].sum()
                    fom_val = df_fom.loc[
                        (df_fom["group"] == g) & (df_fom["scenario"].astype(str) == sc) &
                        (df_fom["year"].astype(str) == yr) & (df_fom["location"].astype(str) == loc) &
                        (df_fom["tech"].astype(str) == tech), "FOM_M$/yr"
                    ].sum()
                    vom_val = df_vom.loc[
                        (df_vom["group"] == g) & (df_vom["scenario"].astype(str) == sc) &
                        (df_vom["year"].astype(str) == yr) & (df_vom["location"].astype(str) == loc) &
                        (df_vom["tech"].astype(str) == tech), "VOM_M$"
                    ].sum()
                    e_val = df_prod.loc[
                        (df_prod["group"] == g) & (df_prod["scenario"].astype(str) == sc) &
                        (df_prod["year"].astype(str) == yr) & (df_prod["location"].astype(str) == loc) &
                        (df_prod["tech"].astype(str) == tech), "E_GWh/yr"
                    ].sum()

                    if float(e_val) > 0:
                        pv_costs  = float(inv_val) + (float(fom_val) + float(vom_val)) * pvaf_val
                        pv_energy = float(e_val) * pvaf_val
                        components.append({
                            "group": g, "scenario": sc, "year": yr, "location": loc,
                            "component": tech, "pv_costs": pv_costs, "pv_energy": pv_energy
                        })

# DIESEL (da diesel_df già calcolato a monte)
for g in group_names:
    sub_g = diesel_df[diesel_df["group"] == g].copy()
    if sub_g.empty:
        continue
    sc_in_g = sorted(sub_g["scenario"].astype(str).unique(),
                     key=lambda s: scenario_names.index(s) if s in scenario_names else 999)
    for sc in sc_in_g:
        for yr in years:
            sub = sub_g[(sub_g["scenario"].astype(str) == sc) & (sub_g["year"].astype(str) == yr)]
            if sub.empty:
                continue
            for _, r in sub.iterrows():
                loc = str(r["location"])
                if loc not in country_code:  # tieni solo le location note
                    continue
                total_gwh = float(r["Total_Unmet_GWh"])
                if total_gwh <= 0:
                    continue
                pv_costs  = float(r["Investment_M$"]) + (float(r["Fixed_M$yr"]) + float(r["Variable_M$"]) + float(r["Fuel_M$"])) * PVAF_DIESEL
                pv_energy = total_gwh * PVAF_DIESEL
                components.append({
                    "group": g, "scenario": str(sc), "year": str(yr), "location": loc,
                    "component": "Diesel_Backup", "pv_costs": pv_costs, "pv_energy": pv_energy
                })

# TRANSMISSION per paese (da tx_costs_energy) – INV/FOM già split, energia /2 per paese
tx_ce = datasets["tx_costs_energy"].copy()
if not tx_ce.empty:
    tx_ce = tx_ce[tx_ce["group"] == TX_GROUP].copy()
    tx_ce["scenario"] = tx_ce["scenario"].astype(str)
    tx_ce["year"] = tx_ce["year"].astype(str)

    def _has_country(line_key: str, ctry: str) -> bool:
        a, b = str(line_key).split(":")
        return (a == ctry) or (b == ctry)

    base_countries = [c for c in country_code if c not in ("MOZ","SAPP")]
    for sc in sorted(tx_ce["scenario"].unique(), key=lambda s: scenario_names.index(s) if s in scenario_names else 999):
        for yr in years:
            sub = tx_ce[(tx_ce["scenario"] == sc) & (tx_ce["year"] == yr)]
            if sub.empty:
                continue
            for loc in base_countries:
                sub_loc = sub[sub["location_norm"].apply(lambda k: _has_country(k, loc))]
                if sub_loc.empty:
                    continue
                inv_sum = float(sub_loc["inv_M$"].sum())
                fom_sum = float(sub_loc["fom_M$/yr"].sum())
                eng_sum = float(sub_loc["energy_GWh"].sum())

                pv_costs  = inv_sum + fom_sum * TX_PVAF             # M$
                pv_energy = (eng_sum * 0.5) * TX_PVAF               # GWh
                if pv_energy <= 0:
                    continue
                components.append({
                    "group": TX_GROUP, "scenario": sc, "year": yr, "location": loc,
                    "component": "Transmission_New", "pv_costs": pv_costs, "pv_energy": pv_energy
                })

# ---- costruisci DF componenti
comp_df = pd.DataFrame(components)

# MOZ = MOZ_NC + MOZ_S (somma dei PV per componente, poi sommo su tutte le componenti)
def _agg_moz(df):
    mask = df["location"].isin(["MOZ_NC","MOZ_S"])
    moz = (df[mask]
           .groupby(["group","scenario","year"], as_index=False)[["pv_costs","pv_energy"]]
           .sum())
    moz["location"] = "MOZ"
    return moz

# Totali per paese (senza SAPP/MOZ): somma su tutte le componenti
tot_country = (comp_df[~comp_df["location"].isin(["MOZ","SAPP"])]
               .groupby(["group","scenario","year","location"], as_index=False)[["pv_costs","pv_energy"]]
               .sum())

# Aggiungi MOZ
moz_tot = _agg_moz(comp_df)
moz_tot = moz_tot[["group","scenario","year","location","pv_costs","pv_energy"]]
tot_all = pd.concat([tot_country, moz_tot], ignore_index=True)

# SAPP = somma su TUTTI i paesi; raddoppia SOLO la trasmissione (costs+energy)
if not comp_df.empty:
    base_countries = [c for c in country_code if c not in ("MOZ","SAPP")]
    # gen+storage+diesel
    comp_nd_tx = comp_df[(comp_df["location"].isin(base_countries)) & (comp_df["component"] != "Transmission_New")]
    sapp_nd = (comp_nd_tx.groupby(["group","scenario","year"], as_index=False)[["pv_costs","pv_energy"]]
               .sum())
    # transmission raddoppiata
    comp_tx = comp_df[(comp_df["location"].isin(base_countries)) & (comp_df["component"] == "Transmission_New")]
    sapp_tx = (comp_tx.groupby(["group","scenario","year"], as_index=False)[["pv_costs","pv_energy"]]
               .sum())

    sapp_tot = sapp_nd.merge(sapp_tx, on=["group","scenario","year"], how="outer", suffixes=("_nd","_tx")).fillna(0.0)
    sapp_tot["pv_costs"]  = sapp_tot["pv_costs_nd"]  + sapp_tot["pv_costs_tx"]
    sapp_tot["pv_energy"] = sapp_tot["pv_energy_nd"] + sapp_tot["pv_energy_tx"]
    sapp_tot = sapp_tot[["group","scenario","year","pv_costs","pv_energy"]]
    sapp_tot["location"] = "SAPP"

    tot_all = pd.concat([tot_all, sapp_tot], ignore_index=True)

# Calcolo LCOE finale “All_Techs”
tot_all["LCOE_$_per_MWh"] = np.where(tot_all["pv_energy"] > 0,
                                     (tot_all["pv_costs"] / tot_all["pv_energy"]) * 1000.0,
                                     np.nan)
system_lcoe_df = tot_all[["group","scenario","year","location","LCOE_$_per_MWh"]].copy()
system_lcoe_df["tech"] = "All_Techs"

# EXPORT: un file per group, uno sheet per scenario (formato simile a LCOE tecnologico)
for g in group_names:
    sub_g = system_lcoe_df[system_lcoe_df["group"] == g].copy()
    if sub_g.empty:
        continue
    out_xlsx = output_path / f"LCOE_System_AllTechs_{g}.xlsx"
    with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        scs = sorted(sub_g["scenario"].astype(str).unique(),
                     key=lambda s: scenario_names.index(s) if s in scenario_names else 999)
        for sc in scs:
            sub = sub_g[sub_g["scenario"] == sc][["location","tech","year","LCOE_$_per_MWh"]].copy()
            if sub.empty:
                pd.DataFrame(columns=["location","tech"] + years).to_excel(writer, sheet_name=sc[:31], index=False)
                continue
            pivot = (sub.pivot_table(index=["location","tech"], columns="year", values="LCOE_$_per_MWh",
                                     aggfunc="mean").reindex(columns=years))
            # Ordina righe secondo l’ordine country_code (inclusi MOZ e SAPP)
            ordered_index = []
            for c in country_code:
                ordered_index += [idx for idx in pivot.index if isinstance(idx, tuple) and idx[0] == c]
            residual = [i for i in pivot.index if i not in ordered_index]
            pivot = pivot.loc[ordered_index + residual]
            pivot.to_excel(writer, sheet_name=sc[:31])
    print(f"[OK] Salvato System LCOE: {out_xlsx}")

#===================================================================================================================================
#===================================================================================================================================
# %%
# Optional: Calculation of LCOE with alternative Method (Results should be equal to Calliope)
# Annualize investment over lifetime (instead of all at year 0) using the CRF

# Tech Level LCOE Calculation with CRF

def crf(r: float, N: int) -> float:
    r = float(r)
    return (r * (1 + r)**N) / ((1 + r)**N - 1)

# CRF per le tech
CRF = {t: crf(discount_rate, lifetime_years[t]) for t in ['PV_New','W_New','Hydro_New','OCGT_New','BESS_New','PHES_New','Transmission_New']}
CRF_DIESEL = crf(discount_rate, LT_Diesel)

# Dataset uniformati (ANNUALIZED + O&M + Production)
df_ann  = datasets["annualized_invest"].rename(columns={"annualized_invest_M$/yr":"ANNINV_M$/yr"})
df_fom  = datasets["fixed_opex"].rename(columns={"fixed_opex_M$/yr":"FOM_M$/yr"})
df_vom  = datasets["variable_opex"].rename(columns={"var_opex_M$":"VOM_M$"})
df_prod = datasets["production"].rename(columns={"prod_GWh":"E_GWh/yr"})

rows_all_crf = []

# ---- GEN/STORAGE: usa Annualized_Investments (M$/yr) + FOM + VOM; LCOE = cost_yr / E_yr
for g in group_names:
    sc_all = set()
    for dfn in (df_ann, df_fom, df_vom, df_prod):
        sc_all |= set(dfn.loc[dfn["group"] == g, "scenario"].astype(str).unique())
    sc_in_g = sorted(sc_all, key=lambda s: scenario_names.index(s) if s in scenario_names else 999)

    for sc in sc_in_g:
        for yr in years:
            for tech in ['PV_New','W_New','Hydro_New','OCGT_New','BESS_New','PHES_New']:
                # individua location presenti
                locs = set()
                for dfn in (df_ann, df_fom, df_vom, df_prod):
                    sub = dfn[(dfn["group"] == g) &
                              (dfn["scenario"].astype(str) == sc) &
                              (dfn["year"].astype(str) == yr) &
                              (dfn["tech"].astype(str) == tech)]
                    if not sub.empty:
                        locs.update(sub["location"].astype(str).unique().tolist())
                locs = [l for l in sorted(locs) if l in country_code]
                if not locs:
                    continue

                for loc in locs:
                    anninv = df_ann.loc[(df_ann["group"]==g)&(df_ann["scenario"].astype(str)==sc)&
                                        (df_ann["year"].astype(str)==yr)&(df_ann["location"].astype(str)==loc)&
                                        (df_ann["tech"].astype(str)==tech), "ANNINV_M$/yr"].sum()
                    fom = df_fom.loc[(df_fom["group"]==g)&(df_fom["scenario"].astype(str)==sc)&
                                     (df_fom["year"].astype(str)==yr)&(df_fom["location"].astype(str)==loc)&
                                     (df_fom["tech"].astype(str)==tech), "FOM_M$/yr"].sum()
                    vom = df_vom.loc[(df_vom["group"]==g)&(df_vom["scenario"].astype(str)==sc)&
                                     (df_vom["year"].astype(str)==yr)&(df_vom["location"].astype(str)==loc)&
                                     (df_vom["tech"].astype(str)==tech), "VOM_M$"].sum()
                    eyr = df_prod.loc[(df_prod["group"]==g)&(df_prod["scenario"].astype(str)==sc)&
                                      (df_prod["year"].astype(str)==yr)&(df_prod["location"].astype(str)==loc)&
                                      (df_prod["tech"].astype(str)==tech), "E_GWh/yr"].sum()

                    if float(eyr) > 0:
                        cost_yr = float(anninv) + float(fom) + float(vom)   # M$/yr
                        lcoe = (cost_yr / float(eyr)) * 1000.0              # $/MWh
                    else:
                        lcoe = np.nan

                    rows_all_crf.append({
                        "group": g, "scenario": sc, "year": yr,
                        "location": loc, "tech": tech,
                        "LCOE_$_per_MWh": lcoe
                    })

# ---- TRANSMISSION_New: inv_M$*CRF_TX + fom_M$/yr ; energia (GWh/yr) / 2 per paese; più MOZ e SAPP
TX_GROUP = "Transmission_Expansion"
tx_ce = datasets["tx_costs_energy"].copy()
if not tx_ce.empty:
    tx_ce = tx_ce[tx_ce["group"] == TX_GROUP].copy()
    tx_ce["scenario"] = tx_ce["scenario"].astype(str)
    tx_ce["year"]     = tx_ce["year"].astype(str)

    def _has_country(line_key: str, ctry: str) -> bool:
        a, b = str(line_key).split(":")
        return (a == ctry) or (b == ctry)

    tx_rows_tmp = []  # per costruire anche MOZ e SAPP
    base_countries = [c for c in country_code if c not in ("MOZ","SAPP")]

    for sc in sorted(tx_ce["scenario"].unique(), key=lambda s: scenario_names.index(s) if s in scenario_names else 999):
        for yr in years:
            sub = tx_ce[(tx_ce["scenario"] == sc) & (tx_ce["year"] == yr)]
            if sub.empty: 
                continue

            # per-paese (INV,FOM già 50/50 nel file; energia /2)
            for loc in base_countries:
                sub_loc = sub[sub["location_norm"].apply(lambda k: _has_country(k, loc))]
                if sub_loc.empty:
                    continue
                inv = float(sub_loc["inv_M$"].sum())
                fom = float(sub_loc["fom_M$/yr"].sum())
                eyr = float(sub_loc["energy_GWh"].sum()) * 0.5

                if eyr > 0:
                    cost_yr = inv * CRF["Transmission_New"] + fom
                    lcoe = (cost_yr / eyr) * 1000.0
                else:
                    lcoe = np.nan

                tx_rows_tmp.append({
                    "group": TX_GROUP, "scenario": sc, "year": yr,
                    "location": loc, "tech": "Transmission_New",
                    "LCOE_$_per_MWh": lcoe,
                    "_cost_yr": (inv * CRF["Transmission_New"] + fom),
                    "_E_yr": eyr
                })

            # MOZ = MOZ_NC + MOZ_S (sommando costi annui ed energia annua)
            moz_rows = [r for r in tx_rows_tmp if r["group"]==TX_GROUP and r["scenario"]==sc and r["year"]==yr and r["location"] in ("MOZ_NC","MOZ_S")]
            if moz_rows:
                cyr = float(np.nansum([r["_cost_yr"] for r in moz_rows]))
                eyr = float(np.nansum([r["_E_yr"] for r in moz_rows]))
                lcoe = np.nan if eyr<=0 else (cyr/eyr)*1000.0
                tx_rows_tmp.append({
                    "group": TX_GROUP, "scenario": sc, "year": yr,
                    "location": "MOZ", "tech": "Transmission_New",
                    "LCOE_$_per_MWh": lcoe,
                    "_cost_yr": cyr, "_E_yr": eyr
                })

            # SAPP = somma su tutti i paesi (raddoppia costi+energia transmission)
            rows_sy = [r for r in tx_rows_tmp if r["group"]==TX_GROUP and r["scenario"]==sc and r["year"]==yr and r["location"] not in ("MOZ","SAPP")]
            if rows_sy:
                cyr = float(np.nansum([r["_cost_yr"] for r in rows_sy])) * 2.0
                eyr = float(np.nansum([r["_E_yr"]   for r in rows_sy])) * 2.0
                lcoe = np.nan if eyr<=0 else (cyr/eyr)*1000.0
                tx_rows_tmp.append({
                    "group": TX_GROUP, "scenario": sc, "year": yr,
                    "location": "SAPP", "tech": "Transmission_New",
                    "LCOE_$_per_MWh": lcoe
                })

    # aggiungi a rows_all_crf
    rows_all_crf += [
        {k: r[k] for k in ["group","scenario","year","location","tech","LCOE_$_per_MWh"]}
        for r in tx_rows_tmp
    ]

# ---- DIESEL (annuity): INV*CRF_DIESEL + Fixed + Variable + Fuel ; E = Total_Unmet_GWh
for g in group_names:
    sub_g = diesel_df[diesel_df["group"] == g].copy()
    if sub_g.empty: 
        continue
    scs = sorted(sub_g["scenario"].astype(str).unique(), key=lambda s: scenario_names.index(s) if s in scenario_names else 999)
    for sc in scs:
        for yr in years:
            sub = sub_g[(sub_g["scenario"].astype(str)==sc)&(sub_g["year"].astype(str)==yr)]
            if sub.empty: 
                continue
            sub = sub[sub["location"].astype(str).isin(country_code)]
            if sub.empty:
                continue
            for _, r in sub.iterrows():
                loc = str(r["location"])
                eyr = float(r["Total_Unmet_GWh"])
                if eyr <= 0:
                    lcoe = np.nan
                else:
                    cost_yr = float(r["Investment_M$"]) * CRF_DIESEL + float(r["Fixed_M$yr"]) + float(r["Variable_M$"]) + float(r["Fuel_M$"])
                    lcoe = (cost_yr / eyr) * 1000.0
                rows_all_crf.append({
                    "group": g, "scenario": sc, "year": yr,
                    "location": loc, "tech": "Diesel_Backup",
                    "LCOE_$_per_MWh": lcoe
                })

# OUTPUT:
lcoe_all_crf_df = pd.DataFrame(rows_all_crf)

for g in group_names:
    sub_g = lcoe_all_crf_df[lcoe_all_crf_df["group"] == g].copy()
    out_xlsx = output_path / f"LCOE_AllTechs_CRF_{g}.xlsx"
    with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        scs = sorted(sub_g["scenario"].astype(str).unique(), key=lambda s: scenario_names.index(s) if s in scenario_names else 999)
        for sc in scs:
            sub = sub_g[sub_g["scenario"] == sc][["location","tech","year","LCOE_$_per_MWh"]].copy()
            if sub.empty:
                pd.DataFrame(columns=["location","tech"] + years).to_excel(writer, sheet_name=sc[:31], index=False); continue
            pivot = (sub.pivot_table(index=["location","tech"], columns="year", values="LCOE_$_per_MWh",
                                     aggfunc="mean").reindex(columns=years))
            # ordina secondo country_code
            ordered_index, residual = [], []
            for c in country_code:
                ordered_index += [idx for idx in pivot.index if isinstance(idx, tuple) and idx[0] == c]
            residual = [i for i in pivot.index if i not in ordered_index]
            pivot = pivot.loc[ordered_index + residual]
            pivot.to_excel(writer, sheet_name=sc[:31])
    print(f"[OK] Salvato (CRF Tech): {out_xlsx}")

#===================================================================================================================================
#===================================================================================================================================
# %% SYSTEM LCOE (All technologies) — CRF / Annuity

# Riusa CRF e CRF_DIESEL definiti sopra; datasets & diesel_df già caricati.

# 1) Raccogli componenti ANNUALIZZATE (cost_yr e E_yr) per (group,scenario,year,location)
components_crf = []  # -> [{group,scenario,year,location,component,cost_yr,E_yr}]

# GEN/STORAGE: Annualized_INV + FOM + VOM ; E_yr = prod_GWh
for g in group_names:
    sc_all = set()
    for dfn in (df_ann, df_fom, df_vom, df_prod):
        sc_all |= set(dfn.loc[dfn["group"]==g, "scenario"].astype(str).unique())
    scs = sorted(sc_all, key=lambda s: scenario_names.index(s) if s in scenario_names else 999)

    for sc in scs:
        for yr in years:
            for tech in ['PV_New','W_New','Hydro_New','OCGT_New','BESS_New','PHES_New']:
                locs = set()
                for dfn in (df_ann, df_fom, df_vom, df_prod):
                    sub = dfn[(dfn["group"]==g)&(dfn["scenario"].astype(str)==sc)&(dfn["year"].astype(str)==yr)&(dfn["tech"].astype(str)==tech)]
                    if not sub.empty:
                        locs.update(sub["location"].astype(str).tolist())
                locs = [l for l in sorted(locs) if l in country_code]
                if not locs: 
                    continue

                for loc in locs:
                    anninv = df_ann.loc[(df_ann["group"]==g)&(df_ann["scenario"].astype(str)==sc)&(df_ann["year"].astype(str)==yr)&(df_ann["location"].astype(str)==loc)&(df_ann["tech"].astype(str)==tech),"ANNINV_M$/yr"].sum()
                    fom    = df_fom.loc[(df_fom["group"]==g)&(df_fom["scenario"].astype(str)==sc)&(df_fom["year"].astype(str)==yr)&(df_fom["location"].astype(str)==loc)&(df_fom["tech"].astype(str)==tech),"FOM_M$/yr"].sum()
                    vom    = df_vom.loc[(df_vom["group"]==g)&(df_vom["scenario"].astype(str)==sc)&(df_vom["year"].astype(str)==yr)&(df_vom["location"].astype(str)==loc)&(df_vom["tech"].astype(str)==tech),"VOM_M$"].sum()
                    eyr    = df_prod.loc[(df_prod["group"]==g)&(df_prod["scenario"].astype(str)==sc)&(df_prod["year"].astype(str)==yr)&(df_prod["location"].astype(str)==loc)&(df_prod["tech"].astype(str)==tech),"E_GWh/yr"].sum()
                    if float(eyr) <= 0:
                        continue
                    components_crf.append({
                        "group": g, "scenario": sc, "year": yr, "location": loc,
                        "component": tech, "cost_yr": float(anninv)+float(fom)+float(vom), "E_yr": float(eyr)
                    })

# DIESEL (annuity)
for g in group_names:
    sub_g = diesel_df[diesel_df["group"] == g].copy()
    if sub_g.empty: 
        continue
    scs = sorted(sub_g["scenario"].astype(str).unique(), key=lambda s: scenario_names.index(s) if s in scenario_names else 999)
    for sc in scs:
        for yr in years:
            sub = sub_g[(sub_g["scenario"].astype(str)==sc)&(sub_g["year"].astype(str)==yr)]
            if sub.empty: 
                continue
            sub = sub[sub["location"].astype(str).isin(country_code)]
            if sub.empty:
                continue
            for _, r in sub.iterrows():
                eyr = float(r["Total_Unmet_GWh"])
                if eyr <= 0:
                    continue
                cost_yr = float(r["Investment_M$"])*CRF_DIESEL + float(r["Fixed_M$yr"]) + float(r["Variable_M$"]) + float(r["Fuel_M$"])
                components_crf.append({
                    "group": g, "scenario": str(sc), "year": str(yr),
                    "location": str(r["location"]), "component": "Diesel_Backup",
                    "cost_yr": cost_yr, "E_yr": eyr
                })

# TRANSMISSION per paese (INV,FOM già 50/50; E/2)
tx_ce = datasets["tx_costs_energy"].copy()
if not tx_ce.empty:
    tx_ce = tx_ce[tx_ce["group"] == TX_GROUP].copy()
    tx_ce["scenario"] = tx_ce["scenario"].astype(str)
    tx_ce["year"]     = tx_ce["year"].astype(str)

    def _has_country(line_key: str, ctry: str) -> bool:
        a, b = str(line_key).split(":")
        return (a == ctry) or (b == ctry)

    base_countries = [c for c in country_code if c not in ("MOZ","SAPP")]

    for sc in sorted(tx_ce["scenario"].unique(), key=lambda s: scenario_names.index(s) if s in scenario_names else 999):
        for yr in years:
            sub = tx_ce[(tx_ce["scenario"]==sc)&(tx_ce["year"]==yr)]
            if sub.empty:
                continue
            for loc in base_countries:
                sub_loc = sub[sub["location_norm"].apply(lambda k: _has_country(k, loc))]
                if sub_loc.empty:
                    continue
                inv = float(sub_loc["inv_M$"].sum())
                fom = float(sub_loc["fom_M$/yr"].sum())
                eyr = float(sub_loc["energy_GWh"].sum()) * 0.5
                if eyr <= 0:
                    continue
                cost_yr = inv * CRF["Transmission_New"] + fom
                components_crf.append({
                    "group": TX_GROUP, "scenario": sc, "year": yr, "location": loc,
                    "component": "Transmission_New", "cost_yr": cost_yr, "E_yr": eyr
                })

# 2) Costruisci DF componenti
comp_crf_df = pd.DataFrame(components_crf)

# 3) Totali per paese (senza MOZ/SAPP)
tot_country = (comp_crf_df[~comp_crf_df["location"].isin(["MOZ","SAPP"])]
               .groupby(["group","scenario","year","location"], as_index=False)[["cost_yr","E_yr"]]
               .sum())

# 4) MOZ = MOZ_NC + MOZ_S
def _agg_moz_crf(df):
    mask = df["location"].isin(["MOZ_NC","MOZ_S"])
    moz = (df[mask].groupby(["group","scenario","year"], as_index=False)[["cost_yr","E_yr"]].sum())
    moz["location"] = "MOZ"
    return moz

moz_tot = _agg_moz_crf(comp_crf_df)
moz_tot = moz_tot[["group","scenario","year","location","cost_yr","E_yr"]]

tot_all = pd.concat([tot_country, moz_tot], ignore_index=True)

# 5) SAPP = somma su TUTTI i paesi; raddoppia SOLO la trasmissione (costi+energia)
base_countries = [c for c in country_code if c not in ("MOZ","SAPP")]
if not comp_crf_df.empty:
    comp_nd_tx = comp_crf_df[(comp_crf_df["location"].isin(base_countries)) & (comp_crf_df["component"] != "Transmission_New")]
    sapp_nd = comp_nd_tx.groupby(["group","scenario","year"], as_index=False)[["cost_yr","E_yr"]].sum()

    comp_tx = comp_crf_df[(comp_crf_df["location"].isin(base_countries)) & (comp_crf_df["component"] == "Transmission_New")]
    sapp_tx = comp_tx.groupby(["group","scenario","year"], as_index=False)[["cost_yr","E_yr"]].sum()
    sapp_tx[["cost_yr","E_yr"]] *= 2.0   # conta entrambi i lati delle linee

    sapp_tot = sapp_nd.merge(sapp_tx, on=["group","scenario","year"], how="outer", suffixes=("_nd","_tx")).fillna(0.0)
    sapp_tot["cost_yr"] = sapp_tot["cost_yr_nd"] + sapp_tot["cost_yr_tx"]
    sapp_tot["E_yr"]    = sapp_tot["E_yr_nd"]    + sapp_tot["E_yr_tx"]
    sapp_tot = sapp_tot[["group","scenario","year","cost_yr","E_yr"]]
    sapp_tot["location"] = "SAPP"

    tot_all = pd.concat([tot_all, sapp_tot], ignore_index=True)

# 6) LCOE di sistema (CRF)
tot_all["LCOE_$_per_MWh"] = np.where(tot_all["E_yr"] > 0, (tot_all["cost_yr"] / tot_all["E_yr"]) * 1000.0, np.nan)
system_lcoe_crf_df = tot_all[["group","scenario","year","location","LCOE_$_per_MWh"]].copy()
system_lcoe_crf_df["tech"] = "All_Techs"

# 7) OUTPUT: file simili ma con nome diverso (CRF)
for g in group_names:
    sub_g = system_lcoe_crf_df[system_lcoe_crf_df["group"] == g].copy()
    if sub_g.empty:
        continue
    out_xlsx = output_path / f"LCOE_System_AllTechs_CRF_{g}.xlsx"
    with ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        scs = sorted(sub_g["scenario"].astype(str).unique(), key=lambda s: scenario_names.index(s) if s in scenario_names else 999)
        for sc in scs:
            sub = sub_g[sub_g["scenario"] == sc][["location","tech","year","LCOE_$_per_MWh"]].copy()
            if sub.empty:
                pd.DataFrame(columns=["location","tech"] + years).to_excel(writer, sheet_name=sc[:31], index=False); continue
            pivot = (sub.pivot_table(index=["location","tech"], columns="year", values="LCOE_$_per_MWh",
                                     aggfunc="mean").reindex(columns=years))
            # ordine country_code (incl. MOZ, SAPP)
            ordered_index = []
            for c in country_code:
                ordered_index += [idx for idx in pivot.index if isinstance(idx, tuple) and idx[0] == c]
            residual = [i for i in pivot.index if i not in ordered_index]
            pivot = pivot.loc[ordered_index + residual]
            pivot.to_excel(writer, sheet_name=sc[:31])
    print(f"[OK] Salvato (CRF System): {out_xlsx}")
 
#===================================================================================================================================
#===================================================================================================================================
# END