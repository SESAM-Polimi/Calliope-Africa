#%%
from pathlib import Path
import pandas as pd
import re
#####################################################################################################################################################################
# --- helper: parsing risultati ---
def parse_energy_cap(df_results: pd.DataFrame) -> pd.DataFrame:
    # accetta PV, W o Wind e normalizza a PV/W
    pat = re.compile(r"^(PV|W|Wind)_([A-Z_]+)_MSR(\d+)$")
    rows = []
    for _, row in df_results.iterrows():
        m = pat.match(str(row["techs"]))
        if not m:
            continue
        tech_raw, ctry, msr = m.groups()
        tech_norm = "PV" if tech_raw.upper() == "PV" else "W"  # Wind -> W, W -> W
        rows.append({
            "Country": ctry,
            "Tech": tech_norm,
            "MSR_ID": int(msr),
            "Installed_kW": row["energy_cap"]
        })
    return pd.DataFrame(rows)

def load_clusters_for_tech(clusters_base: Path, countries: list[str], tech: str) -> pd.DataFrame:
    frames = []
    for ctry in countries:
        folder = clusters_base / ctry
        fpath = folder / f"{ctry}_Cluster_Stats_{tech}.xlsx"
        if not fpath.exists():
            print(f"[SKIP] manca: {fpath}")
            continue
        df = pd.read_excel(fpath).copy()
        # normalizza nomi colonne
        rename_map = {
            "ClusterID": "MSR_ID",
            "WeightedLat": "WeightedLat",
            "WeightedLon": "WeightedLon",
            "TotalCapacityMW": "TotalCapacity_MW",
        }
        df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)
        # calcola Max_kW
        if "TotalCapacity_MW" in df.columns:
            df["Max_kW"] = df["TotalCapacity_MW"] * 1000.0
        elif "Max_kW" not in df.columns:
            df["Max_kW"] = pd.NA
        # aggiungi chiavi
        df["Country"] = ctry
        df["Tech"] = tech
        keep = ["Country", "Tech", "MSR_ID", "WeightedLat", "WeightedLon", "Max_kW"]
        frames.append(df[[c for c in keep if c in df.columns]])
    if frames:
        return pd.concat(frames, ignore_index=True)
    else:
        return pd.DataFrame(columns=["Country","Tech","MSR_ID","WeightedLat","WeightedLon","Max_kW"])

# --- helper: normalizza tipi per la chiave di merge ---
def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in ["Country","Tech"]:
        if c in out.columns:
            out[c] = out[c].astype(str).str.upper()
    if "MSR_ID" in out.columns:
        out["MSR_ID"] = pd.to_numeric(out["MSR_ID"], errors="coerce").astype("Int64")
    return out

# --- funzione per riepilogo per paese (tutti gli scenari) ---
def build_country_capacity_sheet(df_results: pd.DataFrame, tech_name: str, countries: list[str]) -> pd.DataFrame:
    if df_results.empty:
        return pd.DataFrame(columns=["Country", "Installed_kW"])

    techs = df_results["techs"].astype(str).str.strip()
    locs  = df_results["locs"].astype(str).str.strip()
    countries_set = set(countries)

    # match esatto (case-insensitive)
    mask_exact = techs.str.upper().eq(tech_name.upper())
    # match con :CTRY o _CTRY (case-insensitive)
    pat = re.compile(rf"^{re.escape(tech_name)}(?:[_:])(?P<ctry>[A-Z_]+)$", re.IGNORECASE)
    mask_suffix = techs.str.match(pat)

    sub = df_results.loc[mask_exact | mask_suffix, ["locs", "techs", "energy_cap"]].copy()
    if sub.empty:
        # fallback: se i nomi sono strani ma contengono il tech_name, tenta un contains con word boundary
        mask_contains = techs.str.contains(rf"\b{re.escape(tech_name)}\b", case=False, regex=True)
        sub = df_results.loc[mask_contains, ["locs", "techs", "energy_cap"]].copy()
        if sub.empty:
            return pd.DataFrame(columns=["Country", "Installed_kW"])

    def _extract_country(tech_str: str, loc_str: str) -> str | None:
        m = pat.match(tech_str)
        if m:
            c = m.group("ctry").upper()
            return c if c in countries_set else None
        # fallback: prova a dedurre da 'locs'
        up = loc_str.upper()
        # caso: loc è esattamente il country
        if up in countries_set:
            return up
        # caso: loc contiene il country come token
        for token in re.findall(r"[A-Z_]+", up):
            if token in countries_set:
                return token
        return None

    sub["Country"] = [ _extract_country(t, l) for t, l in zip(sub["techs"], sub["locs"]) ]
    sub = sub.dropna(subset=["Country"])
    if sub.empty:
        return pd.DataFrame(columns=["Country", "Installed_kW"])

    out = (sub.groupby("Country", as_index=False)
             .agg(Installed_kW=("energy_cap", "sum"))
             .sort_values("Country")
             .reset_index(drop=True))

    # Log diagnostico (utile per capire cosa sta succedendo)
    print(f"    [extra {tech_name}] matched_rows={len(sub)} countries={len(out)} sum_kW={out['Installed_kW'].sum():.0f}")
    return out

# --- NUOVO helper: coppie di paesi per 400_kV_New ---
def build_transmission_pairs_sheet(df_results: pd.DataFrame, tech_name: str, countries: list[str]) -> pd.DataFrame:
    """
    Crea tabella di capacità tra coppie di paesi per una tecnologia di trasmissione (es. 400_kV_New),
    trattando le coppie come non direzionali e SENZA sommare le due direzioni:
    - (AGO, DRC) == (DRC, AGO)
    - si mantiene un solo valore di capacità per coppia.
    Colonne: Country1, Country2, Tech, Installed Cap [kW]
    """
    if df_results.empty:
        return pd.DataFrame(columns=["Country1", "Country2", "Tech", "Installed Cap [kW]"])

    df = df_results.copy()
    df["techs"] = df["techs"].astype(str).str.strip()
    df["locs"]  = df["locs"].astype(str).str.strip()

    countries_set = set(countries)
    # Match: tech_name:CTRY oppure tech_name_CTRY (case-insensitive)
    pat = re.compile(rf"^(?i:{re.escape(tech_name)})(?:[_:])(?P<ctry>[A-Z_]+)$", re.IGNORECASE)

    rows = []
    for loc, tech, cap in zip(df["locs"], df["techs"], df["energy_cap"]):
        m = pat.match(tech)
        if not m:
            continue
        c1 = str(loc).upper()
        c2 = m.group("ctry").upper()
        # escludi self-loop e paesi non nella lista
        if c1 in countries_set and c2 in countries_set and c1 != c2:
            a, b = sorted([c1, c2])  # normalizza (coppia non direzionale)
            rows.append({
                "Country1": a,
                "Country2": b,
                "Tech": tech_name,
                "Installed Cap [kW]": cap
            })

    if not rows:
        return pd.DataFrame(columns=["Country1", "Country2", "Tech", "Installed Cap [kW]"])

    df_pairs = pd.DataFrame(rows)

    # Se la stessa coppia compare due volte (due direzioni) con lo stesso valore, tieni il primo (no somma).
    # Se per qualche motivo i due valori differiscono, emetti un warning e prendi il massimo per quella coppia.
    dup_check = (df_pairs.groupby(["Country1", "Country2", "Tech"])["Installed Cap [kW]"]
                          .nunique() > 1)
    inconsistent = int(dup_check.sum())
    aggfunc = "first" if inconsistent == 0 else "max"
    if inconsistent:
        print(f"    [WARN] {inconsistent} coppie hanno valori non identici tra direzioni; uso il valore massimo per ciascuna.")

    out = (df_pairs
           .groupby(["Country1", "Country2", "Tech"], as_index=False)
           .agg(**{"Installed Cap [kW]": ("Installed Cap [kW]", aggfunc)})
           .sort_values(["Country1", "Country2"])
           .reset_index(drop=True))

    print(f"    [Transmission pairs (undirected, no-sum) {tech_name}] pairs={len(out)}")
    return out

def build_hydro_sheet(df_results: pd.DataFrame, hydro_catalog_path: Path, countries: list[str]) -> pd.DataFrame:
    # 1) leggi catalogo hydro (atteso con colonne: Country, Tech, Lat, Long, Total Capacity [kW])
    cat = pd.read_excel(hydro_catalog_path).copy()
    cat = cat.rename(columns={
        "Total Capacity [kW]": "Total Cap [kW]",
        "Lat": "Lat",
        "Long": "Long",
        "Country": "Country",
        "Tech": "Tech",
    })
    # normalizza chiavi
    cat["Country_up"] = cat["Country"].astype(str).str.upper()
    cat["Tech_up"]    = cat["Tech"].astype(str).str.upper()
    # 2) filtra i risultati per Hydro (case-insensitive, supporta eventuali suffix :CTRY o _CTRY)
    df = df_results.copy()
    df["techs"] = df["techs"].astype(str).str.strip()
    df["locs"]  = df["locs"].astype(str).str.strip()
    # tieni righe che "iniziano con Hydro"
    hydro_mask = df["techs"].str.startswith("Hydro", na=False)
    hyd = df.loc[hydro_mask, ["locs","techs","energy_cap"]].copy()
    if hyd.empty:
        return pd.DataFrame(columns=["Country","Tech","Lat","Long","Installed Cap [kW]","Total Cap [kW]","Saturation_pct"])
    countries_set = set(countries)
    # regex: base = nome sito; suffix opzionale :CTRY o _CTRY (se CTRY è un codice noto lo usiamo, altrimenti ignoriamo)
    # es: 'Hydro_Large_New_1:AGO' -> base=Hydro_Large_New_1, ctry=AGO
    pat = re.compile(r"^(?P<base>Hydro[0-9A-Za-z_]+?)(?:[_:](?P<ctry>[A-Z_]+))?$", re.IGNORECASE)
    def _split_tech_country(t: str) -> tuple[str, str|None]:
        m = pat.match(t)
        if not m:
            return t, None
        base = m.group("base")
        ctry = m.group("ctry")
        if ctry and ctry.upper() in countries_set:
            return base, ctry.upper()
        return base, None
    def _extract_country_from_locs(loc: str) -> str|None:
        up = str(loc).upper()
        if up in countries_set:
            return up
        # prova a trovare un token che combaci con un codice paese
        for token in re.findall(r"[A-Z_]+", up):
            if token in countries_set:
                return token
        return None
    # estrae Tech base e Country
    bases, ctrys = [], []
    for t, l in zip(hyd["techs"], hyd["locs"]):
        base, ctry_suffix = _split_tech_country(t)
        bases.append(base)
        ctrys.append(ctry_suffix if ctry_suffix else _extract_country_from_locs(l))
    hyd["Tech_base"] = pd.Series(bases, index=hyd.index).astype(str)
    hyd["Country"]   = pd.Series(ctrys, index=hyd.index)
    # tieni solo righe con country riconosciuto
    hyd = hyd.dropna(subset=["Country"])
    if hyd.empty:
        return pd.DataFrame(columns=["Country","Tech","Lat","Long","Installed Cap [kW]","Total Cap [kW]","Saturation_pct"])
    # 3) aggrega Installed per (Country, Tech_base); assumo energy_cap già in kW
    hyd["Country_up"] = hyd["Country"].astype(str).str.upper()
    hyd["Tech_up"]    = hyd["Tech_base"].astype(str).str.upper()
    installed = (hyd.groupby(["Country_up","Tech_up"], as_index=False)
                   .agg(**{"Installed Cap [kW]": ("energy_cap", "sum")}))
    # 4) unisci col catalogo Hydro su (Country, Tech) case-insensitive
    merged = pd.merge(
        installed,
        cat[["Country_up","Tech_up","Country","Tech","Lat","Long","Total Cap [kW]"]],
        on=["Country_up","Tech_up"],
        how="inner"  # tieni solo siti presenti nel catalogo
    )
    if merged.empty:
        return pd.DataFrame(columns=["Country","Tech","Lat","Long","Installed Cap [kW]","Total Cap [kW]","Saturation_pct"])
    # 5) calcola saturazione e ordina
    merged["Saturation_pct"] = (merged["Installed Cap [kW]"] / merged["Total Cap [kW]"].replace({0: pd.NA})) * 100.0
    merged = (merged
              .sort_values(["Country","Tech"])
              .reset_index(drop=True)
              [["Country","Tech","Lat","Long","Installed Cap [kW]","Total Cap [kW]","Saturation_pct"]])
    # log sintetico utile
    print(f"    [Hydro] siti con installato: {len(merged)}  somma_kW={merged['Installed Cap [kW]'].sum():.0f}")
    return merged

# --- funzione principale per UN file results_energy_cap (uno scenario) ---
def write_msr_excel_for_scenario(
    results_csv_path: Path,
    clusters_path: Path,
    countries: list[str],
    out_dir: Path,
    scenario_label: str,
    techs=("PV","W"),
    extra_techs=None,
    skip_empty_extra: bool = True,
    hydro_catalog_path: Path | None = None,   # << aggiunto
    add_hydro_if_present: bool = True,        # << aggiunto
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    # 1) leggi risultati e parse (assume energy_cap in kW già coerente)
    res = pd.read_csv(results_csv_path)
    res_parsed = parse_energy_cap(res)
    res_parsed = normalize_keys(res_parsed)
    # (opzionale) somma duplicati
    res_parsed = (res_parsed
                  .groupby(["Country","Tech","MSR_ID"], as_index=False, dropna=False)
                  .agg({"Installed_kW":"sum"}))
    # 2–5) PV/W
    outputs = {}
    for tech in techs:
        clu = load_clusters_for_tech(clusters_path, countries, tech)
        clu = normalize_keys(clu)
        merge = pd.merge(
            res_parsed.loc[res_parsed["Tech"] == tech, ["Country","Tech","MSR_ID","Installed_kW"]],
            clu,
            on=["Country","Tech","MSR_ID"],
            how="inner",
            validate="many_to_one"
        )
        merge["Saturation_pct"] = (merge["Installed_kW"] / merge["Max_kW"].replace({0: pd.NA})) * 100.0
        merge = merge.sort_values(["Country","MSR_ID"]).reset_index(drop=True)
        final_cols = ["Country","MSR_ID","WeightedLat","WeightedLon","Installed_kW","Max_kW","Saturation_pct"]
        outputs[tech] = merge[[c for c in final_cols if c in merge.columns]]
    # 6) scrivi Excel (PV/W + extra)
    out_file = out_dir / f"{scenario_label}_Recap.xlsx"
    if extra_techs is None:
        extra_techs = []
    # costruisci fogli extra (solo se con dati quando skip_empty_extra=True)
    extra_sheets = {}
    for extra in extra_techs:
        if extra.upper() == "400_KV_NEW":
            df_extra = build_transmission_pairs_sheet(res, extra, countries)
            if df_extra.empty and skip_empty_extra:
                print(f"    [skip sheet] {extra}: nessun dato")
                continue
            if df_extra.empty:  # se vuoi comunque il foglio con header
                df_extra = pd.DataFrame(columns=["Country1", "Country2", "Tech", "Installed Cap [kW]"])
        else:
            df_extra = build_country_capacity_sheet(res, extra, countries)
            if df_extra.empty and skip_empty_extra:
                print(f"    [skip sheet] {extra}: nessun dato")
                continue
            if df_extra.empty:  # header standard per extra non-transmission
                df_extra = pd.DataFrame(columns=["Country", "Installed_kW"])
        extra_sheets[extra] = df_extra

    hydro_sheet = pd.DataFrame()
    if add_hydro_if_present and hydro_catalog_path is not None and hydro_catalog_path.exists():
        hydro_sheet = build_hydro_sheet(res, hydro_catalog_path, countries)
    
    with pd.ExcelWriter(out_file, engine="openpyxl") as writer:
        for tech in techs:
            df = outputs.get(
                tech,
                pd.DataFrame(columns=["Country","MSR_ID","WeightedLat","WeightedLon","Installed_kW","Max_kW","Saturation_pct"])
            )
            df.to_excel(writer, sheet_name=tech, index=False)

        for name, df in extra_sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
        if not hydro_sheet.empty:
            hydro_sheet.to_excel(writer, sheet_name="Hydro", index=False)

#####################################################################################################################################################################

folder_path = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\20_RESULTS_Calliope")
clusters_path = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\13_FinalClusteringTotalSAPP\4_FINAL_OUTPUT\4Calliope")
out_base = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\EnergyCap\Results")
out_base.mkdir(parents=True, exist_ok=True)
ENERGY_CAP_FILE = "results_energy_cap.csv"
REQUIRED_COLS = {"locs", "techs", "energy_cap"}
Ctry_Code = ["AGO","BWA","DRC","LSO","MOZ_NC","MOZ_S","MWI","NAM","SWZ","TZA","ZAF","ZMB","ZWE"]
Tech_MSR = ["PV","W"]
EXTRA_TECHS = ["BESS_New", "PHES_New", "OCGT_pp_New", "400_kV_New"]
HYDRO_CATALOG = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\14_HydroPower\Hydro_SAPP.xlsx")
group_names = [
    "Autarky",
    # "Existing_Transmission",
    # "Transmission_Expansion",
]
years = [
    "2030",
    "2035",
    "2040",
]
scenario_names = [
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
    "VRES+Hydro4+NG_PHES",
]

for scenario_name in scenario_names:
    print(f"\n=== Scenario: {scenario_name} ===")
    for group in group_names:
        for year in years:
            csv_path = folder_path / group / year / f"Results_{group}_{scenario_name}" / ENERGY_CAP_FILE
            if not csv_path.exists():
                print(f"[SKIP] manca: {csv_path}")
                continue
            label = f"{group}_{year}_{scenario_name}"
            # Validazione veloce colonne richieste
            try:
                sample = pd.read_csv(csv_path, nrows=5)
            except Exception as e:
                print(f"[ERRORE] lettura {csv_path}: {e}")
                continue
            missing = REQUIRED_COLS - set(sample.columns)
            if missing:
                print(f"[SKIP] colonne mancanti in {csv_path.name}: {missing}")
                continue
            out_dir = out_base / group / year
            try:
                out_path = write_msr_excel_for_scenario(
                    results_csv_path=csv_path,
                    clusters_path=clusters_path,
                    countries=Ctry_Code,
                    out_dir=out_dir,
                    scenario_label=label,
                    techs=("PV","W"),
                    extra_techs=EXTRA_TECHS,
                    skip_empty_extra=True,
                    hydro_catalog_path=HYDRO_CATALOG,
                    add_hydro_if_present=True
                    )
                print(f"  -> Creato: {out_path}")
            except Exception as e:
                print(f"[ERRORE] creazione file per {label}: {e}")
                continue
            # (opzionale) riepilogo
            try:
                results_data = pd.read_csv(csv_path)
                print(
                    f"  OK: {csv_path.name}  "
                    f"(righe={len(results_data)}, "
                    f"paesi={results_data['locs'].nunique()}, "
                    f"techs={results_data['techs'].nunique()})"
                )
            except Exception as e:
                print(f"[WARN] riepilogo fallito per {csv_path}: {e}")
