# %%
# -*- coding: utf-8 -*-
"""
Crea GeoPackage per QGIS con layer PV e W per ogni combinazione group/year/scenario,
più file .qml di stile (colore da Saturation e dimensione da Max_MW),
e un Excel di riepilogo unico (fogli: PV, WIND).

Requisiti:
    pip install pandas geopandas shapely fiona openpyxl

Autore: ChatGPT
"""

from pathlib import Path
from typing import List, Tuple, Dict
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# ========================= CONFIG UTENTE (adatta se serve) =========================
# Input
RESULTS_BASE = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\EnergyCap\Results")

GROUPS = ["Autarky", "Existing_Transmission", "Transmission_Expansion"]
YEARS = [2030, 2035, 2040]
SCENARIOS = [
    "VRES_BESS", "VRES_BESS+PHES", "VRES_no_Storage", "VRES_PHES",
    "VRES+Hydro4_BESS", "VRES+Hydro4_BESS+PHES", "VRES+Hydro4_no_Storage", "VRES+Hydro4_PHES",
    "VRES+Hydro4+NG_BESS", "VRES+Hydro4+NG_BESS+PHES", "VRES+Hydro4+NG_no_Storage", "VRES+Hydro4+NG_PHES"
]

# Output
OUT_BASE = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\23_QGIS\SaturationMap")
# Cartelle di lavoro
GPKG_DIRNAME = "GPKG"
QML_DIRNAME = "QML"
RECAP_XLSX = OUT_BASE / "SAPP_Saturation_Recap.xlsx"

# CRS output
CRS_EPSG = 4326  # WGS84

# Nomi fogli nei recap Excel sorgente
PV_SHEET = "PV"
W_SHEET = "W"

# Nomi colonne (come da input)
COLS = {
    "country": "Country",
    "id": "MSR_ID",
    "lat": "WeightedLat",
    "lon": "WeightedLon",
    "installed_kw": "Installed_kW",
    "max_kw": "Max_kW",
    "saturation": "Saturation_pct",   # valori 0–1 già presenti
}

# Classi dimensioni cerchi (mm) in base a Max_MW (bordi inclusi a sinistra, esclusi a destra tranne l'ultimo)
SIZE_CLASS_BINS_MW = [0, 50, 100, 200, 500]  # soglie
SIZE_CLASS_MM = [2.5, 4.0, 5.5, 7.0, 9.0]     # mm corrispondenti alle classi

# Colori saturazione per QGIS (hex) ai punti 0.0, 0.25, 0.5, 0.75, 1.0
SAT_COLORS = {
    0.00: "#BDBDBD",  # grigio
    0.25: "#2ECC71",  # verde
    0.50: "#F4D03F",  # giallo
    0.75: "#E74C3C",  # rosso
    1.00: "#000000"   # nero
}
POINT_OUTLINE_COLOR = "#000000"
POINT_OUTLINE_WIDTH_MM = 0.2

# ==================================================================================


def ensure_dirs(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def build_source_path(group: str, year: int, scenario: str) -> Path:
    """Costruisce il path completo del file Excel di recap."""
    fname = f"{group}_{year}_{scenario}_Recap.xlsx"
    return RESULTS_BASE / group / str(year) / fname


def read_sheet_to_gdf(xlsx_path: Path, sheet_name: str,
                      group: str, year: int, scenario: str) -> gpd.GeoDataFrame:
    """Legge un foglio (PV o W) e restituisce un GeoDataFrame con SOLO i campi:
       Lat, Lon, Max_MW, Saturation_pct (0–1), + geometria (EPSG:4326).
       Saturation viene validata e, se mancante/errata, ricalcolata da Installed/Max.
    """
    if not xlsx_path.exists():
        raise FileNotFoundError(f"File non trovato: {xlsx_path}")

    df = pd.read_excel(xlsx_path, sheet_name=sheet_name, engine="openpyxl")

    # Verifica colonne richieste
    needed = ["country", "id", "lat", "lon", "installed_kw", "max_kw", "saturation"]
    for k in needed:
        col = COLS[k]
        if col not in df.columns:
            raise KeyError(f"Manca la colonna '{col}' nel file {xlsx_path.name} (sheet {sheet_name})")

    # Conversioni numeriche
    installed_kw = pd.to_numeric(df[COLS["installed_kw"]], errors="coerce")
    max_kw       = pd.to_numeric(df[COLS["max_kw"]], errors="coerce")
    lon          = pd.to_numeric(df[COLS["lon"]], errors="coerce")
    lat          = pd.to_numeric(df[COLS["lat"]], errors="coerce")
    sat_raw      = pd.to_numeric(df[COLS["saturation"]], errors="coerce")  # atteso 0..1

    # Calcolo/validazione Max_MW
    max_mw = (max_kw / 1000.0).where(max_kw.notna(), other=pd.NA)

    # Saturation valida se in [0,1]
    sat_valid = sat_raw.where(sat_raw.between(0.0, 1.0, inclusive="both"))

    # Fallback: se sat è NaN o fuori range, ricalcolo da Installed/Max (evita divisione per zero)
    installed_mw = installed_kw / 1000.0
    with pd.option_context("mode.use_inf_as_na", True):
        sat_calc = (installed_mw / max_mw).where((max_mw > 0) & installed_mw.notna() & max_mw.notna())

    saturation = sat_valid.fillna(sat_calc).fillna(0.0).clip(0.0, 1.0).round(4)

    # Geometrie
    geometry = [Point(xy) if pd.notna(xy[0]) and pd.notna(xy[1]) else None for xy in zip(lon, lat)]

    # Costruzione GDF con SOLO i campi richiesti
    gdf = gpd.GeoDataFrame(
        {
            "Lat": lat.astype(float),
            "Lon": lon.astype(float),
            "Max_MW": max_mw.astype(float),
            "Saturation_pct": saturation.astype(float),  # 0..1
        },
        geometry=geometry,
        crs=f"EPSG:{CRS_EPSG}",
    )

    # Elimina righe senza geometria o senza Max_MW
    gdf = gdf[gdf.geometry.notna()].copy()
    gdf = gdf[gdf["Max_MW"].notna()].copy()

    return gdf


def save_layers_to_gpkg(pv_gdf: gpd.GeoDataFrame,
                        w_gdf: gpd.GeoDataFrame,
                        out_gpkg: Path):
    """Salva i layer PV e W nello stesso GPKG."""
    ensure_dirs(out_gpkg.parent)
    # se esiste, sovrascrivi (cancellando file)
    if out_gpkg.exists():
        out_gpkg.unlink()

    pv_gdf.to_file(out_gpkg, layer="PV", driver="GPKG")
    w_gdf.to_file(out_gpkg, layer="WIND", driver="GPKG")


def qml_graduated_saturation_color() -> str:
    """
    QML per layer di punti:
      - dimensione simbolo calcolata da Max_MW (CASE WHEN) in mm
      - colore graduato su Saturation_pct (0..1) con 5 stop: 0, 0.25, 0.5, 0.75, 1.0
    """
    # CASE WHEN su Max_MW per le dimensioni (coerente con SIZE_CLASS_BINS_MW / SIZE_CLASS_MM)
    # Esempio: CASE WHEN "Max_MW" < 50 THEN 2.5 WHEN "Max_MW" < 100 THEN 4 ...
    size_cases = []
    for i, thr in enumerate(SIZE_CLASS_BINS_MW):
        # saltiamo il 1° elemento (0) per costruire condizioni " < thr "
        if i == 0:
            continue
        size_cases.append(f"""WHEN "Max_MW" < {SIZE_CLASS_BINS_MW[i]} THEN {SIZE_CLASS_MM[i-1]}""")
    # ultimo ELSE -> dimensione massima
    size_expr = "CASE " + " ".join(size_cases) + f" ELSE {SIZE_CLASS_MM[-1]} END"

    # Palette saturazione
    sat_classes = [
        (0.0, 0.25, "#BDBDBD"),
        (0.25, 0.50, "#2ECC71"),
        (0.50, 0.75, "#F4D03F"),
        (0.75, 1.00, "#E74C3C"),
        (1.00, 1.00, "#000000"),
    ]

    # Symbol template con data-defined size = size_expr
    symbol_template = f"""
      <symbol type="marker" name="{{name}}">
        <layer pass="0" class="SimpleMarker" enabled="1" locked="0">
          <prop k="name" v="circle"/>
          <prop k="color" v="{{color}}"/>
          <prop k="outline_color" v="{POINT_OUTLINE_COLOR}"/>
          <prop k="outline_width" v="{POINT_OUTLINE_WIDTH_MM}"/>
          <prop k="size" v="4"/>
          <prop k="size_unit" v="MM"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties" type="Map">
                <Option name="size" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="expression" type="QString" value="{size_expr}"/>
                  <Option name="type" type="int" value="3"/>
                </Option>
              </Option>
              <Option name="type" type="int" value="2"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    """

    ranges_xml = []
    for i, (minv, maxv, color) in enumerate(sat_classes, 1):
        name = f"{minv:.2f}–{maxv:.2f}"
        symbol_xml = symbol_template.replace("{name}", f"symbol{i}").replace("{color}", color)
        rng = f"""<range lower="{minv}" upper="{maxv}" symbol="symbol{i}" label="{name}" render="true"/>"""
        ranges_xml.append(symbol_xml + rng)

    qml = f"""<?xml version="1.0" encoding="UTF-8"?>
<qgis version="3.28" styleCategories="Symbology">
  <renderer-v2 attr="Saturation_pct" graduatedMethod="GraduatedColor" type="graduatedSymbol">
    <ranges>
      {''.join(ranges_xml)}
    </ranges>
    <source-symbol>
      <symbol type="marker" name="symbol">
        <layer pass="0" class="SimpleMarker" enabled="1" locked="0">
          <prop k="name" v="circle"/>
          <prop k="color" v="#ffffff"/>
          <prop k="size" v="4"/>
          <prop k="size_unit" v="MM"/>
        </layer>
      </symbol>
    </source-symbol>
    <legend type="default"/>
    <capStyle>square</capStyle>
    <symbollevels enabled="0"/>
    <mode>custom</mode>
    <invertColorRamp>false</invertColorRamp>
  </renderer-v2>
  <layerGeometryType>0</layerGeometryType>
</qgis>
"""
    return qml


def write_qml(qml_text: str, out_path: Path):
    ensure_dirs(out_path.parent)
    out_path.write_text(qml_text, encoding="utf-8")


def main():
    # Prepara cartelle output
    ensure_dirs(OUT_BASE)
    ensure_dirs(OUT_BASE / GPKG_DIRNAME)
    ensure_dirs(OUT_BASE / QML_DIRNAME)

    # Accumulatori per recap finale
    recap_pv_list = []
    recap_w_list = []

    # Pre-costruisci stile QML (uguale per PV e WIND; stesso campo)
    # ⬇️ chiamata aggiornata: la funzione non accetta più parametri
    qml_text = qml_graduated_saturation_color()

    # Loop su tutte le combinazioni
    missing_files = []
    processed = 0

    for group in GROUPS:
        for year in YEARS:
            for scenario in SCENARIOS:
                src = build_source_path(group, year, scenario)
                if not src.exists():
                    missing_files.append(src)
                    continue

                try:
                    pv_gdf = read_sheet_to_gdf(src, PV_SHEET, group, year, scenario)
                    w_gdf = read_sheet_to_gdf(src, W_SHEET, group, year, scenario)
                except Exception as e:
                    print(f"[ERRORE] {src.name}: {e}")
                    continue

                # Salva in GPKG (un file per combinazione, 2 layer)
                out_gpkg = OUT_BASE / GPKG_DIRNAME / group / str(year) / f"{group}_{year}_{scenario}.gpkg"
                save_layers_to_gpkg(pv_gdf, w_gdf, out_gpkg)

                # Salva stili QML (uno per PV e uno per WIND)
                pv_qml = OUT_BASE / QML_DIRNAME / group / str(year) / f"{group}_{year}_{scenario}_PV.qml"
                w_qml  = OUT_BASE / QML_DIRNAME / group / str(year) / f"{group}_{year}_{scenario}_WIND.qml"
                write_qml(qml_text, pv_qml)
                write_qml(qml_text, w_qml)

                # Accumula recap (solo se ti serve ancora)
                pv_recap = pv_gdf.drop(columns="geometry").copy()
                w_recap  = w_gdf.drop(columns="geometry").copy()
                recap_pv_list.append(pv_recap)
                recap_w_list.append(w_recap)

                processed += 1
                print(f"[OK] {group} {year} {scenario} -> {out_gpkg}")

    # Scrivi recap Excel (2 fogli: PV e WIND)
    if recap_pv_list or recap_w_list:
        with pd.ExcelWriter(RECAP_XLSX, engine="openpyxl") as xw:
            if recap_pv_list:
                pd.concat(recap_pv_list, ignore_index=True).to_excel(xw, sheet_name="PV", index=False)
            if recap_w_list:
                pd.concat(recap_w_list, ignore_index=True).to_excel(xw, sheet_name="WIND", index=False)
        print(f"[OK] Riepilogo scritto in: {RECAP_XLSX}")

    # Report file mancanti
    if missing_files:
        print("\n[ATTENZIONE] File mancanti:")
        for p in missing_files:
            print(" -", p)

    print(f"\nCombinazioni processate: {processed} (GPKG con 2 layer + QML)")


if __name__ == "__main__":
    main()

# %% =========================
# SEZIONE HYDRO (solo scenari con "Hydro4") -> Shapefile separati
# ===========================

HYDRO_SHP_DIRNAME = "HYDRO_SHP"
HYDRO_SHEET = "Hydro"

HYDRO_COLS = {
    "country": "Country",
    "tech": "Tech",
    "lat": "Lat",
    "lon": "Long",
    "installed_kw": "Installed Cap [kW]",
    "total_kw": "Total Cap [kW]",
    "saturation_pct": "Saturation_pct",  # già in 0–100
}


def _remove_existing_shapefile(shp_path: Path):
    """Rimuove tutti i file associati a uno shapefile esistente."""
    stem = shp_path.with_suffix("")
    for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg", ".qpj"]:
        f = Path(str(stem) + ext)
        if f.exists():
            try:
                f.unlink()
            except Exception as e:
                print(f"[WARN] Impossibile cancellare {f}: {e}")


def read_hydro_sheet_to_gdf(xlsx_path: Path,
                            group: str, year: int, scenario: str) -> gpd.GeoDataFrame:
    """
    Legge il foglio 'Hydro' e restituisce un GeoDataFrame con:
      Country, Tech, Lat, Lon, Max_MW (Total Cap [kW]/1000), Sat_pct (0..100),
      Hydro_ID e geometria (EPSG:4326).
    """
    if not xlsx_path.exists():
        raise FileNotFoundError(f"File non trovato: {xlsx_path}")

    df = pd.read_excel(xlsx_path, sheet_name=HYDRO_SHEET, engine="openpyxl")

    # Verifica colonne richieste
    needed = list(HYDRO_COLS.values())
    for col in needed:
        if col not in df.columns:
            raise KeyError(f"Manca la colonna '{col}' nel file {xlsx_path.name} (sheet {HYDRO_SHEET})")

    # Conversioni pulite
    country = df[HYDRO_COLS["country"]].astype(str).fillna("")
    tech    = df[HYDRO_COLS["tech"]].astype(str).fillna("")
    lat     = pd.to_numeric(df[HYDRO_COLS["lat"]], errors="coerce")
    lon     = pd.to_numeric(df[HYDRO_COLS["lon"]], errors="coerce")
    inst_kw = pd.to_numeric(df[HYDRO_COLS["installed_kw"]], errors="coerce")
    tot_kw  = pd.to_numeric(df[HYDRO_COLS["total_kw"]], errors="coerce")

    # Saturation già in 0–100, ma puliamo NaN e arrotondiamo ai multipli di 25
    sat_raw = pd.to_numeric(df[HYDRO_COLS["saturation_pct"]], errors="coerce")
    with pd.option_context("mode.use_inf_as_na", True):
        sat_fallback = (inst_kw / tot_kw * 100.0).where((tot_kw > 0) & inst_kw.notna() & tot_kw.notna())
    sat_pct = sat_raw.fillna(sat_fallback).fillna(0.0).clip(0, 100).round()

    # Arrotonda ai multipli di 25 se vicino
    sat_pct = ((sat_pct / 25).round() * 25).clip(0, 100).astype(int)

    # Calcolo capacità massima
    max_mw = (tot_kw / 1000.0).where(tot_kw.notna(), other=pd.NA)

    # Geometria
    geometry = [Point(xy) if pd.notna(xy[0]) and pd.notna(xy[1]) else None for xy in zip(lon, lat)]

    gdf = gpd.GeoDataFrame(
        {
            "Country": country,
            "Tech": tech,
            "Lat": lat,
            "Lon": lon,
            "Max_MW": max_mw.astype(float),
            "Sat_pct": sat_pct.astype(int),
        },
        geometry=geometry,
        crs=f"EPSG:{CRS_EPSG}",
    )

    # Filtra righe valide
    gdf = gdf[gdf.geometry.notna() & gdf["Max_MW"].notna()].copy()

    # ID sintetico
    gdf["Hydro_ID"] = [
        f"HYDRO_{str(c)[:4]}_{str(t)[:6]}_{i+1}"
        for i, (c, t) in enumerate(zip(gdf["Country"], gdf["Tech"]))
    ]

    # Ordine finale
    gdf = gdf[["Hydro_ID", "Country", "Tech", "Lat", "Lon", "Max_MW", "Sat_pct", "geometry"]]
    return gdf


def save_hydro_to_shp(hydro_gdf: gpd.GeoDataFrame, out_shp: Path):
    """Salva il layer Hydro in ESRI Shapefile."""
    ensure_dirs(out_shp.parent)
    _remove_existing_shapefile(out_shp)
    hydro_gdf.to_file(out_shp, driver="ESRI Shapefile", encoding="utf-8")


#  =========================
# RUN SOLO HYDRO
# =========================

def main_hydro():
    ensure_dirs(OUT_BASE)
    ensure_dirs(OUT_BASE / HYDRO_SHP_DIRNAME)

    missing_files = []
    processed = 0

    for group in GROUPS:
        for year in YEARS:
            for scenario in SCENARIOS:
                if "Hydro4" not in scenario:
                    continue

                src = build_source_path(group, year, scenario)
                if not src.exists():
                    missing_files.append(src)
                    continue

                try:
                    hydro_gdf = read_hydro_sheet_to_gdf(src, group, year, scenario)
                    out_shp = OUT_BASE / HYDRO_SHP_DIRNAME / group / str(year) / f"{group}_{year}_{scenario}_HYDRO.shp"
                    save_hydro_to_shp(hydro_gdf, out_shp)
                    processed += 1
                    print(f"[OK][HYDRO] {group} {year} {scenario} -> {out_shp}")
                except Exception as e:
                    print(f"[ERRORE][HYDRO] {src.name}: {e}")

    if missing_files:
        print("\n[ATTENZIONE][HYDRO] File mancanti:")
        for p in missing_files:
            print(" -", p)

    print(f"\nCombinazioni HYDRO processate: {processed} (solo shapefile)")


if __name__ == "__main__":
    main_hydro()

# %%
