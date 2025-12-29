import os
import re
import sys
from pathlib import Path
import pandas as pd
import yaml

base_input_dir = r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\EnergyCap\Results"
base_output_dir = r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\YamlCreation\Output"

groups = {
    # "Autarky",
    # "Existing_Transmission",
    "Transmission_Expansion"
}
years = {
    # "2030",
    "2035",
}
scenarios = {
    "VRES_BESS",
    "VRES_BESS+PHES",
    "VRES_no_Storage",
    "VRES_PHES",
    "VRES+Hydro4_BESS",
    "VRES+Hydro4_BESS+PHES",
    "VRES+Hydro4_no_Storage",
    "VRES+Hydro4_PHES",
    "VRES+Hydro4+NG_BESS",
    "VRES+Hydro4+NG_BESS+PHES",
    "VRES+Hydro4+NG_no_Storage",
    "VRES+Hydro4+NG_PHES"
}

for group in sorted(groups):
    for year in sorted(years):
        for scenario in sorted(scenarios):
            # Input / Output
            input_dir = Path(base_input_dir) / group / year / f"{group}_{year}_{scenario}_Recap.xlsx"
            output_dir = Path(base_output_dir) / group / year / scenario
            output_dir.mkdir(parents=True, exist_ok=True)
            print("INPUT_DIR :", input_dir)

            if not input_dir.exists():
                print(f"[SKIP] File non trovato: {input_dir}")
                continue

            try:
                dfs: dict[str, pd.DataFrame] = pd.read_excel(input_dir, sheet_name=None)
            except Exception as e:
                print(f"[ERRORE] Lettura Excel fallita: {input_dir}\n   → {e}")
                continue

            print(f"[OK] Letto: {input_dir.name} | sheets: {list(dfs.keys())}")
            print("OUTPUT_DIR:", output_dir)

            present = set(dfs.keys())
            families: list[tuple[str, str, bool]] = [
                ("Location_Constraints_MSR.yaml",   "locations", ("PV" in present) or ("W" in present)),
                ("Location_Constraints_BESS.yaml",  "locations", "BESS_New"   in present),
                ("Location_Constraints_PHES.yaml",  "locations", "PHES_New"   in present),
                ("Location_Constraints_Hydro.yaml", "locations", "Hydro"      in present),
                ("Transmission_links_Free.yaml",    "links",     "400_kV_New" in present),
                ("Location_Constraints_NG.yaml",    "locations", "OCGT_pp_New" in present),
            ]

            # --- scheletri (indent=4) ---
            for fname, root_key, needed in families:
                if not needed:
                    continue
                out_path = output_dir / fname
                data = {root_key: {}}
                try:
                    text = yaml.dump(data, sort_keys=False, allow_unicode=True, indent=4, width=4096)
                    # non serve sostituire .inf qui (non presente), ma lasciamo lo stesso pattern ovunque
                    text = text.replace(".inf", "inf")
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    print(f"   Created Base: {out_path}")
                except Exception as e:
                    print(f"   [ERRORE] Creazione YAML fallita: {out_path}\n      → {e}")
            # ============================================================================================
            # ================== MSR (PV + Wind) ==================
            pv_df = dfs.get("PV")
            w_df  = dfs.get("W")
            if (pv_df is not None) or (w_df is not None):
                msr_yaml = {"locations": {}}

                def _ensure_country(country):
                    node = msr_yaml["locations"].setdefault(str(country), {})
                    node.setdefault("techs", {})
                    return node["techs"]

                def _normalize_msr_id(val):
                    import math
                    if val is None:
                        return ""
                    if isinstance(val, int):
                        return str(val)
                    if isinstance(val, float):
                        if math.isnan(val):
                            return ""
                        return str(int(val))
                    s = str(val).strip()
                    if s.isdigit():
                        return str(int(s))
                    return s

                def _add_entry(country, tech_name, min_cap, max_cap, resource_file, msr_id_str):
                    try:
                        min_cap = float(min_cap)
                    except Exception:
                        min_cap = 0.0
                    try:
                        max_cap = float(max_cap)
                    except Exception:
                        max_cap = 0.0

                    techs = _ensure_country(country)
                    techs[tech_name] = {
                        "constraints": {
                            "energy_cap_min": min_cap,  # Installed_kW
                            "energy_cap_max": max_cap,  # Max_kW
                            "resource": f"file={resource_file}:{country}{msr_id_str}",
                            "resource_unit": "energy_per_cap",
                        }
                    }

                def _process_msr_sheet(df, tech_prefix, resource_file):
                    required = {"Country", "MSR_ID", "Installed_kW", "Max_kW"}
                    missing = required - set(df.columns)
                    if missing:
                        print(f"   ⚠ MSR sheet mancano colonne {missing} (prefix={tech_prefix}); salto.")
                        return

                    grp = (
                        df.groupby(["Country", "MSR_ID"], as_index=False, dropna=False)
                          .agg({"Installed_kW": "sum", "Max_kW": "max"})
                    )

                    for _, r in grp.iterrows():
                        country = str(r["Country"])
                        msr_id  = _normalize_msr_id(r["MSR_ID"])
                        tech_name = f"{tech_prefix}_{country}_MSR{msr_id}"
                        _add_entry(country, tech_name, r["Installed_kW"], r["Max_kW"], resource_file, msr_id)

                if pv_df is not None:
                    _process_msr_sheet(pv_df, tech_prefix="PV",   resource_file="Solar_SAPP_MSR.csv")
                if w_df is not None:
                    _process_msr_sheet(w_df,  tech_prefix="Wind", resource_file="Wind_SAPP_MSR.csv")

                out_path = output_dir / "Location_Constraints_MSR.yaml"
                try:
                    text = yaml.dump(msr_yaml, sort_keys=False, allow_unicode=True, indent=4, width=4096)
                    text = text.replace(".inf", "inf")
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    print(f"   ✔ Scritto MSR: {out_path}")
                except Exception as e:
                    print(f"   [ERRORE] Scrittura MSR fallita: {out_path}\n      → {e}")
            # ============================================================================================
            # ================== HYDRO (progetti nominati a quarti) ==================
            hydro_df = dfs.get("Hydro")
            if hydro_df is not None:
                hydro_yaml = {"locations": {}}

                def _ensure_country_h(country: str):
                    node = hydro_yaml["locations"].setdefault(str(country), {})
                    node.setdefault("techs", {})
                    return node["techs"]

                def _extract_index_from_tech(tech: str) -> str:
                    s = str(tech).strip()
                    m = re.search(r"_(\d+)$", s)
                    return m.group(1) if m else ""

                def _map_resource_country_code(country: str) -> str:
                    # eccezione Angola: AO invece di AGO (per il dataset attuale)
                    return "AO" if str(country) == "AGO" else str(country)

                for _, r in hydro_df.iterrows():
                    country  = str(r.get("Country", "")).strip()
                    tech     = str(r.get("Tech", "")).strip()
                    try:
                        installed = float(r.get("Installed Cap [kW]", 0.0))
                    except Exception:
                        installed = 0.0
                    try:
                        total = float(r.get("Total Cap [kW]", 0.0))
                    except Exception:
                        total = 0.0

                    units_max = 4
                    per_unit = (total / units_max) if units_max > 0 else 0.0
                    if per_unit > 0:
                        units_used = int(round(installed / per_unit))
                    else:
                        units_used = 0
                    if units_used < 0:
                        units_used = 0
                    if units_used > units_max:
                        units_used = units_max

                    techs = _ensure_country_h(country)
                    idx = _extract_index_from_tech(tech)
                    res_code = _map_resource_country_code(country)

                    techs[tech] = {
                        "constraints": {
                            "units_max": units_max,
                            "units_equals": units_used,
                            "energy_cap_per_unit": per_unit,
                            # niente energy_cap_min/max (come da tua scelta)
                            "resource": f"file=Hydro_SAPP_New.csv:{res_code}{idx}",
                            "resource_unit": "energy_per_cap",
                        }
                    }

                out_path = output_dir / "Location_Constraints_Hydro.yaml"
                try:
                    text = yaml.dump(hydro_yaml, sort_keys=False, allow_unicode=True, indent=4, width=4096)
                    text = text.replace(".inf", "inf")
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    print(f"   ✔ Scritto Hydro: {out_path}")
                except Exception as e:
                    print(f"   [ERRORE] Scrittura Hydro fallita: {out_path}\n      → {e}")
            # ============================================================================================
            # ================== OCGT_pp_New (NG) ==================
            ng_df = dfs.get("OCGT_pp_New")
            if ng_df is None:
                ng_df = dfs.get("NG")

            if ng_df is None:
                print("   ⚠ Nessun foglio OCGT_pp_New/NG trovato; salto NG.")
            else:
                ng_yaml = {"locations": {}}

                def _ensure_country_ng(country: str):
                    node = ng_yaml["locations"].setdefault(str(country), {})
                    node.setdefault("techs", {})
                    return node["techs"]

                req = {"Country", "Installed_kW"}
                if not req.issubset(set(ng_df.columns)):
                    print("   ⚠ NG sheet mancano colonne richieste; salto.")
                else:
                    grp = (ng_df.groupby(["Country"], as_index=False, dropna=False)
                               .agg({"Installed_kW": "sum"}))

                    for _, r in grp.iterrows():
                        country = str(r["Country"])
                        try:
                            installed = float(r["Installed_kW"])
                        except Exception:
                            installed = 0.0

                        techs = _ensure_country_ng(country)
                        techs["OCGT_pp_New"] = {
                            "constraints": {
                                "energy_cap_min": installed,
                                "energy_cap_max": float("inf")   # poi .inf → inf
                            }
                        }

                    out_path = output_dir / "Location_Constraints_NG.yaml"
                    try:
                        text = yaml.dump(ng_yaml, sort_keys=False, allow_unicode=True, indent=4, width=4096)
                        text = text.replace(".inf", "inf")
                        with open(out_path, "w", encoding="utf-8") as f:
                            f.write(text)
                        print(f"   ✔ Scritto NG: {out_path}")
                    except Exception as e:
                        print(f"   [ERRORE] Scrittura NG fallita: {out_path}\n      → {e}")
            # ============================================================================================
            # ================== BESS_New ==================
            bess_df = dfs.get("BESS_New")
            if bess_df is not None:
                bess_yaml = {"locations": {}}

                def _ensure_country_b(country: str):
                    node = bess_yaml["locations"].setdefault(str(country), {})
                    node.setdefault("techs", {})
                    return node["techs"]

                req = {"Country", "Installed_kW"}
                if not req.issubset(set(bess_df.columns)):
                    print("   ⚠ BESS sheet mancano colonne richieste; salto.")
                else:
                    # lista paesi dal foglio BESS_New
                    grp = (bess_df.groupby(["Country"], as_index=False, dropna=False)
                               .agg({"Installed_kW": "sum"}))

                    for _, r in grp.iterrows():
                        country = str(r["Country"])
                        try:
                            installed = float(r["Installed_kW"])
                        except Exception:
                            installed = 0.0

                        techs = _ensure_country_b(country)
                        techs["BESS_New"] = {
                            "constraints": {
                                "energy_cap_min": installed,              # anche se 0
                                "energy_cap_max": float("inf"),           # poi .inf → inf
                                "energy_cap_per_storage_cap_equals": 0.25 # 4h
                            }
                        }

                    out_path = output_dir / "Location_Constraints_BESS.yaml"
                    try:
                        text = yaml.dump(bess_yaml, sort_keys=False, allow_unicode=True, indent=4, width=4096)
                        text = text.replace(".inf", "inf")
                        with open(out_path, "w", encoding="utf-8") as f:
                            f.write(text)
                        print(f"   ✔ Scritto BESS: {out_path}")
                    except Exception as e:
                        print(f"   [ERRORE] Scrittura BESS fallita: {out_path}\n      → {e}")
            # ============================================================================================
            # ================== PHES_New ==================
            phes_df = dfs.get("PHES_New")
            if phes_df is not None:
                # --- Carica i limiti di storage per paese (Excel con: Country, Storage_Max [kWh]) ---
                phes_limits_xlsx_path = r"C:\Users\giorg\Desktop\PoliMi\Tesi\14_HydroPower\PHES_SAPP.xlsx"  # <-- AGGIORNA QUESTO PERCORSO
                phes_storage_cap_max = {}
                try:
                    lim = pd.read_excel(phes_limits_xlsx_path)
                    required_cols = {"Country", "Storage_Max [kWh]"}
                    missing = required_cols - set(lim.columns)
                    if missing:
                        print(f"   ⚠ PHES limits: colonne mancanti {missing} in {phes_limits_xlsx_path}")
                    else:
                        lim = lim[["Country", "Storage_Max [kWh]"]].copy()
                        lim["Country"] = lim["Country"].astype(str).str.strip()
                        # Se ci fossero duplicati per Country, prendiamo il massimo
                        lim = lim.groupby("Country", as_index=False, dropna=False)["Storage_Max [kWh]"].max()
                        for _, rr in lim.iterrows():
                            try:
                                phes_storage_cap_max[str(rr["Country"])] = float(rr["Storage_Max [kWh]"])
                            except Exception:
                                pass
                        print(f"   [OK] PHES limits caricati per {len(phes_storage_cap_max)} paesi.")
                except FileNotFoundError:
                    print(f"   ⚠ PHES limits Excel non trovato: {phes_limits_xlsx_path}")

                phes_yaml = {"locations": {}}

                def _ensure_country_p(country: str):
                    node = phes_yaml["locations"].setdefault(str(country), {})
                    node.setdefault("techs", {})
                    return node["techs"]

                req = {"Country", "Installed_kW"}
                if not req.issubset(set(phes_df.columns)):
                    print("   ⚠ PHES sheet mancano colonne richieste; salto.")
                else:
                    # Sommiamo la potenza installata per paese dal recap
                    grp = (phes_df.groupby(["Country"], as_index=False, dropna=False)
                       .agg({"Installed_kW": "sum"}))

                    for _, r in grp.iterrows():
                        country = str(r["Country"])
                        try:
                            installed = float(r["Installed_kW"])
                        except Exception:
                            installed = 0.0

                        constraints = {
                            "energy_cap_min": installed,                         # kW dal recap
                            "energy_cap_per_storage_cap_equals": 0.16666666667,  # 6h
                        }
                        # storage_cap_max (kWh) per paese, dal file Excel dei limiti
                        max_kwh = phes_storage_cap_max.get(country)
                        if max_kwh is not None:
                            constraints["storage_cap_max"] = max_kwh
                        else:
                            print(f"   ⚠ storage_cap_max mancante per {country} in {phes_limits_xlsx_path}; lo salto.")
            
                        techs = _ensure_country_p(country)
                        techs["PHES_New"] = {"constraints": constraints}

                    out_path = output_dir / "Location_Constraints_PHES.yaml"
                    try:
                        text = yaml.dump(phes_yaml, sort_keys=False, allow_unicode=True, indent=4, width=4096)
                        text = text.replace(".inf", "inf")  # uniforma eventuali 'inf'
                        with open(out_path, "w", encoding="utf-8") as f:
                            f.write(text)
                        print(f"   ✔ Scritto PHES: {out_path}")
                    except Exception as e:
                        print(f"   [ERRORE] Scrittura PHES fallita: {out_path}\n      → {e}")
            # ============================================================================================
            # ================== Transmission (400_kV_New) ==================
            tx_df = dfs.get("400_kV_New")
            if tx_df is not None:
               # --- Excel con le distanze: colonne = Country1, Country2, Distance ---
                tx_distances_xlsx_path = r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\YamlCreation\Transmission.xlsx"  # <-- AGGIORNA QUESTO PERCORSO
                dist_map = {}
                try:
                    dist_df = pd.read_excel(tx_distances_xlsx_path)
                    req_cols = {"Country1", "Country2", "Distance"}
                    if not req_cols.issubset(set(dist_df.columns)):
                        print(f"   ⚠ Transmission distances: colonne mancanti {req_cols - set(dist_df.columns)} in {tx_distances_xlsx_path}")
                        dist_df = None
                except FileNotFoundError:
                    print(f"   ⚠ Transmission distances Excel non trovato: {tx_distances_xlsx_path}")
                    dist_df = None

                def _pair(a, b):
                    a, b = str(a).strip(), str(b).strip()
                    return (a, b) if a <= b else (b, a)

                if dist_df is not None:
                    dist_df = dist_df.copy()
                    dist_df["pair"] = dist_df.apply(lambda r: _pair(r["Country1"], r["Country2"]), axis=1)
                    # Se ci fossero duplicati per la stessa coppia, teniamo il max (supponiamo univoche)
                    dist_grp = dist_df.groupby("pair", as_index=False, dropna=False)["Distance"].max()
                    for _, rr in dist_grp.iterrows():
                        dist_map[rr["pair"]] = float(rr["Distance"])

                # --- build YAML da zero ---
                tx_yaml = {
                    "techs": {
                        "400_kV_New": {
                            "essentials": {
                                "name": "High Voltage Grid 400 kV",
                                "parent": "transmission",
                                "carrier": "electricity",
                                "color": "#000000"
                            },
                            "constraints": {
                                "lifetime": 40
                            },
                            "costs": {
                                "monetary": {
                                    "energy_cap": 17.350,
                                    "energy_cap_per_distance": 40.64,
                                    "om_prod": 0.0076,
                                    "interest_rate": 0.10
                                }
                            }
                        }
                    },
                    "links": {}
                }

                # Normalizza e aggrega il recap per coppia non direzionale
                df_tx = tx_df.copy()
                need_cols = {"Country1", "Country2", "Installed Cap [kW]"}
                if not need_cols.issubset(set(df_tx.columns)):
                    print(f"   ⚠ Transmission recap: colonne mancanti {need_cols - set(df_tx.columns)}; salto.")
                else:
                    df_tx["pair"] = df_tx.apply(lambda r: _pair(r["Country1"], r["Country2"]), axis=1)
                    agg = (df_tx.groupby("pair", as_index=False, dropna=False)
                                 .agg({"Installed Cap [kW]": "sum"}))

                    for _, rr in agg.iterrows():
                        a, b = rr["pair"]
                        installed = float(rr["Installed Cap [kW]"]) if pd.notna(rr["Installed Cap [kW]"]) else 0.0
                        link_key = f"{a},{b}"

                        node = {
                            "techs": {
                                "400_kV_New": {
                                    "constraints": {
                                        "energy_cap_min": installed,
                                        "energy_cap_max": "inf",        # stringa 'inf'
                                        "energy_eff_per_distance": 0.995
                                    }
                                }
                            }
                        }
                        # distance se presente nel file distanze
                        d = dist_map.get((a, b))
                        if d is not None:
                            node["techs"]["400_kV_New"]["distance"] = d
                        else:
                            print(f"   ⚠ Distance mancante per {link_key} in {tx_distances_xlsx_path}; la ometto.")

                        tx_yaml["links"][link_key] = node

                    # Scrivi il file con indentazione a 4 spazi
                    out_path = output_dir / "Transmission_links_Free.yaml"
                    try:
                        text = yaml.dump(tx_yaml, sort_keys=False, allow_unicode=True, indent=4, width=4096)
                        with open(out_path, "w", encoding="utf-8") as f:
                            f.write(text)
                        print(f"   ✔ Scritto Transmission: {out_path} (links: {len(tx_yaml['links'])})")
                    except Exception as e:
                        print(f"   [ERRORE] Scrittura Transmission fallita: {out_path}\n      → {e}")
            # =======================================================================
            ##### FINE #####