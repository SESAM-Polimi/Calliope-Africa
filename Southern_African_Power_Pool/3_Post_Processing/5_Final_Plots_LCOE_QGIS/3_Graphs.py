# %%
# =========================
# SEZIONE 1 — LIBRERIE
# =========================
from pathlib import Path
from typing import Dict, List, Tuple
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# (opzionale) render più nitido
plt.rcParams["figure.dpi"] = 130
plt.rcParams["savefig.dpi"] = 220


# %%
# ================================================
# SEZIONE 2 — CONFIG: percorsi, scenari, colori
# ================================================
# --- PERCORSI (ADATTA QUI SE SERVE) ---
RESULTS_BASE = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\20_RESULTS_Calliope")
RECAP_BASE   = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\EnergyCap\Results")
OUT_BASE     = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\PLOTS")

# --- INSIEMI DI RIFERIMENTO ---
COUNTRY_CODE = ['AGO','BWA','DRC','LSO','MOZ_NC','MOZ_S','MWI','NAM','SWZ','TZA','ZAF','ZMB','ZWE', 'MOZ', 'SAPP']

GROUP_NAMES = [
    'Autarky',
    'Existing_Transmission',
    'Transmission_Expansion'
]
YEARS = ['2030','2035','2040']
SCENARIO_NAMES = [
    'VRES_no_Storage',
    'VRES_BESS',
    'VRES_PHES',
    'VRES_BESS+PHES',
    'VRES+Hydro4_no_Storage',
    'VRES+Hydro4_BESS',
    'VRES+Hydro4_PHES',
    'VRES+Hydro4_BESS+PHES',
    'VRES+Hydro4+NG_no_Storage',
    'VRES+Hydro4+NG_BESS',
    'VRES+Hydro4+NG_PHES',
    'VRES+Hydro4+NG_BESS+PHES'
]

# --- MAPPATURA SCENARI → (MACRO, SUB) ---
SCENARIO_TO_MACRO: Dict[str, Tuple[str,str]] = {
    'VRES_no_Storage'                : ('VRES', 'N'),
    'VRES_BESS'                      : ('VRES', 'B'),
    'VRES_PHES'                      : ('VRES', 'P'),
    'VRES_BESS+PHES'                 : ('VRES', 'B+P'),

    'VRES+Hydro4_no_Storage'         : ('VRES+Hydro', 'N'),
    'VRES+Hydro4_BESS'               : ('VRES+Hydro', 'B'),
    'VRES+Hydro4_PHES'               : ('VRES+Hydro', 'P'),
    'VRES+Hydro4_BESS+PHES'          : ('VRES+Hydro', 'B+P'),

    'VRES+Hydro4+NG_no_Storage'      : ('VRES+Hydro+NG', 'N'),
    'VRES+Hydro4+NG_BESS'            : ('VRES+Hydro+NG', 'B'),
    'VRES+Hydro4+NG_PHES'            : ('VRES+Hydro+NG', 'P'),
    'VRES+Hydro4+NG_BESS+PHES'       : ('VRES+Hydro+NG', 'B+P'),
}
MACROS = ['VRES','VRES+Hydro','VRES+Hydro+NG']
SUBS   = ['N','B','P','B+P']

# --- TECNOLOGIE (ordine in legenda/stack) ---
# NB: qui usiamo i nomi “post-processing” coerenti con i tuoi altri file
ORDER_TECHS = ["PV_New", "W_New", "Hydro_New", "OCGT_New"]

# --- COLORI per tecnologia (puoi cambiarli come vuoi) ---
TECH_COLORS: Dict[str, str] = {
    "PV_New"           : "#EFF463",  # giallo
    "W_New"            : "#52AF6C",  # verde acceso
    "Hydro_New"        : "#38B0FF",  # blu acceso
    "OCGT_New"         : "#C300FF",  # Viola Scuro
    "BESS_New"         : "#FEB3F2",  # rosa chiaro
    "PHES_New"         : "#B4E1FA",  # celeste
    "Transmission_New" : "#770000",  # rosso scuro
}


# %%
# ======================================================================================
# SEZIONE 3 — CAPACITÀ [GW] e GRAFICO (3 blocchi × 4 sotto-scenari) — VERSIONE FINALE
# ======================================================================================

# ---------- Loader: dai tuoi *_Recap.xlsx ----------
def _read_capacity_from_recap(group: str, year: str, scenario: str) -> pd.DataFrame:
    f = RECAP_BASE / group / year / f"{group}_{year}_{scenario}_Recap.xlsx"
    if not f.exists():
        return pd.DataFrame(columns=["tech_std", "cap_GW"])

    xl = pd.read_excel(f, sheet_name=None, engine="openpyxl")
    rows = []

    # PV
    if "PV" in xl and "Installed_kW" in xl["PV"].columns:
        rows.append(("PV_New", float(xl["PV"]["Installed_kW"].sum()) / 1e6))

    # W / Wind
    if "W" in xl and "Installed_kW" in xl["W"].columns:
        rows.append(("W_New", float(xl["W"]["Installed_kW"].sum()) / 1e6))

    # Hydro (sheet “Hydro” con “Installed Cap [kW]”)
    if "Hydro" in xl and "Installed Cap [kW]" in xl["Hydro"].columns:
        rows.append(("Hydro_New", float(xl["Hydro"]["Installed Cap [kW]"].sum()) / 1e6))

    # Extra sheets
    extra_map = {
        "BESS_New": "BESS_New",
        "PHES_New": "PHES_New",
        "OCGT_pp_New": "OCGT_New",
        "400_kV_New": "Transmission_New",
    }
    for sh, tech_std in extra_map.items():
        if sh not in xl:
            continue
        df = xl[sh]
        kW_col = "Installed_kW" if "Installed_kW" in df.columns else ("Installed Cap [kW]" if "Installed Cap [kW]" in df.columns else None)
        if kW_col:
            rows.append((tech_std, float(df[kW_col].sum()) / 1e6))

    if not rows:
        return pd.DataFrame(columns=["tech_std", "cap_GW"])

    return (pd.DataFrame(rows, columns=["tech_std", "cap_GW"])
              .groupby("tech_std", as_index=False)["cap_GW"].sum())

# ---------- Fallback: dai results_energy_cap.csv ----------
def _read_capacity_from_csv(group: str, year: str, scenario: str) -> pd.DataFrame:
    csvp = RESULTS_BASE / group / year / f"Results_{group}_{scenario}" / "results_energy_cap.csv"
    if not csvp.exists():
        return pd.DataFrame(columns=["tech_std", "cap_GW"])

    df = pd.read_csv(csvp, low_memory=False)
    df["techs"] = df["techs"].astype(str)
    df["locs"] = df["locs"].astype(str)

    rows = []
    # PV / W MSR
    pv_mask = df["techs"].str.match(r"^PV_[A-Z_]+_MSR\d+$", na=False)
    if pv_mask.any():
        rows.append(("PV_New", float(df.loc[pv_mask, "energy_cap"].sum()) / 1e6))

    w_mask = df["techs"].str.match(r"^(W|Wind)_[A-Z_]+_MSR\d+$", na=False)
    if w_mask.any():
        rows.append(("W_New", float(df.loc[w_mask, "energy_cap"].sum()) / 1e6))

    # Hydro
    hyd_mask = df["techs"].str.match(r"^Hydro_Large_New", na=False)
    if hyd_mask.any():
        rows.append(("Hydro_New", float(df.loc[hyd_mask, "energy_cap"].sum()) / 1e6))

    # OCGT / BESS / PHES
    if (df["techs"] == "OCGT_pp_New").any():
        rows.append(("OCGT_New", float(df.loc[df["techs"] == "OCGT_pp_New", "energy_cap"].sum()) / 1e6))
    if (df["techs"] == "BESS_New").any():
        rows.append(("BESS_New", float(df.loc[df["techs"] == "BESS_New", "energy_cap"].sum()) / 1e6))
    if (df["techs"] == "PHES_New").any():
        rows.append(("PHES_New", float(df.loc[df["techs"] == "PHES_New", "energy_cap"].sum()) / 1e6))

    # Transmission: coppie non direzionali (media tra direzioni)
    tx_mask = df["techs"].str.match(r"^400_kV_New[:_][A-Z_]+$", na=False)
    if tx_mask.any():
        tx = df.loc[tx_mask, ["locs", "techs", "energy_cap"]].copy()
        tx["peer"] = tx["techs"].str.split("[:_]", n=1, expand=True)[1]
        uv = np.sort(tx[["locs", "peer"]].to_numpy(), axis=1)
        tx["u"], tx["v"] = uv[:, 0], uv[:, 1]
        edges = tx.groupby(["u", "v"], as_index=False)["energy_cap"].mean()
        rows.append(("Transmission_New", float(edges["energy_cap"].sum()) / 1e6))

    if not rows:
        return pd.DataFrame(columns=["tech_std", "cap_GW"])

    return (pd.DataFrame(rows, columns=["tech_std", "cap_GW"])
              .groupby("tech_std", as_index=False)["cap_GW"].sum())

# ---------- Build combined capacity table ----------
def build_capacity_from_recaps(
    recap_base: Path,
    results_base: Path,
    groups: List[str],
    years: List[str],
    scenarios: List[str],
    countries: List[str],  # firma coerente
    location: str = "SAPP",
) -> pd.DataFrame:
    rows = []
    for g in groups:
        for y in years:
            for sc in scenarios:
                cap = _read_capacity_from_recap(g, y, sc)
                if cap.empty:
                    cap = _read_capacity_from_csv(g, y, sc)
                if cap.empty:
                    continue
                for _, r in cap.iterrows():
                    t = str(r["tech_std"])
                    if t not in ORDER_TECHS:
                        continue
                    rows.append({
                        "group": g, "year": str(y), "scenario": sc,
                        "location": location, "tech": t,
                        "cap_GW": float(r["cap_GW"]),
                    })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["tech"] = pd.Categorical(df["tech"], categories=ORDER_TECHS, ordered=True)
    return df

# ---------- Helper pivot ----------
def _prepare_macro_pivot(df: pd.DataFrame,
                         group: str,
                         year: str,
                         value_col: str,
                         tech_order: List[str],
                         location: str = "SAPP") -> pd.DataFrame:
    sub = df[(df["group"] == group) &
             (df["year"].astype(str) == str(year)) &
             (df["location"] == location)].copy()

    if sub.empty:
        idx = pd.MultiIndex.from_product([MACROS, SUBS, tech_order], names=["macro", "sub", "tech"])
        return pd.DataFrame({value_col: np.zeros(len(idx))}, index=idx).reset_index()

    sub = sub[sub["scenario"].astype(str).isin(SCENARIO_TO_MACRO)].copy()
    if sub.empty:
        idx = pd.MultiIndex.from_product([MACROS, SUBS, tech_order], names=["macro", "sub", "tech"])
        return pd.DataFrame({value_col: np.zeros(len(idx))}, index=idx).reset_index()

    sub[["macro", "sub"]] = sub["scenario"].map(SCENARIO_TO_MACRO).apply(pd.Series)
    idx = pd.MultiIndex.from_product([MACROS, SUBS, tech_order], names=["macro", "sub", "tech"])
    agg = (sub.groupby(["macro", "sub", "tech"], observed=True)[value_col]
             .sum(min_count=1)
             .reindex(idx, fill_value=0.0)
             .reset_index())
    return agg

# ---------- Parametri grafici ----------
EXISTING_CAP_GW = 58.494  # baseline
TECH_LABEL = {
    "PV_New": "PV",
    "W_New": "Wind",
    "Hydro_New": "Hydro",
    "OCGT_New": "OCGT",
    "Transmission_New": "Transmission",
    "BESS_New": "BESS",
    "PHES_New": "PHES",
}
EXCLUDE_THIS_PLOT: set[str] = {"BESS_New", "PHES_New","Transmission_New"}

def compute_group_ymax(df: pd.DataFrame,
                       group: str,
                       include_tx: bool,
                       value_col: str = "cap_GW") -> float:
    """Calcola limite Y per gruppo."""
    if df.empty:
        return 100.0

    d = df.copy()
    d = d[(d["group"] == group) & (d["scenario"].astype(str).isin(SCENARIO_TO_MACRO))]
    if d.empty:
        return 100.0

    if not include_tx:
        d = d[d["tech"] != "Transmission_New"]

    d[["macro", "sub"]] = d["scenario"].map(SCENARIO_TO_MACRO).apply(pd.Series)
    totals = (d.groupby(["year", "macro", "sub"], observed=True)[value_col]
                .sum(min_count=1)
                .reset_index())

    if totals.empty:
        return 100.0

    ymax = float(totals[value_col].max()) + EXISTING_CAP_GW
    return ymax * 1.10

# ---------- Funzione di plotting ----------
def _plot_macro_stacked_capacity(ax: plt.Axes,
                                 data: pd.DataFrame,
                                 value_col: str = "cap_GW",
                                 tech_order: List[str] = None,
                                 title: str = "",
                                 ylabel: str = "Installed capacity [GW]",
                                 show_transmission: bool = True,
                                 bar_width: float = 0.18,
                                 gap_macro: float = 0.70,
                                 colors: Dict[str, str] = None,
                                 ymax_fixed: float | None = None):
    tech_order = tech_order or ORDER_TECHS
    colors = colors or TECH_COLORS

    techs_to_plot = [t for t in tech_order if t not in EXCLUDE_THIS_PLOT]
    if not show_transmission:
        techs_to_plot = [t for t in techs_to_plot if t != "Transmission_New"]

    x_positions, x_labels = [], []
    for i_macro, macro in enumerate(MACROS):
        base = i_macro * (4 * bar_width + gap_macro)
        for j, sublab in enumerate(SUBS):
            x_positions.append(base + j * bar_width)
            x_labels.append((macro, sublab))

    for i, (macro, sublab) in enumerate(zip([m for m in MACROS for _ in SUBS], SUBS * len(MACROS))):
        bottom = 0.0
        ax.bar(x_positions[i], EXISTING_CAP_GW, width=bar_width * 0.92,
               bottom=bottom, color="#bdbdbd", edgecolor="none",
               label="Existing" if i == 0 else None)
        bottom += EXISTING_CAP_GW

        dbar = data[(data["macro"] == macro) & (data["sub"] == sublab)]
        for t in techs_to_plot:
            val = float(dbar.loc[dbar["tech"] == t, value_col].sum()) if not dbar.empty else 0.0
            if val <= 0:
                continue
            ax.bar(x_positions[i], val, width=bar_width * 0.92, bottom=bottom,
                   color=colors.get(t, "#999999"), edgecolor="none",
                   label=TECH_LABEL.get(t, t) if i == 0 else None)
            bottom += val

    if ymax_fixed is not None:
        ax.set_ylim(0, ymax_fixed * 1.08)  # aggiunge 8% di spazio extra sopra
        ymax = ymax_fixed * 1.08
    else:
        _, ymax = ax.get_ylim()
        ax.set_ylim(0, ymax * 1.25)  # più spazio se non fisso


    ax.set_title(title, pad=12)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.6)
    ax.set_xticks(x_positions)
    ax.set_xticklabels([lbl for (_, lbl) in x_labels])
    ax.tick_params(axis="x", labelsize=10)

    ax_ymax = ax.get_ylim()[1]
    for i_macro, macro in enumerate(MACROS):
        left = i_macro * (4 * bar_width + gap_macro)
        right = left + 3 * bar_width
        center = (left + right) / 2.0
        ax.text(center, -ax_ymax * 0.07, macro, ha="center", va="top",
                fontsize=12, fontweight="bold", transform=ax.transData)

# ---------- Plot per gruppo ----------
def plot_capacity_by_group(capacity_df: pd.DataFrame,
                           out_dir: Path,
                           groups: List[str] = GROUP_NAMES,
                           years: List[str] = YEARS,
                           tech_order: List[str] = ORDER_TECHS,
                           location: str = "SAPP"):

    base = Path(out_dir) / "capacity"
    base.mkdir(parents=True, exist_ok=True)

    for g in groups:
        gdir = base / g
        gdir.mkdir(parents=True, exist_ok=True)

        show_tx_for_group = (g == "Transmission_Expansion")
        ymax_group = compute_group_ymax(capacity_df, group=g, include_tx=show_tx_for_group)

        for yr in years:
            agg = _prepare_macro_pivot(capacity_df, group=g, year=yr,
                                       value_col="cap_GW", tech_order=tech_order,
                                       location=location)

            fig, ax = plt.subplots(figsize=(12.5, 6.8))
            _plot_macro_stacked_capacity(
                ax, agg, value_col="cap_GW",
                tech_order=tech_order, ylabel="Installed capacity [GW]",
                title=f"{g} — {yr}", colors=TECH_COLORS,
                show_transmission=show_tx_for_group,
                ymax_fixed=ymax_group
            )

            # spazio extra in alto per le legende
            fig.subplots_adjust(top=0.95, bottom=0.22, left=0.08, right=0.98)

            # legenda tecnologie (senza bordo)
            handles = [Patch(facecolor="#bdbdbd", edgecolor="none", label="Existing")]
            for t in tech_order:
                if not show_tx_for_group and t == "Transmission_New":
                    continue
                handles.append(Patch(facecolor=TECH_COLORS.get(t, "#999999"),
                                     edgecolor="none",
                                     label=TECH_LABEL.get(t, t)))
            labels = [h.get_label() for h in handles]
            leg1 = ax.legend(handles=handles, labels=labels,
                             ncol=min(5, len(handles)),
                             loc="upper left", bbox_to_anchor=(0.0, 0.99),
                             frameon=False, fontsize=10)

            # mini-leggenda N/B/P/B+P
            sublabels = ['N = NoStorage', 'B = BESS', 'P = PHES', 'B+P = BESS+PHES']
            dummy = [Patch(facecolor="none", edgecolor="none", label=s) for s in sublabels]
            leg2 = ax.legend(handles=dummy, labels=[d.get_label() for d in dummy],
                             loc="upper right", bbox_to_anchor=(1.0, 0.99),
                             frameon=False, fontsize=10)
            ax.add_artist(leg1)

            out_path = gdir / f"{g}_{yr}_capacity.png"
            fig.savefig(out_path, dpi=220, bbox_inches="tight")
            plt.close(fig)

# ===== ESECUZIONE =====
capacity_df = build_capacity_from_recaps(
    recap_base=RECAP_BASE,
    results_base=RESULTS_BASE,
    groups=GROUP_NAMES,
    years=YEARS,
    scenarios=SCENARIO_NAMES,
    countries=COUNTRY_CODE,
    location="SAPP",
)
OUT_BASE.mkdir(parents=True, exist_ok=True)
plot_capacity_by_group(capacity_df, out_dir=OUT_BASE, location="SAPP")


# %% ============================================================================
# SEZIONE 4 — STORAGE: build dataframe (BESS_New + PHES_New)
# ==============================================================================

STORAGE_TECHS = ["BESS_New", "PHES_New"]
STORAGE_LABEL = {"BESS_New": "BESS", "PHES_New": "PHES"}
ORDER_SUBS_WITH_STORAGE = ["B", "P", "B+P"]
STORAGE_SCENARIOS = [s for s in SCENARIO_NAMES if SCENARIO_TO_MACRO[s][1] != "N"]

def build_storage_capacity_from_recaps(
    recap_base: Path,
    results_base: Path,
    groups: List[str],
    years: List[str],
    scenarios: List[str],
    location: str = "SAPP",
) -> pd.DataFrame:
    rows = []
    for g in groups:
        for y in years:
            for sc in scenarios:
                if sc not in SCENARIO_TO_MACRO:
                    continue
                macro, sub = SCENARIO_TO_MACRO[sc]
                if sub == "N":
                    continue  # no storage

                cap = _read_capacity_from_recap(g, y, sc)
                if cap.empty:
                    cap = _read_capacity_from_csv(g, y, sc)
                if cap.empty:
                    # registra zeri per coerenza
                    for t in STORAGE_TECHS:
                        rows.append({"group": g, "year": str(y), "scenario": sc,
                                     "macro": macro, "sub": sub, "location": location,
                                     "tech": t, "cap_GW": 0.0})
                    continue

                subcap = cap[cap["tech_std"].isin(STORAGE_TECHS)].copy()
                have = set(subcap["tech_std"])
                for _, r in subcap.iterrows():
                    rows.append({"group": g, "year": str(y), "scenario": sc,
                                 "macro": macro, "sub": sub, "location": location,
                                 "tech": str(r["tech_std"]), "cap_GW": float(r["cap_GW"])})
                for t in (set(STORAGE_TECHS) - have):
                    rows.append({"group": g, "year": str(y), "scenario": sc,
                                 "macro": macro, "sub": sub, "location": location,
                                 "tech": t, "cap_GW": 0.0})

    df = pd.DataFrame(rows)
    if not df.empty:
        df["tech"] = pd.Categorical(df["tech"], categories=STORAGE_TECHS, ordered=True)
    return df


def _prepare_storage_pivot(df: pd.DataFrame,
                           group: str,
                           year: str,
                           location: str = "SAPP") -> pd.DataFrame:
    subdf = df[(df["group"] == group) &
               (df["year"].astype(str) == str(year)) &
               (df["location"] == location)].copy()
    if subdf.empty:
        return pd.DataFrame(columns=["macro", "sub", "scenario", "tech", "cap_GW"])

    subdf = subdf[subdf["scenario"].isin(STORAGE_SCENARIOS)].copy()
    subdf["sub"] = pd.Categorical(subdf["sub"],
                                  categories=ORDER_SUBS_WITH_STORAGE,
                                  ordered=True)
    subdf.sort_values(by=["macro", "sub", "scenario", "tech"], inplace=True)

    agg = (subdf.groupby(["macro", "sub", "scenario", "tech"], observed=True)["cap_GW"]
                 .sum(min_count=1)
                 .reset_index())
    return agg

# ============================================================================
# Limite Y fisso per tutti gli anni (per group)
# ==============================================================================

def compute_storage_ymax(storage_df: pd.DataFrame, group: str, location: str = "SAPP") -> float:
    """
    Ritorna un limite Y "comune" per tutte le figure di un dato group,
    basato sul massimo (BESS+PHES) tra TUTTI gli anni/scenari/macros.
    Applica un margine e arrotonda al multiplo di 5 GW.
    """
    d = storage_df[(storage_df["group"] == group) & (storage_df["location"] == location)]
    if d.empty:
        return 10.0
    # totale per barra (somma BESS+PHES) su ogni year/macro/sub/scenario
    tot = (d.groupby(["year", "macro", "sub", "scenario"], observed=True)["cap_GW"]
             .sum(min_count=1)
             .reset_index())
    if tot.empty:
        return 10.0
    ymax = float(tot["cap_GW"].max())
    ymax *= 1.12  # padding
    # arrotonda verso l'alto al multiplo di 5 GW
    nice = float(np.ceil(max(ymax, 1.0) / 5.0) * 5.0)
    return nice


#  ============================================================================
# STACKED (BESS sotto, PHES sopra) con lettere sui tick — versione con ymax fisso
# ==============================================================================

def plot_storage_capacity_by_group(storage_df: pd.DataFrame,
                                                 out_dir: Path,
                                                 groups: List[str] = GROUP_NAMES,
                                                 years: List[str] = YEARS,
                                                 location: str = "SAPP",
                                                 bar_width: float = 0.52,
                                                 gap_macro: float = 1.00,
                                                 ymax_fixed: float | None = None):
    """
    Barre stacked (BESS sotto, PHES sopra), con etichette B/P/B+P sui tick centrati,
    macro-blocchi sotto l'asse e (opzionale) limite Y fisso.
    Se `ymax_fixed` è None, calcola un limite per ogni figura in base ai suoi dati.
    """
    base = Path(out_dir) / "storage_capacity"
    base.mkdir(parents=True, exist_ok=True)

    for g in groups:
        gdir = base / g
        gdir.mkdir(parents=True, exist_ok=True)

        # Se richiesto asse Y fisso, calcolalo una volta per il group
        group_ymax = ymax_fixed
        if group_ymax is None:
            group_ymax = compute_storage_ymax(storage_df, group=g, location=location)

        for yr in years:
            data = _prepare_storage_pivot(storage_df, group=g, year=yr, location=location)
            fig, ax = plt.subplots(figsize=(12.5, 6.2))

            if data.empty:
                ax.text(0.5, 0.5, "No storage data available",
                        ha="center", va="center", fontsize=12, transform=ax.transAxes)
                ax.set_axis_off()
                out_path = gdir / f"{g}_{yr}_storage_capacity.png"
                fig.savefig(out_path, dpi=220, bbox_inches="tight")
                plt.close(fig)
                continue

            # Posizioni: una barra per scenario (ordine B, P, B+P) in ogni macro
            x_centers, x_labels = [], []       # [(macro, sub)]
            bars = []                          # (x, b_val, p_val)
            x_cursor = 0.0

            for macro in MACROS:
                subset = data[data["macro"] == macro].copy()
                if subset.empty:
                    x_cursor += gap_macro
                    continue

                subset["sub"] = pd.Categorical(subset["sub"],
                                               categories=["B", "P", "B+P"], ordered=True)
                scen_order = (subset[["scenario", "sub"]]
                              .drop_duplicates()
                              .sort_values(by="sub"))

                for _, row in scen_order.iterrows():
                    sc = row["scenario"]; sublab = row["sub"]
                    b_val = float(subset.loc[(subset["scenario"] == sc) &
                                             (subset["tech"] == "BESS_New"), "cap_GW"].sum())
                    p_val = float(subset.loc[(subset["scenario"] == sc) &
                                             (subset["tech"] == "PHES_New"), "cap_GW"].sum())

                    x = x_cursor
                    bars.append((x, b_val, p_val))
                    x_centers.append(x)
                    x_labels.append((macro, sublab))
                    x_cursor += bar_width + 0.25  # spazio tra scenari

                x_cursor += gap_macro  # spazio tra macro-blocchi

            # Disegno barre stacked (BESS sotto, PHES sopra)
            legend_done = {"BESS": False, "PHES": False}
            for x, b_val, p_val in bars:
                bottom = 0.0
                if b_val > 0:
                    ax.bar(x, b_val, width=bar_width,
                           color=TECH_COLORS.get("BESS_New", "#999999"),
                           edgecolor="none",
                           label=None if legend_done["BESS"] else "BESS")
                    legend_done["BESS"] = True
                    bottom += b_val
                if p_val > 0:
                    ax.bar(x, p_val, width=bar_width, bottom=bottom,
                           color=TECH_COLORS.get("PHES_New", "#999999"),
                           edgecolor="none",
                           label=None if legend_done["PHES"] else "PHES")
                    legend_done["PHES"] = True

            # Legenda
            handles = [Patch(facecolor=TECH_COLORS.get("BESS_New", "#999999"), edgecolor="none", label="BESS"),
                       Patch(facecolor=TECH_COLORS.get("PHES_New", "#999999"), edgecolor="none", label="PHES")]
            ax.legend(handles=handles, ncol=2, loc="upper left", bbox_to_anchor=(0.0, 1.02),
                      frameon=False, fontsize=10)

            # Look & feel
            ax.set_title(f"{g} — {yr} | Storage capacity (GW) — Stacked", pad=12)
            ax.set_ylabel("Installed storage capacity [GW]")
            ax.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.6)

            # Ticks sotto l'asse: lettere B / P / B+P centrate
            if x_centers:
                ax.set_xticks(x_centers)
                ax.set_xticklabels([sublab for (_, sublab) in x_labels], fontsize=11, fontweight="bold")
                ax.tick_params(axis="x", length=0)
            else:
                ax.set_xticks([])

            # ===== Limite Y fisso =====
            ax.set_ylim(0.0, group_ymax)

            # Macro-blocchi sotto l'asse
            ymin, ymax = ax.get_ylim()
            text_y = ymin - (ymax - ymin) * 0.12
            if x_centers:
                i = 0
                while i < len(x_centers):
                    macro = x_labels[i][0]
                    j = i
                    while j < len(x_centers) and x_labels[j][0] == macro:
                        j += 1
                    left = x_centers[i] - bar_width * 0.6
                    right = x_centers[j-1] + bar_width * 0.6
                    center = (left + right) / 2.0
                    ax.text(center, text_y, macro, ha="center", va="top",
                            fontsize=12, fontweight="bold", transform=ax.transData)
                    i = j
                fig.subplots_adjust(bottom=0.24)
            else:
                fig.subplots_adjust(bottom=0.14)

            out_path = gdir / f"{g}_{yr}_storage_capacity.png"
            fig.savefig(out_path, dpi=220, bbox_inches="tight")
            plt.close(fig)


# ===== ESECUZIONE STORAGE: costruzione dataframe =====
storage_capacity_df = build_storage_capacity_from_recaps(
    recap_base=RECAP_BASE,
    results_base=RESULTS_BASE,
    groups=GROUP_NAMES,
    years=YEARS,
    scenarios=SCENARIO_NAMES,
    location="SAPP",
)

# (opzionale, utile in IDE): verifica che esista
assert not storage_capacity_df.empty, "storage_capacity_df è vuoto: controlla i percorsi ai Recap/CSV."

# %% ============================================================================
# SEZIONE 5 — GENERATION SHARE [%] (stacked per fonte, usando i file già elaborati)
# ==============================================================================

import math

# Etichette per legenda tecnologie
TECH_LABEL = {
    "PV_New": "PV",
    "W_New": "Wind",
    "Hydro_New": "Hydro",
    "OCGT_New": "Gas",
    "Coal_New": "Coal",
    "Nuclear_New": "Nuclear",
    "Other_New": "Other",
}

# Ordine fonti in stack/leggenda
# (Oil è confluito in Other, quindi non appare più come voce separata)
GEN_PLOT_TECHS = [
    "PV_New", "W_New", "Hydro_New", "OCGT_New",
    "Coal_New", "Nuclear_New",
    "Other_New",
]

# Colori (integro i nuovi)
TECH_COLORS.update({
    "Coal_New":    "#454545",
    "Nuclear_New": "#70FFCA",
    "Other_New":   "#A0A0A0",
})

# Paesi SAPP per fallback SAPP (evito 'MOZ' aggregato e 'SAPP' stesso)
SAPP_COUNTRIES = [c for c in COUNTRY_CODE if c not in {"MOZ", "SAPP"}]

# ---------- percorsi ----------
def _excel_path_for_group(group: str) -> Path:
    base = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\Results")
    return base / group / f"Electricity_Production_BySource_GWh_{group}.xlsx"

# ---------- mapping 'source' -> 'tech' ----------
def _normalize_source_to_techkey(src: str) -> str | None:
    """
    Regole:
      - Escludi: BESS/PHES (storage)
      - Raggruppa in Other_New: CSP, Bioenergy, Geothermal, 'Other', **Oil/Diesel/HFO**
      - Gas -> OCGT_New
      - Tutto il non riconosciuto -> Other_New
    """
    s = str(src).strip().lower()
    s = re.sub(r"\s+", " ", s)

    # esclusi (storage)
    if any(k in s for k in ["bess", "battery", "pumped", "phes", "storage"]):
        return None

    # raggruppati in Other (include anche Oil)
    if any(k in s for k in ["csp", "concentrated solar", "solar thermal",
                            "bio", "biomass", "biogas", "bagasse", "waste",
                            "geothermal", "geotherma", "other",
                            "oil", "diesel", "hfo", "fo", "fuel oil", "lfo"]):
        return "Other_New"

    if any(k in s for k in ["pv", "photovoltaic", "solar"]):
        return "PV_New"
    if s == "w" or "wind" in s:
        return "W_New"
    if any(k in s for k in ["hydro", "hydropower", "hydroelectric", "run of river", "ror"]):
        return "Hydro_New"
    if any(k in s for k in ["natural gas", "ng", "gas", "ocgt", "open cycle", "ccgt", "combined cycle", "gt"]):
        return "OCGT_New"
    if any(k in s for k in ["coal", "lignite", "hard coal"]):
        return "Coal_New"
    if "nuclear" in s:
        return "Nuclear_New"

    return "Other_New"

# ---------- helper: normalizza colonne + forward-fill location (celle unite) ----------
def _prep_df_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    if "location" in out.columns:
        out["location"] = out["location"].astype(str).replace({"": np.nan, "nan": np.nan}).ffill()
        out["location"] = out["location"].astype(str).str.strip()
        out["location_norm"] = out["location"].str.lower()
    if "source" in out.columns:
        out["source"] = out["source"].astype(str).str.strip()
    out.columns = [str(c).strip() for c in out.columns]
    return out

def _aggregate_by_tech(subdf: pd.DataFrame, yr_cols: list[str]) -> pd.DataFrame:
    tmp = subdf.copy()
    tmp["tech"] = tmp["source"].apply(_normalize_source_to_techkey)
    tmp = tmp.dropna(subset=["tech"])
    if tmp.empty:
        return pd.DataFrame(columns=["tech", *yr_cols])
    return tmp.groupby("tech", as_index=False)[yr_cols].sum()

# ---------- LOADER ----------
def _read_genshare_from_excel(group: str,
                              years: list[str],
                              scenarios: list[str],
                              location: str = "SAPP") -> pd.DataFrame:
    """
    Ritorna DF lungo:
      [group, year, scenario, macro, sub, location, tech, gen_GWh, share_pct]
    - Se location == 'SAPP': usa riga SAPP (ffill) o fallback somma paesi.
    - Se location è un Paese: usa solo la sua riga (no fallback).
    """
    xlsx = _excel_path_for_group(group)
    if not xlsx.exists():
        raise FileNotFoundError(f"Excel non trovato per il group {group}: {xlsx}")

    sheets = pd.read_excel(xlsx, sheet_name=None, engine="openpyxl")
    rows = []
    want_sapp = str(location).strip().upper() == "SAPP"

    for sc_name, raw in sheets.items():
        if sc_name not in SCENARIO_TO_MACRO or raw is None or raw.empty:
            continue
        macro, sub = SCENARIO_TO_MACRO[sc_name]
        df = _prep_df_columns(raw)
        if "location" not in df.columns or "source" not in df.columns:
            continue

        yr_cols = [str(y) for y in years if str(y) in df.columns]
        if not yr_cols:
            continue

        agg = pd.DataFrame(columns=["tech", *yr_cols])

        if want_sapp:
            sapp = df[df["location_norm"] == "sapp"].copy()
            if not sapp.empty:
                agg = _aggregate_by_tech(sapp, yr_cols)
            if agg.empty or (set(agg["tech"]) <= {"PV_New"}):
                sel = df[df["location"].isin(SAPP_COUNTRIES)].copy()
                if not sel.empty:
                    agg = _aggregate_by_tech(sel, yr_cols)
        else:
            # singolo Paese
            sel = df[df["location_norm"] == str(location).strip().lower()].copy()
            if not sel.empty:
                agg = _aggregate_by_tech(sel, yr_cols)

        if agg.empty:
            for y in yr_cols:
                for t in GEN_PLOT_TECHS:
                    rows.append({"group": group, "year": str(y), "scenario": sc_name,
                                 "macro": macro, "sub": sub, "location": location,
                                 "tech": t, "gen_GWh": 0.0, "share_pct": 0.0})
            continue

        for y in yr_cols:
            tot = float(agg[y].sum())
            for _, r in agg.iterrows():
                gwh = float(r[y])
                share = (gwh / tot * 100.0) if tot > 0 else 0.0
                rows.append({"group": group, "year": str(y), "scenario": sc_name,
                             "macro": macro, "sub": sub, "location": location,
                             "tech": str(r["tech"]), "gen_GWh": gwh, "share_pct": share})

        present = set(agg["tech"].astype(str))
        for t in (set(GEN_PLOT_TECHS) - present):
            for y in yr_cols:
                rows.append({"group": group, "year": str(y), "scenario": sc_name,
                             "macro": macro, "sub": sub, "location": location,
                             "tech": t, "gen_GWh": 0.0, "share_pct": 0.0})

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.loc[:, ~out.columns.duplicated()].copy()
        out["tech"] = pd.Categorical(out["tech"], categories=GEN_PLOT_TECHS, ordered=True)
    return out

# ---------- prepara dati per plot ----------
def _prepare_genshare_for_plot(gen_df: pd.DataFrame,
                               group: str,
                               year: str,
                               location: str) -> pd.DataFrame:
    sub = gen_df[(gen_df["group"] == group) &
                 (gen_df["year"].astype(str) == str(year)) &
                 (gen_df["location"] == location)].copy()
    if sub.empty:
        idx = pd.MultiIndex.from_product([MACROS, SUBS, GEN_PLOT_TECHS],
                                         names=["macro", "sub", "tech"])
        return pd.DataFrame({"share_pct": np.zeros(len(idx))}, index=idx).reset_index()

    rows = []
    for macro in MACROS:
        for sublab in SUBS:
            gpart = sub[(sub["macro"] == macro) & (sub["sub"] == sublab)].copy()
            if gpart.empty:
                for t in GEN_PLOT_TECHS:
                    rows.append({"macro": macro, "sub": sublab, "tech": t, "share_pct": 0.0})
                continue
            pivot = (gpart.groupby("tech", observed=True)["share_pct"]
                           .sum()
                           .reindex(GEN_PLOT_TECHS, fill_value=0.0))
            tot = float(pivot.sum())
            if tot > 0:
                pivot = pivot / tot * 100.0
            for t, v in pivot.items():
                rows.append({"macro": macro, "sub": sublab, "tech": t, "share_pct": float(v)})
    return pd.DataFrame(rows)

# ---------- plotting ----------
def _plot_macro_stacked_share(ax: plt.Axes,
                              data: pd.DataFrame,
                              value_col: str = "share_pct",
                              tech_order: list[str] = None,
                              title: str = "",
                              ylabel: str = "Generation share [%]",
                              bar_width: float = 0.18,
                              gap_macro: float = 0.70,
                              colors: dict[str, str] = None):
    tech_order = tech_order or GEN_PLOT_TECHS
    colors = colors or TECH_COLORS

    x_positions, x_labels = [], []
    for i_macro, macro in enumerate(MACROS):
        base = i_macro * (4 * bar_width + gap_macro)
        for j, sublab in enumerate(SUBS):
            x_positions.append(base + j * bar_width)
            x_labels.append((macro, sublab))

    for i, (macro, sublab) in enumerate(zip([m for m in MACROS for _ in SUBS], SUBS * len(MACROS))):
        bottom = 0.0
        dbar = data[(data["macro"] == macro) & (data["sub"] == sublab)]
        for t in tech_order:
            val = float(dbar.loc[dbar["tech"] == t, value_col].sum()) if not dbar.empty else 0.0
            if val <= 0:
                continue
            ax.bar(x_positions[i], val, width=bar_width * 0.92, bottom=bottom,
                   color=colors.get(t, "#999999"), edgecolor="none")
            bottom += val

    ax.set_ylim(0, 100)
    ax.set_title(title, pad=12)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.6)
    ax.set_xticks(x_positions)
    ax.set_xticklabels([lbl for (_, lbl) in x_labels])
    ax.tick_params(axis="x", labelsize=10)

    ax_ymax = ax.get_ylim()[1]
    for i_macro, macro in enumerate(MACROS):
        left = i_macro * (4 * bar_width + gap_macro)
        right = left + 3 * bar_width
        center = (left + right) / 2.0
        ax.text(center, -ax_ymax * 0.07, macro, ha="center", va="top",
                fontsize=12, fontweight="bold", transform=ax.transData)

def _add_legends_outside(fig, plot_data: pd.DataFrame, tech_order: list[str]):
    # tech legend in 2 righe bilanciate, alto-sx, fuori dal grafico
    leg_techs = [t for t in tech_order if (plot_data.loc[plot_data["tech"] == t, "share_pct"].sum()) > 0]
    if not leg_techs:
        leg_techs = tech_order
    handles = [Patch(facecolor=TECH_COLORS.get(t, "#999999"),
                     edgecolor="none",
                     label=TECH_LABEL.get(t, t.replace("_New", "").upper()))
               for t in leg_techs]
    ncols = math.ceil(len(handles) / 2)  # due righe quasi eque
    fig.legend(handles=handles,
               ncol=ncols, loc="upper left", bbox_to_anchor=(0.005, 0.985),
               frameon=False, fontsize=10, columnspacing=0.9, handletextpad=0.4)

    # mini-leggenda N/B/P/B+P in alto-destra, fuori
    sublabels = ['N = NoStorage', 'B = BESS', 'P = PHES', 'B+P = BESS+PHES']
    dummy = [Patch(facecolor="none", edgecolor="none", label=s) for s in sublabels]
    fig.legend(handles=dummy,
               loc="upper right", bbox_to_anchor=(0.995, 0.985),
               frameon=False, fontsize=10)

# --------- funzioni principali: SAPP e per-Paese ----------
def plot_generation_share_by_group(gen_df: pd.DataFrame,
                                   out_dir: Path,
                                   groups: list[str] = GROUP_NAMES,
                                   years: list[str] = YEARS,
                                   tech_order: list[str] = GEN_PLOT_TECHS,
                                   location: str = "SAPP",
                                   subfolder_name: str = "generation_share"):
    base = Path(out_dir) / subfolder_name
    base.mkdir(parents=True, exist_ok=True)
    gen_df = gen_df.loc[:, ~gen_df.columns.duplicated()].copy()

    for g in groups:
        gdir = base / g
        gdir.mkdir(parents=True, exist_ok=True)
        for yr in years:
            plot_data = _prepare_genshare_for_plot(gen_df, group=g, year=yr, location=location)

            fig, ax = plt.subplots(figsize=(12.5, 6.5))
            _plot_macro_stacked_share(
                ax, plot_data, value_col="share_pct",
                tech_order=tech_order, ylabel="Generation share [%]",
                title=f"{g} — {yr}", colors=TECH_COLORS
            )

            # fascia bianca sopra per legende (fuori dal grafico)
            fig.subplots_adjust(top=0.80, bottom=0.22, left=0.08, right=0.98)
            _add_legends_outside(fig, plot_data, tech_order)

            out_path = gdir / f"{g}_{yr}_generation_share.png"
            fig.savefig(out_path, dpi=220, bbox_inches="tight")
            plt.close(fig)

def plot_generation_share_by_countries(gen_df: pd.DataFrame,
                                       out_dir: Path,
                                       countries: list[str],
                                       groups: list[str] = GROUP_NAMES,
                                       years: list[str] = YEARS,
                                       tech_order: list[str] = GEN_PLOT_TECHS):
    """
    Crea gli stessi grafici per ogni Paese.
    Output: .../PLOTS/generation_share_by_country/<COUNTRY>/<GROUP>/<GROUP>_<YEAR>_generation_share_<COUNTRY>.png
    """
    base = Path(out_dir) / "generation_share_by_country"
    base.mkdir(parents=True, exist_ok=True)
    gen_df = gen_df.loc[:, ~gen_df.columns.duplicated()].copy()

    for loc in countries:
        loc_dir = base / loc
        loc_dir.mkdir(parents=True, exist_ok=True)
        for g in groups:
            gdir = loc_dir / g
            gdir.mkdir(parents=True, exist_ok=True)
            for yr in years:
                plot_data = _prepare_genshare_for_plot(gen_df, group=g, year=yr, location=loc)

                fig, ax = plt.subplots(figsize=(12.5, 6.5))
                _plot_macro_stacked_share(
                    ax, plot_data, value_col="share_pct",
                    tech_order=tech_order, ylabel="Generation share [%]",
                    title=f"{g} — {yr} — {loc}", colors=TECH_COLORS
                )

                fig.subplots_adjust(top=0.80, bottom=0.22, left=0.08, right=0.98)
                _add_legends_outside(fig, plot_data, tech_order)

                out_path = gdir / f"{g}_{yr}_generation_share_{loc}.png"
                fig.savefig(out_path, dpi=220, bbox_inches="tight")
                plt.close(fig)

# ===== COSTRUZIONE DF =====
# SAPP
generation_share_df = pd.concat([
    _read_genshare_from_excel("Autarky", YEARS, SCENARIO_NAMES, location="SAPP"),
    _read_genshare_from_excel("Existing_Transmission", YEARS, SCENARIO_NAMES, location="SAPP"),
    _read_genshare_from_excel("Transmission_Expansion", YEARS, SCENARIO_NAMES, location="SAPP"),
], ignore_index=True)

assert not generation_share_df.empty, "generation_share_df è vuoto: verifica i path dei 3 Excel per group."

# ===== PLOT SAPP =====
plot_generation_share_by_group(
    generation_share_df,
    out_dir=OUT_BASE,
    groups=GROUP_NAMES,
    years=YEARS,
    tech_order=GEN_PLOT_TECHS,
    location="SAPP",
    subfolder_name="generation_share"
)

# ===== PLOT PER PAESE (solo MOZ totale) =====
# ===== PLOT PER PAESE (lista di paesi) =====
COUNTRIES_FOR_PLOTS = ["AGO","BWA","DRC","LSO","MWI","NAM","SWZ","TZA","ZAF","ZMB","ZWE","MOZ","SAPP"]

pieces = []
for loc in COUNTRIES_FOR_PLOTS:
    for g in GROUP_NAMES:
        pieces.append(_read_genshare_from_excel(g, YEARS, SCENARIO_NAMES, location=loc))

generation_share_by_country_df = pd.concat(pieces, ignore_index=True)

# (opzionale) sanity check
print("Loaded locations:", sorted(generation_share_by_country_df["location"].unique()))

plot_generation_share_by_countries(
    generation_share_by_country_df,
    out_dir=OUT_BASE,
    countries=COUNTRIES_FOR_PLOTS,
    groups=GROUP_NAMES,
    years=YEARS,
    tech_order=GEN_PLOT_TECHS
)


# %%
# %% ============================================================================
# SEZIONE 6 — ANNUAL COSTS (M$/yr): PV / W / Hydro / Gas / BESS / PHES (+ Transmission in TX_Expansion)
# ==============================================================================

# === CONFIG percorsi file costi ===
COSTS_BASE = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\Results")

# nomi base: i file sono <basename>_<group>.xlsx
COSTS_FILES = {
    "annualized": "Annualized_Investments",
    "fixed_om":  "O&M_Fixed_Yearly_Costs",
    "var_om":    "O&M_Variable_Costs",
}
TX_PAIR_FILE_BASENAME = "Transmission_Costs"  # -> Transmission_Costs_<group>.xlsx

# tecnologie incluse (Transmission aggiunta solo per group == Transmission_Expansion)
COST_TECHS = ["PV_New", "W_New", "Hydro_New", "OCGT_New", "BESS_New", "PHES_New"]

# etichette leggenda senza suffisso _New
TECH_LABEL_COSTS = {
    "PV_New": "PV",
    "W_New": "Wind",
    "Hydro_New": "Hydro",
    "OCGT_New": "Gas",
    "BESS_New": "BESS",
    "PHES_New": "PHES",
    "Transmission_New": "Transmission",
}

# ordine dello stack (Transmission alla fine)
COST_TECH_ORDER = ["PV_New", "W_New", "Hydro_New", "OCGT_New", "BESS_New", "PHES_New", "Transmission_New"]

# ---------- utility ----------
def _cost_excel_path_for_group(group: str, basename: str) -> Path:
    return COSTS_BASE / group / f"{basename}_{group}.xlsx"

def _prep_cost_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    if "location" in out.columns:
        out["location"] = out["location"].astype(str).replace({"": np.nan, "nan": np.nan}).ffill()
        out["location"] = out["location"].astype(str).str.strip()
    if "tech" in out.columns:
        out["tech"] = out["tech"].astype(str).str.strip()
    return out

def crf(r: float, n: int) -> float:
    return r * (1 + r)**n / ((1 + r)**n - 1)

# Parametri per annualizzare l'Investment della Transmission (file a coppie)
TX_R = 0.10
TX_N = 40
TX_CRF = crf(TX_R, TX_N)  # ≈ 0.1023/yr

# ---------- lettura componenti costi per tecnologia (PV/W/H/NG/BESS/PHES) ----------
def _read_component_costs(group: str,
                          component_key: str,  # "annualized" | "fixed_om" | "var_om"
                          years: list[str],
                          scenarios: list[str]) -> pd.DataFrame:
    """
    Ritorna df lungo: [group, scenario, location, tech, year, value_Myr]
    (valori in M$/yr, come nei file input).
    """
    basename = COSTS_FILES[component_key]
    xlsx = _cost_excel_path_for_group(group, basename)
    if not xlsx.exists():
        return pd.DataFrame(columns=["group","scenario","location","tech","year","value_Myr"])

    sheets = pd.read_excel(xlsx, sheet_name=None, engine="openpyxl")
    rows = []
    for sc_name, raw in sheets.items():
        if sc_name not in scenarios or raw is None or raw.empty:
            continue
        df = _prep_cost_df(raw)
        yr_cols = [y for y in years if y in df.columns]
        if "location" not in df.columns or "tech" not in df.columns or not yr_cols:
            continue

        sub = df[df["tech"].isin(COST_TECHS + ["Transmission_New"])].copy()
        if sub.empty:
            continue

        g = sub.groupby(["location","tech"], as_index=False)[yr_cols].sum()
        for _, r in g.iterrows():
            loc = str(r["location"]); tech = str(r["tech"])
            for y in yr_cols:
                rows.append({"group": group, "scenario": sc_name, "location": loc,
                             "tech": tech, "year": str(y), "value_Myr": float(r[y])})
    return pd.DataFrame(rows)

# ---------- Transmission dai file a coppie: annualizza Investment e somma ----------
def _read_transmission_pairs_costs(group: str,
                                   years: list[str],
                                   scenarios: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Legge Transmission_Costs_<group>.xlsx (colonne: Country 1, Country 2, Parameter, 2030, 2035, 2040, ...).
    Parameter ∈ {'Investment','Fixed_O&M','Variable_O&M'(se presente), 'Energy'}.
    Annualizza 'Investment' con CRF(10%, 40y).
    Ritorna due DF (M$/yr) già sommati su Investment_annualized + Fixed_O&M + Variable_O&M:
      - SAPP: somma unica di tutte le coppie (una volta sola).
      - Country: somma di tutte le coppie dove il Paese compare in Country 1 o Country 2.
    """
    xlsx = _cost_excel_path_for_group(group, TX_PAIR_FILE_BASENAME)
    if not xlsx.exists():
        empty = ["group","scenario","location","tech","year","value_Myr"]
        return (pd.DataFrame(columns=empty), pd.DataFrame(columns=empty))

    sheets = pd.read_excel(xlsx, sheet_name=None, engine="openpyxl")
    sapp_rows, ctry_rows = [], []

    for sc_name, df in sheets.items():
        if sc_name not in scenarios or df is None or df.empty:
            continue

        t = df.copy()
        t.columns = [str(c).strip() for c in t.columns]
        for col in ["Country 1","Country 2","Parameter"]:
            assert col in t.columns, f"Colonna mancante in Transmission file: {col}"

        yr_cols = [y for y in years if y in t.columns]
        if not yr_cols:
            continue

        t["Parameter"] = t["Parameter"].astype(str).str.strip()
        wanted = t["Parameter"].isin(["Investment","Fixed_O&M","Variable_O&M"])
        if not wanted.any():
            wanted = t["Parameter"].isin(["Investment","Fixed_O&M"])
        tt = t.loc[wanted, ["Country 1","Country 2","Parameter", *yr_cols]].copy()

        # annualizza Investimenti
        inv_mask = tt["Parameter"] == "Investment"
        if inv_mask.any():
            tt.loc[inv_mask, yr_cols] = tt.loc[inv_mask, yr_cols].astype(float) * TX_CRF

        # --- SAPP: somma una volta tutte le coppie ---
        sapp_sum = tt.groupby("Parameter", as_index=False)[yr_cols].sum()
        for _, r in sapp_sum.iterrows():
            for y in yr_cols:
                sapp_rows.append({
                    "group": group, "scenario": sc_name, "location": "SAPP",
                    "tech": "Transmission_New", "year": str(y), "param": r["Parameter"],
                    "value_Myr": float(r[y])
                })

        # --- Per Paese: somma su tutte le coppie che includono il Paese ---
        countries_in_file = sorted(set(tt["Country 1"].astype(str)) | set(tt["Country 2"].astype(str)))
        for ctry in countries_in_file:
            mask = (tt["Country 1"].astype(str) == ctry) | (tt["Country 2"].astype(str) == ctry)
            subt = tt.loc[mask]
            if subt.empty:
                continue
            g = subt.groupby("Parameter", as_index=False)[yr_cols].sum()
            for _, r in g.iterrows():
                for y in yr_cols:
                    ctry_rows.append({
                        "group": group, "scenario": sc_name, "location": ctry,
                        "tech": "Transmission_New", "year": str(y), "param": r["Parameter"],
                        "value_Myr": float(r[y])
                    })

    def _fold_param(df_in: pd.DataFrame) -> pd.DataFrame:
        if df_in.empty:
            return df_in
        return (df_in.groupby(["group","scenario","location","tech","year"], as_index=False)["value_Myr"]
                     .sum())

    sapp_df = _fold_param(pd.DataFrame(sapp_rows))
    ctry_df = _fold_param(pd.DataFrame(ctry_rows))
    return sapp_df, ctry_df

# ---------- costruzione DF totale (SAPP e per-paese) ----------
def build_annual_costs_df(groups: list[str],
                          years: list[str],
                          scenarios: list[str],
                          countries: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ritorna:
      costs_sapp_df: [group, year, scenario, macro, sub, location='SAPP', tech, value_Myr]
      costs_ctry_df: [group, year, scenario, macro, sub, location=<CTRY>, tech, value_Myr]
    """
    # 1) Somma Annualized + O&M fix + O&M var per tecnologia (no Transmission qui)
    comp_all = []
    for g in groups:
        for comp_key in ["annualized","fixed_om","var_om"]:
            comp_all.append(_read_component_costs(g, comp_key, years, scenarios))
    comp_all = (pd.concat(comp_all, ignore_index=True)
                if comp_all else pd.DataFrame(columns=["group","scenario","location","tech","year","value_Myr"]))
    if not comp_all.empty:
        comp_all = (comp_all.groupby(["group","scenario","location","tech","year"], as_index=False)["value_Myr"]
                           .sum())
        comp_all = comp_all[comp_all["tech"].isin(COST_TECHS)].copy()

    # 2) Transmission dai file a coppie (solo per Transmission_Expansion)
    tx_sapp = pd.DataFrame(columns=["group","scenario","location","tech","year","value_Myr"])
    tx_ctry = pd.DataFrame(columns=["group","scenario","location","tech","year","value_Myr"])
    if "Transmission_Expansion" in groups:
        sapp_df, ctry_df = _read_transmission_pairs_costs("Transmission_Expansion", years, scenarios)
        tx_sapp, tx_ctry = sapp_df, ctry_df

    # 3) SAPP: somma per tecnologia su tutti i paesi + aggiungi Transmission SAPP
    sapp_gen = pd.DataFrame(columns=["group","scenario","location","tech","year","value_Myr"])
    if not comp_all.empty:
        sapp_gen = (comp_all.groupby(["group","scenario","tech","year"], as_index=False)["value_Myr"]
                           .sum())
        sapp_gen["location"] = "SAPP"
    costs_sapp = pd.concat([sapp_gen, tx_sapp], ignore_index=True)

    # 4) Per Paese: costi per location dal comp_all + Transmission per presenza nella coppia
    costs_ctry = comp_all.copy()
    if not tx_ctry.empty:
        costs_ctry = pd.concat([costs_ctry, tx_ctry], ignore_index=True)

    # 5) Aggiungi macro/sub e ordina
    def _attach_macro_sub(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        out = df.copy()
        out[["macro","sub"]] = out["scenario"].map(SCENARIO_TO_MACRO).apply(pd.Series)
        out["tech"] = pd.Categorical(out["tech"], categories=COST_TECH_ORDER, ordered=True)
        return out

    costs_sapp = _attach_macro_sub(costs_sapp)
    costs_ctry = _attach_macro_sub(costs_ctry)

    # 6) Filtra tecnologie per group (Transmission solo per Transmission_Expansion)
    def _filter_for_group(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        out = []
        for g in groups:
            sub = df[df["group"] == g].copy()
            keep = COST_TECHS + (["Transmission_New"] if g == "Transmission_Expansion" else [])
            sub = sub[sub["tech"].isin(keep)]
            out.append(sub)
        return pd.concat(out, ignore_index=True) if out else df

    costs_sapp = _filter_for_group(costs_sapp)
    costs_ctry = _filter_for_group(costs_ctry)

    for d in (costs_sapp, costs_ctry):
        if not d.empty:
            d.sort_values(["group","year","macro","sub","scenario","tech","location"], inplace=True)

    return costs_sapp, costs_ctry

# ---------- helper per plot ----------
def _prepare_costs_for_plot(df: pd.DataFrame,
                            group: str,
                            year: str,
                            location: str) -> pd.DataFrame:
    sub = df[(df["group"] == group) &
             (df["year"].astype(str) == str(year)) &
             (df["location"] == location)].copy()
    if sub.empty:
        idx = pd.MultiIndex.from_product([MACROS, SUBS, COST_TECH_ORDER], names=["macro","sub","tech"])
        return pd.DataFrame({"value_Myr": np.zeros(len(idx))}, index=idx).reset_index()

    agg = (sub.groupby(["macro","sub","tech"], observed=True)["value_Myr"]
               .sum(min_count=1)
               .reindex(pd.MultiIndex.from_product([MACROS, SUBS, COST_TECH_ORDER], names=["macro","sub","tech"]),
                        fill_value=0.0)
               .reset_index())
    return agg

def compute_costs_ymax(costs_df: pd.DataFrame, group: str, location: str) -> float:
    d = costs_df[(costs_df["group"] == group) & (costs_df["location"] == location)]
    if d.empty:
        return 100.0
    tot = (d.groupby(["year","macro","sub"], observed=True)["value_Myr"]
             .sum(min_count=1)
             .reset_index())
    if tot.empty:
        return 100.0
    ymax = float(tot["value_Myr"].max())
    # arrotonda al multiplo di 50 M$/yr
    return float(np.ceil(max(ymax, 1.0) / 50.0) * 50.0)

# ---------- plotting (barre per scenario, stack per tecnologia; colori = TECH_COLORS esistenti) ----------
def _plot_macro_stacked_costs(ax: plt.Axes,
                              data: pd.DataFrame,
                              title: str,
                              ylabel: str = "Annual system cost [M$/yr]",
                              bar_width: float = 0.18,
                              gap_macro: float = 0.70):
    x_positions, x_labels = [], []
    for i_macro, macro in enumerate(MACROS):
        base = i_macro * (4 * bar_width + gap_macro)
        for j, sublab in enumerate(SUBS):
            x_positions.append(base + j * bar_width)
            x_labels.append((macro, sublab))

    for i, (macro, sublab) in enumerate(zip([m for m in MACROS for _ in SUBS], SUBS * len(MACROS))):
        bottom = 0.0
        dbar = data[(data["macro"] == macro) & (data["sub"] == sublab)]
        for t in COST_TECH_ORDER:
            val = float(dbar.loc[dbar["tech"] == t, "value_Myr"].sum()) if not dbar.empty else 0.0
            if val <= 0:
                continue
            ax.bar(x_positions[i], val, width=bar_width * 0.92, bottom=bottom,
                   color=TECH_COLORS.get(t, "#999999"), edgecolor="none")
            bottom += val

    ax.set_title(title, pad=12)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.6)
    ax.set_xticks(x_positions)
    ax.set_xticklabels([lbl for (_, lbl) in x_labels])
    ax.tick_params(axis="x", labelsize=10)

    # Etichette macro sotto l'asse
    ax_ymax = ax.get_ylim()[1]
    for i_macro, macro in enumerate(MACROS):
        left = i_macro * (4 * bar_width + gap_macro)
        right = left + 3 * bar_width
        center = (left + right) / 2.0
        ax.text(center, -ax_ymax * 0.16, macro, ha="center", va="top",
                fontsize=13, fontweight="bold", transform=ax.transData)

def _add_costs_legends(fig, plot_data: pd.DataFrame):
    # tecnologie realmente presenti (>0) in figura
    leg_techs = []
    for t in COST_TECH_ORDER:
        val = float(plot_data.loc[plot_data["tech"] == t, "value_Myr"].sum()) if not plot_data.empty else 0.0
        if val > 0:
            leg_techs.append(t)
    if not leg_techs:
        leg_techs = COST_TECH_ORDER

    handles = [Patch(facecolor=TECH_COLORS.get(t, "#999999"),
                     edgecolor="none",
                     label=TECH_LABEL_COSTS.get(t, t.replace("_New","")) )
               for t in leg_techs]
    ncols = int(np.ceil(len(handles)/2))
    fig.legend(handles=handles, ncol=ncols, loc="upper left",
               bbox_to_anchor=(0.005, 0.985), frameon=False, fontsize=10,
               columnspacing=0.9, handletextpad=0.4)

    # mini-leggenda N/B/P/B+P (come negli altri grafici)
    sublabels = ['N = NoStorage', 'B = BESS', 'P = PHES', 'B+P = BESS+PHES']
    dummy = [Patch(facecolor="none", edgecolor="none", label=s) for s in sublabels]
    fig.legend(handles=dummy, loc="upper right", bbox_to_anchor=(0.995, 0.985),
               frameon=False, fontsize=10)

# ---------- plot SAPP ----------
def plot_annual_costs_sapp(costs_sapp_df: pd.DataFrame,
                           out_dir: Path,
                           groups: list[str] = GROUP_NAMES,
                           years: list[str] = YEARS,
                           location: str = "SAPP"):
    base = Path(out_dir) / "annual_costs"
    base.mkdir(parents=True, exist_ok=True)

    for g in groups:
        gdir = base / g
        gdir.mkdir(parents=True, exist_ok=True)

        ymax_group = compute_costs_ymax(costs_sapp_df, group=g, location=location)

        for yr in years:
            plot_data = _prepare_costs_for_plot(costs_sapp_df, group=g, year=yr, location=location)
            fig, ax = plt.subplots(figsize=(12.5, 6.5))
            _plot_macro_stacked_costs(ax, plot_data, title=f"{g} — {yr} — {location}",
                                       ylabel="Annual system cost [M$/yr]")
            ax.set_ylim(0.0, ymax_group * 1.08)
            fig.subplots_adjust(top=0.80, bottom=0.22, left=0.08, right=0.98)
            _add_costs_legends(fig, plot_data)

            out_path = gdir / f"{g}_{yr}_annual_costs_{location}.png"
            fig.savefig(out_path, dpi=220, bbox_inches="tight")
            plt.close(fig)

# ---------- plot per Paese ----------
def plot_annual_costs_by_countries(costs_ctry_df: pd.DataFrame,
                                   out_dir: Path,
                                   countries: list[str],
                                   groups: list[str] = GROUP_NAMES,
                                   years: list[str] = YEARS):
    base = Path(out_dir) / "annual_costs_by_country"
    base.mkdir(parents=True, exist_ok=True)

    for loc in countries:
        loc_dir = base / loc
        loc_dir.mkdir(parents=True, exist_ok=True)
        for g in groups:
            gdir = loc_dir / g
            gdir.mkdir(parents=True, exist_ok=True)

            ymax_group = compute_costs_ymax(costs_ctry_df, group=g, location=loc)

            for yr in years:
                plot_data = _prepare_costs_for_plot(costs_ctry_df, group=g, year=yr, location=loc)
                fig, ax = plt.subplots(figsize=(12.5, 6.5))
                _plot_macro_stacked_costs(ax, plot_data, title=f"{g} — {yr} — {loc}",
                                           ylabel="Annual system cost [M$/yr]")
                ax.set_ylim(0.0, ymax_group * 1.08)
                fig.subplots_adjust(top=0.80, bottom=0.22, left=0.08, right=0.98)
                _add_costs_legends(fig, plot_data)

                out_path = gdir / f"{g}_{yr}_annual_costs_{loc}.png"
                fig.savefig(out_path, dpi=220, bbox_inches="tight")
                plt.close(fig)

# ===== ESECUZIONE: costruzione DF e grafici =====
costs_sapp_df, costs_ctry_df = build_annual_costs_df(
    groups=GROUP_NAMES, years=YEARS, scenarios=SCENARIO_NAMES, countries=COUNTRY_CODE
)

# sanity check
assert not costs_sapp_df.empty, "costs_sapp_df è vuoto: verifica file costi/percorsi."
assert not costs_ctry_df.empty, "costs_ctry_df è vuoto: verifica file costi/percorsi."

# SAPP aggregato
plot_annual_costs_sapp(costs_sapp_df, out_dir=OUT_BASE, groups=GROUP_NAMES, years=YEARS, location="SAPP")

# Per Paese (escludo 'SAPP'; includo 'MOZ' totale)
plot_annual_costs_by_countries(costs_ctry_df,
                               out_dir=OUT_BASE,
                               countries=["AGO","BWA","DRC","LSO","MWI","NAM","SWZ","TZA","ZAF","ZMB","ZWE","MOZ"])

# # %% ============================================================================
# # EXPORT TABELLE — SOLO SAPP (un file per group, uno sheet per anno)
# # ============================================================================

# from pandas import ExcelWriter

# def export_sapp_costs_tables(costs_sapp_df: pd.DataFrame,
#                              out_dir: Path,
#                              groups: list[str] = GROUP_NAMES,
#                              years: list[str] = YEARS,
#                              location: str = "SAPP",
#                              tech_cols: list[str] = COST_TECH_ORDER):
#     """
#     Crea un Excel per ciascun group con 3 sheet (2030/2035/2040).
#     Ogni sheet è una pivot con righe = (Macro, Sub, Scenario) e colonne = tecnologie, valori = M$/yr.
#     """
#     base = Path(out_dir) / "annual_costs"
#     base.mkdir(parents=True, exist_ok=True)

#     for g in groups:
#         # filtra solo SAPP del group
#         d = costs_sapp_df[(costs_sapp_df["group"] == g) &
#                           (costs_sapp_df["location"] == location)].copy()
#         if d.empty:
#             continue

#         xlsx_path = base / f"Annual_Costs_SAPP_{g}.xlsx"
#         with ExcelWriter(xlsx_path, engine="openpyxl") as xw:
#             for yr in years:
#                 sub = d[d["year"].astype(str) == str(yr)].copy()
#                 if sub.empty:
#                     # crea sheet vuoto con intestazioni
#                     empty = pd.DataFrame(columns=["Macro","Sub","Scenario", *[TECH_LABEL_COSTS.get(t, t) for t in tech_cols]])
#                     empty.to_excel(xw, sheet_name=str(yr), index=False)
#                     continue

#                 # pivot: righe (macro, sub, scenario), colonne = tech, valori = value_Myr (somma)
#                 pv = (sub.groupby(["macro","sub","scenario","tech"], observed=True)["value_Myr"]
#                           .sum(min_count=1)
#                           .reset_index())

#                 # mappa etichette colonna tech e garantisce l'ordine desiderato
#                 pv["tech"] = pd.Categorical(pv["tech"], categories=tech_cols, ordered=True)
#                 pv = pv.pivot_table(index=["macro","sub","scenario"],
#                                     columns="tech",
#                                     values="value_Myr",
#                                     aggfunc="sum",
#                                     fill_value=0.0)

#                 # riordina colonne secondo COST_TECH_ORDER e rinomina senza _New
#                 cols_ordered = [c for c in tech_cols if c in pv.columns]
#                 pv = pv.reindex(columns=cols_ordered)
#                 pv.columns = [TECH_LABEL_COSTS.get(c, c.replace("_New","")) for c in pv.columns]
#                 pv = pv.sort_index()  # ordina righe (macro, sub, scenario)

#                 # esporta
#                 pv.to_excel(xw, sheet_name=str(yr))

#         # (opzionale) stampa percorso in console
#         print(f"[OK] Tabella SAPP esportata: {xlsx_path}")

# # ESECUZIONE EXPORT (SOLO SAPP)
# export_sapp_costs_tables(costs_sapp_df, out_dir=OUT_BASE,
#                          groups=GROUP_NAMES, years=YEARS, location="SAPP",
#                          tech_cols=COST_TECH_ORDER)


# %% ============================================================================
# SEZIONE 7 — ANNUAL COSTS (B$/yr): PV / Wind / Hydro / Gas / BESS / PHES (+ Transmission)
# Solo SAPP (niente per-paese), overlay LCOE, scale fisse globali
# ============================================================================

COSTS_BASE = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\Results")
LCOE_BASE  = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\LCOE")

COSTS_FILES = {
    "annualized": "Annualized_Investments",
    "fixed_om":  "O&M_Fixed_Yearly_Costs",
    "var_om":    "O&M_Variable_Costs",
}
TX_PAIR_FILE_BASENAME = "Transmission_Costs"  # Transmission_Costs_<group>.xlsx

COST_TECHS = ["PV_New","W_New","Hydro_New","OCGT_New","BESS_New","PHES_New"]
TECH_LABEL_COSTS = {
    "PV_New":"PV","W_New":"Wind","Hydro_New":"Hydro","OCGT_New":"Gas",
    "BESS_New":"BESS","PHES_New":"PHES","Transmission_New":"Transmission",
}
COST_TECH_ORDER = ["PV_New","W_New","Hydro_New","OCGT_New","BESS_New","PHES_New","Transmission_New"]

# ---------- utility ----------
def _cost_excel_path_for_group(group: str, basename: str) -> Path:
    return COSTS_BASE / group / f"{basename}_{group}.xlsx"

def crf(r: float, n: int) -> float:
    return r * (1 + r)**n / ((1 + r)**n - 1)

TX_CRF = crf(0.10, 40)  # annualizzazione Transmission (10% / 40y)

def _prep_cost_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    if "location" in out:
        out["location"] = out["location"].astype(str).str.strip().str.upper()
    if "tech" in out:
        out["tech"] = out["tech"].astype(str).str.strip()
    return out

# ---------- lettura componenti tecnologia (in B$/yr) ----------
def _read_component_costs(group: str, component_key: str, years: list[str], scenarios: list[str]) -> pd.DataFrame:
    """
    Ritorna DF lungo: [group, scenario, location, tech, year, value_Byr] in B$/yr.
    """
    xlsx = _cost_excel_path_for_group(group, COSTS_FILES[component_key])
    if not xlsx.exists():
        return pd.DataFrame(columns=["group","scenario","location","tech","year","value_Byr"])

    sheets = pd.read_excel(xlsx, sheet_name=None, engine="openpyxl")
    rows = []
    for sc_name, raw in sheets.items():
        if sc_name not in scenarios or raw is None or raw.empty:
            continue
        df = _prep_cost_df(raw)
        yr_cols = [y for y in years if y in df.columns]
        if not yr_cols or "location" not in df.columns or "tech" not in df.columns:
            continue
        sub = df[df["tech"].isin(COST_TECHS + ["Transmission_New"])]
        if sub.empty:
            continue
        gsum = sub.groupby(["location","tech"], as_index=False)[yr_cols].sum()
        for _, r in gsum.iterrows():
            loc = str(r["location"])
            tech = str(r["tech"])
            for y in yr_cols:
                rows.append({
                    "group": group, "scenario": sc_name, "location": loc,
                    "tech": tech, "year": str(y), "value_Byr": float(r[y]) / 1000.0
                })
    return pd.DataFrame(rows)

# ---------- Transmission (SAPP only) in B$/yr ----------
def _read_transmission_pairs_costs_sapp(group: str, years: list[str], scenarios: list[str]) -> pd.DataFrame:
    """
    Legge Transmission_Costs_<group>.xlsx, annualizza 'Investment' (CRF 10%/40y),
    somma Investment_annualized + Fixed_O&M (+ Variable_O&M se presente) su tutte le coppie.
    Ritorna DF lungo per SAPP: [group, scenario, location='SAPP', tech='Transmission_New', year, value_Byr].
    """
    xlsx = _cost_excel_path_for_group(group, TX_PAIR_FILE_BASENAME)
    if not xlsx.exists():
        return pd.DataFrame(columns=["group","scenario","location","tech","year","value_Byr"])

    sheets = pd.read_excel(xlsx, sheet_name=None, engine="openpyxl")
    rows = []
    for sc_name, df in sheets.items():
        if sc_name not in scenarios or df is None or df.empty:
            continue
        t = df.copy()
        t.columns = [str(c).strip() for c in t.columns]
        assert all(c in t.columns for c in ["Country 1","Country 2","Parameter"]), "Transmission file: colonne mancanti"
        yr_cols = [y for y in years if y in t.columns]
        if not yr_cols:
            continue
        t["Parameter"] = t["Parameter"].astype(str).str.strip()
        tt = t[t["Parameter"].isin(["Investment","Fixed_O&M","Variable_O&M"])].copy()
        inv_mask = tt["Parameter"] == "Investment"
        if inv_mask.any():
            tt.loc[inv_mask, yr_cols] = tt.loc[inv_mask, yr_cols].astype(float) * TX_CRF

        sapp_sum = tt.groupby("Parameter", as_index=False)[yr_cols].sum()
        for _, r in sapp_sum.iterrows():
            for y in yr_cols:
                rows.append({
                    "group": group, "scenario": sc_name, "location": "SAPP",
                    "tech": "Transmission_New", "year": str(y),
                    "value_Byr": float(r[y]) / 1000.0
                })
    if not rows:
        return pd.DataFrame(columns=["group","scenario","location","tech","year","value_Byr"])
    out = (pd.DataFrame(rows)
             .groupby(["group","scenario","location","tech","year"], as_index=False)["value_Byr"]
             .sum())
    return out

# ---------- build cost DF SAPP ----------
def build_annual_costs_sapp_df(groups: list[str], years: list[str], scenarios: list[str]) -> pd.DataFrame:
    """
    Ritorna DF SAPP lungo: [group, scenario, macro, sub, location='SAPP', tech, year, value_Byr] (B$/yr).
    """
    comp = []
    for g in groups:
        for key in ["annualized","fixed_om","var_om"]:
            comp.append(_read_component_costs(g, key, years, scenarios))
    comp = pd.concat(comp, ignore_index=True) if comp else pd.DataFrame()
    if not comp.empty:
        comp = (comp.groupby(["group","scenario","location","tech","year"], as_index=False)["value_Byr"].sum())
        comp = comp[comp["tech"].isin(COST_TECHS)].copy()

    # SAPP = somma dei Paesi (tecnologie), + Transmission SAPP solo se available
    sapp = pd.DataFrame(columns=["group","scenario","tech","year","value_Byr","location"])
    if not comp.empty:
        sapp = (comp.groupby(["group","scenario","tech","year"], as_index=False)["value_Byr"].sum())
        sapp["location"] = "SAPP"

    if "Transmission_Expansion" in groups:
        tx_sapp = _read_transmission_pairs_costs_sapp("Transmission_Expansion", years, scenarios)
        sapp = pd.concat([sapp, tx_sapp], ignore_index=True)

    if sapp.empty:
        return sapp

    sapp[["macro","sub"]] = sapp["scenario"].map(SCENARIO_TO_MACRO).apply(pd.Series)
    sapp["tech"] = pd.Categorical(sapp["tech"], categories=COST_TECH_ORDER, ordered=True)
    sapp.sort_values(["group","year","macro","sub","scenario","tech"], inplace=True)
    return sapp

# ---------- LCOE (System = 'All_Techs') ----------
def build_lcoe_system_df(groups: list[str], years: list[str], scenarios: list[str]) -> pd.DataFrame:
    rows = []
    for g in groups:
        xlsx = LCOE_BASE / g / f"LCOE_System_AllTechs_{g}.xlsx"
        if not xlsx.exists():
            continue
        sheets = pd.read_excel(xlsx, sheet_name=None, engine="openpyxl")
        for sc_name, raw in sheets.items():
            if sc_name not in scenarios or raw is None or raw.empty:
                continue
            if sc_name not in SCENARIO_TO_MACRO:
                continue
            macro, sub = SCENARIO_TO_MACRO[sc_name]
            df = raw.copy()
            df.columns = [str(c).strip() for c in df.columns]
            if "location" not in df.columns or "tech" not in df.columns:
                continue
            df = df[df["tech"].astype(str).str.strip().eq("All_Techs")].copy()
            yr_cols = [y for y in years if y in df.columns]
            if not yr_cols:
                continue
            for _, r in df.iterrows():
                loc = str(r["location"]).strip().upper()
                for y in yr_cols:
                    val = r[y]
                    if pd.isna(val):
                        continue
                    rows.append({
                        "group": g, "scenario": sc_name, "macro": macro, "sub": sub,
                        "location": loc, "year": str(y), "lcoe_$MWh": float(val)
                    })
    out = pd.DataFrame(rows)
    if not out.empty:
        out["location"] = out["location"].astype(str).str.upper()
    return out

# ---------- scale fisse globali (solo SAPP) ----------
def _nice_round_up(x: float, step: float) -> float:
    return float(np.ceil(max(x, 1e-9) / step) * step)

def compute_fixed_costs_ymax_sapp(costs_sapp_df: pd.DataFrame) -> float:
    if costs_sapp_df.empty:
        return 0.1
    tot = (costs_sapp_df.groupby(["group","year","macro","sub"], observed=True)["value_Byr"]
             .sum(min_count=1))
    ymax = float(tot.max()) if not tot.empty else 0.1
    return _nice_round_up(ymax, 0.05)  # multiplo di 0.05 B$ (= 50 M$)

def compute_fixed_lcoe_ymax_sapp(lcoe_df: pd.DataFrame) -> float:
    if lcoe_df.empty:
        return 100.0
    vals = lcoe_df[lcoe_df["location"] == "SAPP"]["lcoe_$MWh"]
    ymax = float(vals.max()) if not vals.empty else 100.0
    return _nice_round_up(ymax, 10.0)  # multiplo di 10 $/MWh

# ---------- helper per plot ----------
def _prepare_costs_for_plot_sapp(df: pd.DataFrame, group: str, year: str, location: str = "SAPP") -> pd.DataFrame:
    sub = df[(df["group"] == group) &
             (df["year"].astype(str) == str(year)) &
             (df["location"] == location)].copy()
    idx = pd.MultiIndex.from_product([MACROS, SUBS, COST_TECH_ORDER], names=["macro","sub","tech"])
    agg = (sub.groupby(["macro","sub","tech"], observed=True)["value_Byr"]
             .sum(min_count=1)
             .reindex(idx, fill_value=0.0)
             .reset_index())
    return agg

def _get_lcoe_points(lcoe_df: pd.DataFrame, group: str, year: str, location: str = "SAPP") -> dict[tuple[str,str], float]:
    if lcoe_df.empty:
        return {}
    sub = lcoe_df[(lcoe_df["group"] == group) &
                  (lcoe_df["year"].astype(str) == str(year)) &
                  (lcoe_df["location"] == location)]
    pts = {}
    for macro in MACROS:
        for sublab in SUBS:
            v = float(sub.loc[(sub["macro"] == macro) & (sub["sub"] == sublab), "lcoe_$MWh"].mean()) if not sub.empty else 0.0
            pts[(macro, sublab)] = v if v > 0 else 0.0
    return pts

# ---------- disegno barre + etichette macro MOLTO in basso ----------
def _plot_macro_stacked_costs(ax: plt.Axes,
                              data: pd.DataFrame,
                              title: str,
                              ylabel: str = "Annual cost [B$/yr]",
                              bar_width: float = 0.18,
                              gap_macro: float = 0.70):
    x_positions, x_labels = [], []
    for i_macro, macro in enumerate(MACROS):
        base = i_macro * (4 * bar_width + gap_macro)
        for j, sublab in enumerate(SUBS):
            x_positions.append(base + j * bar_width)
            x_labels.append((macro, sublab))

    for i, (macro, sublab) in enumerate(zip([m for m in MACROS for _ in SUBS], SUBS * len(MACROS))):
        bottom = 0.0
        dbar = data[(data["macro"] == macro) & (data["sub"] == sublab)]
        for t in COST_TECH_ORDER:
            val = float(dbar.loc[dbar["tech"] == t, "value_Byr"].sum()) if not dbar.empty else 0.0
            if val <= 0:
                continue
            ax.bar(x_positions[i], val, width=bar_width * 0.92, bottom=bottom,
                   color=TECH_COLORS.get(t, "#999999"), edgecolor="none")
            bottom += val

    ax.set_title(title, pad=12)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.6)
    ax.set_xticks(x_positions)
    ax.set_xticklabels([lbl for (_, lbl) in x_labels])
    ax.tick_params(axis="x", labelsize=10)

    # Etichette macro molto in basso (spostate di più rispetto a prima)
    ax_ymax = ax.get_ylim()[1]
    for i_macro, macro in enumerate(MACROS):
        left = i_macro * (4 * bar_width + gap_macro)
        right = left + 3 * bar_width
        center = (left + right) / 2.0
        ax.text(center, -ax_ymax * 0.42, macro, ha="center", va="top",
                fontsize=13, fontweight="bold", transform=ax.transData)

def _add_costs_legends(fig, plot_data: pd.DataFrame):
    leg_techs = []
    for t in COST_TECH_ORDER:
        val = float(plot_data.loc[plot_data["tech"] == t, "value_Byr"].sum()) if not plot_data.empty else 0.0
        if val > 0:
            leg_techs.append(t)
    if not leg_techs:
        leg_techs = COST_TECH_ORDER

    handles = [Patch(facecolor=TECH_COLORS.get(t, "#999999"), edgecolor="none",
                     label=TECH_LABEL_COSTS.get(t, t.replace("_New","")) )
               for t in leg_techs]
    ncols = int(np.ceil(len(handles) / 2))
    fig.legend(handles=handles, ncol=ncols, loc="upper left",
               bbox_to_anchor=(0.005, 0.985), frameon=False, fontsize=10,
               columnspacing=0.9, handletextpad=0.4)

    # mini-leggenda N/B/P/B+P
    sublabels = ['N = NoStorage', 'B = BESS', 'P = PHES', 'B+P = BESS+PHES']
    dummy = [Patch(facecolor="none", edgecolor="none", label=s) for s in sublabels]
    fig.legend(handles=dummy, loc="upper right", bbox_to_anchor=(0.995, 0.985),
               frameon=False, fontsize=10)

# ---------- overlay LCOE (asse destro) ----------
def _overlay_lcoe_points(ax: plt.Axes,
                         lcoe_points: dict[tuple[str,str], float],
                         ylabel: str = "LCOE [$ / MWh]",
                         bar_width: float = 0.18,
                         gap_macro: float = 0.70,
                         color: str = "#860303",
                         fixed_ymin: float = 0.0,
                         fixed_ymax: float | None = None):
    x_positions = []
    for i_macro, macro in enumerate(MACROS):
        base = i_macro * (4 * bar_width + gap_macro)
        for j, sublab in enumerate(SUBS):
            x_positions.append((macro, sublab, base + j * bar_width))

    ax2 = ax.twinx()
    xs, ys = [], []
    for (macro, sublab, x) in x_positions:
        v = lcoe_points.get((macro, sublab), 0.0)
        if v and np.isfinite(v):
            xs.append(x); ys.append(v)

    if xs:
        ax2.scatter(xs, ys, s=36, marker="o", color=color, zorder=5)
    ax2.set_ylabel(ylabel, color=color)
    ax2.tick_params(axis="y", colors=color)
    if fixed_ymax is not None:
        ax2.set_ylim(fixed_ymin, fixed_ymax)
    else:
        y_min, y_max = (min(ys), max(ys)) if ys else (0.0, 100.0)
        pad = max(1.0, 0.06 * (y_max - y_min if y_max > y_min else y_max))
        ax2.set_ylim(max(0.0, y_min - pad), y_max + pad)
    return ax2

# ---------- plot SAPP ----------
def plot_annual_costs_sapp(costs_sapp_df: pd.DataFrame,
                           lcoe_df: pd.DataFrame,
                           out_dir: Path,
                           groups: list[str],
                           years: list[str],
                           location: str,
                           fixed_cost_ymax: float,
                           fixed_lcoe_ymax: float):
    base = Path(out_dir) / "annual_costs"
    base.mkdir(parents=True, exist_ok=True)

    for g in groups:
        gdir = base / g
        gdir.mkdir(parents=True, exist_ok=True)

        for yr in years:
            data = _prepare_costs_for_plot_sapp(costs_sapp_df, group=g, year=yr, location=location)
            fig, ax = plt.subplots(figsize=(12.5, 6.5))
            _plot_macro_stacked_costs(ax, data, title=f"{g} — {yr} — {location}", ylabel="Annual cost [B$/yr]")
            ax.set_ylim(0.0, fixed_cost_ymax)

            # più spazio sotto per le etichette macro molto in basso
            fig.subplots_adjust(top=0.80, bottom=0.36, left=0.08, right=0.98)

            _add_costs_legends(fig, data)
            # overlay LCOE
            lpts = _get_lcoe_points(lcoe_df, group=g, year=yr, location=location)
            _overlay_lcoe_points(ax, lpts, fixed_ymin=0.0, fixed_ymax=fixed_lcoe_ymax)

            out_path = gdir / f"{g}_{yr}_annual_costs_{location}.png"
            fig.savefig(out_path, dpi=220, bbox_inches="tight")
            plt.close(fig)

# ---------- export tabella SAPP in B$/yr ----------
from pandas import ExcelWriter
def export_sapp_costs_tables(costs_sapp_df: pd.DataFrame,
                             out_dir: Path,
                             groups: list[str],
                             years: list[str],
                             location: str,
                             tech_cols: list[str]):
    base = Path(out_dir) / "annual_costs"
    base.mkdir(parents=True, exist_ok=True)

    for g in groups:
        d = costs_sapp_df[(costs_sapp_df["group"] == g) & (costs_sapp_df["location"] == location)].copy()
        if d.empty:
            continue
        p = base / f"Annual_Costs_SAPP_{g}.xlsx"
        with ExcelWriter(p, engine="openpyxl") as xw:
            for y in years:
                sub = d[d["year"].astype(str) == str(y)]
                if sub.empty:
                    pd.DataFrame(columns=["Macro","Sub","Scenario", *[TECH_LABEL_COSTS.get(t,t) for t in tech_cols]]).to_excel(xw, sheet_name=str(y), index=False)
                    continue

                pv = (sub.groupby(["macro","sub","scenario","tech"], observed=True)["value_Byr"]
                        .sum(min_count=1)
                        .reset_index())
                pv["tech"] = pd.Categorical(pv["tech"], categories=tech_cols, ordered=True)
                pv = pv.pivot_table(index=["macro","sub","scenario"], columns="tech", values="value_Byr", aggfunc="sum", fill_value=0.0)
                pv = pv.reindex(columns=[c for c in tech_cols if c in pv.columns])
                pv.columns = [TECH_LABEL_COSTS.get(c, c.replace("_New","")) for c in pv.columns]
                pv.sort_index().to_excel(xw, sheet_name=str(y))
        print(f"[OK] Tabella SAPP esportata (B$/yr): {p}")

# ===== ESECUZIONE (solo SAPP) =====
costs_sapp_df = build_annual_costs_sapp_df(GROUP_NAMES, YEARS, SCENARIO_NAMES)
lcoe_system_df = build_lcoe_system_df(GROUP_NAMES, YEARS, SCENARIO_NAMES)

# Scale fisse globali SAPP
COST_YMAX_SAPP = compute_fixed_costs_ymax_sapp(costs_sapp_df)
LCOE_YMAX_SAPP = compute_fixed_lcoe_ymax_sapp(lcoe_system_df)

print(f"[Scale fisse SAPP] Costi: {COST_YMAX_SAPP} B$/yr — LCOE: {LCOE_YMAX_SAPP} $/MWh")

# Plot SAPP con LCOE
plot_annual_costs_sapp(costs_sapp_df, lcoe_system_df, OUT_BASE,
                       groups=GROUP_NAMES, years=YEARS, location="SAPP",
                       fixed_cost_ymax=COST_YMAX_SAPP, fixed_lcoe_ymax=LCOE_YMAX_SAPP)

# Export tabella SAPP
export_sapp_costs_tables(costs_sapp_df, OUT_BASE, GROUP_NAMES, YEARS, "SAPP", COST_TECH_ORDER)


# %% ============================================================================
# SEZIONE 9 — INVESTMENT SHARE BY COUNTRY (stacked bars, 0–100%)
#   - Fonte: Annualized_Investments_<group>.xlsx
#   - Fix: merged cells -> forward-fill della colonna 'location'
#   - Aggregazione: per Paese (MOZ_NC + MOZ_S → MOZ), escluso 'SAPP'
#   - Output: per ogni group/anno, 3 subplot (macro) × 4 barre (N, B, P, B+P)
# ============================================================================

from pandas import ExcelWriter

INV_BASE = COSTS_BASE
INV_BASENAME = "Annualized_Investments"

# palette Paesi fissa (12 SAPP, MOZ aggregato)
SAPP_COUNTRY_ORDER = ["AGO","BWA","DRC","LSO","MOZ","MWI","NAM","SWZ","TZA","ZAF","ZMB","ZWE"]

def _collapse_location_loc(loc: str) -> str:
    loc = str(loc).strip().upper()
    if loc in {"MOZ_NC", "MOZ_S"}:
        return "MOZ"
    return loc

def _inv_excel_path_for_group(group: str) -> Path:
    return INV_BASE / group / f"{INV_BASENAME}_{group}.xlsx"

def _read_investments_long(group: str,
                           years: list[str],
                           scenarios: list[str]) -> pd.DataFrame:
    """
    Legge Annualized_Investments_<group>.xlsx e ritorna:
      [group, scenario, macro, sub, location, year, inv_Myr]
    - Gestisce celle 'location' merge/blank con forward-fill.
    - Esclude righe SAPP (totale regionale) per la ripartizione per-paese.
    """
    xlsx = _inv_excel_path_for_group(group)
    if not xlsx.exists():
        return pd.DataFrame(columns=["group","scenario","macro","sub","location","year","inv_Myr"])

    sheets = pd.read_excel(xlsx, sheet_name=None, engine="openpyxl")
    rows = []
    for sc_name, raw in sheets.items():
        if sc_name not in scenarios or raw is None or raw.empty:
            continue
        if sc_name not in SCENARIO_TO_MACRO:
            continue

        macro, sub = SCENARIO_TO_MACRO[sc_name]
        df = raw.copy()
        # normalizza nomi colonne
        df.columns = [str(c).strip() for c in df.columns]
        if "location" not in df.columns:
            continue
        yr_cols = [y for y in years if y in df.columns]
        if not yr_cols:
            continue

        # === FIX MERGED CELLS ===
        # 1) lascia NaN, poi ffill (propaga il paese verso il basso)
        df["location"] = df["location"].replace({"" : np.nan})
        df["location"] = df["location"].ffill()

        # 2) normalizza, filtra valori non validi
        df["location"] = (df["location"]
                          .astype(str).str.strip().str.upper())
        # escludi totali regionali e righe senza location valida
        df = df[(df["location"].notna()) &
                (df["location"] != "") &
                (df["location"] != "NAN") &
                (df["location"] != "SAPP")]

        # 3) collassa MOZ_NC/MOZ_S -> MOZ
        df["location"] = df["location"].map(_collapse_location_loc)

        if df.empty:
            continue

        # somma per paese (su tutte le tecnologie)
        gsum = df.groupby("location", as_index=False)[yr_cols].sum()

        # registra righe "lunghe"
        for _, r in gsum.iterrows():
            loc = str(r["location"])
            for y in yr_cols:
                val = r[y]
                if pd.isna(val):
                    continue
                rows.append({
                    "group": group, "scenario": sc_name, "macro": macro, "sub": sub,
                    "location": loc, "year": str(y), "inv_Myr": float(val)
                })
    return pd.DataFrame(rows)

def _build_investment_share_df(groups: list[str],
                               years: list[str],
                               scenarios: list[str]) -> pd.DataFrame:
    """
    Calcola le quote % per Paese dentro ogni (group, year, macro, sub).
    """
    parts = []
    for g in groups:
        inv = _read_investments_long(g, years, scenarios)
        if inv.empty:
            continue

        # Assicura che i soli Paesi in legenda siano quelli SAPP (gli altri -> scartati)
        inv = inv[inv["location"].isin(SAPP_COUNTRY_ORDER)].copy()

        agg = (inv.groupby(["group","year","macro","sub","scenario","location"], observed=True)["inv_Myr"]
                  .sum(min_count=1).reset_index())

        # shares dentro ogni macro+sub
        out_rows = []
        for (grp, yr, mac, sub), subdf in agg.groupby(["group","year","macro","sub"]):
            tot = float(subdf["inv_Myr"].sum())
            # reindex per includere anche paesi con quota 0
            subdf = (subdf.set_index("location")
                           .reindex(SAPP_COUNTRY_ORDER, fill_value=0.0)
                           .reset_index())
            for _, r in subdf.iterrows():
                share = (float(r["inv_Myr"]) / tot * 100.0) if tot > 0 else 0.0
                out_rows.append({
                    "group": grp, "year": str(yr), "macro": mac, "sub": sub,
                    "location": r["location"], "share_pct": share
                })
        parts.append(pd.DataFrame(out_rows))
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

def _country_color_map(countries: list[str]) -> dict[str, str]:
    cmap = plt.get_cmap("tab20")
    colors = {}
    for i, c in enumerate(countries):
        colors[c] = cmap(i % 20)
    return colors

def plot_investment_share_bars(share_df: pd.DataFrame,
                               out_dir: Path,
                               groups: list[str] = GROUP_NAMES,
                               years: list[str] = YEARS):
    """
    Per ogni group/year: 3 subplot (macro) con 4 barre (N, B, P, B+P).
    Ogni barra è una stacked 0–100% sulle quote per Paese.
    """
    base = Path(out_dir) / "investment_share_bars"
    base.mkdir(parents=True, exist_ok=True)

    if share_df.empty:
        raise RuntimeError("Investment share DF è vuoto: controlla i file Annualized_Investments_*.")

    color_map = _country_color_map(SAPP_COUNTRY_ORDER)

    for g in groups:
        gdir = base / g
        gdir.mkdir(parents=True, exist_ok=True)

        for yr in years:
            sub = share_df[(share_df["group"] == g) & (share_df["year"].astype(str) == str(yr))].copy()
            if sub.empty:
                continue

            macros_present = [m for m in MACROS if m in set(sub["macro"])]
            n_macros = len(macros_present)
            fig, axes = plt.subplots(1, n_macros, figsize=(5.6 * n_macros, 5.2))
            if n_macros == 1:
                axes = [axes]

            for ax, mac in zip(axes, macros_present):
                chunk = sub[sub["macro"] == mac].copy()
                if chunk.empty:
                    ax.text(0.5, 0.5, f"{mac}\n(no data)", ha="center", va="center")
                    ax.axis("off")
                    continue

                scenarios = ["N", "B", "P", "B+P"]
                # costruiamo una matrice: index=Paese, columns=scenario, valori=share%
                mat = (chunk.pivot_table(index="location", columns="sub", values="share_pct",
                                         aggfunc="sum", fill_value=0.0)
                             .reindex(index=SAPP_COUNTRY_ORDER, columns=scenarios, fill_value=0.0))

                x = np.arange(len(scenarios))
                bottom = np.zeros_like(x, dtype=float)

                for ctry in SAPP_COUNTRY_ORDER:
                    vals = mat.loc[ctry, scenarios].to_numpy(dtype=float)
                    if (vals > 0).any():
                        ax.bar(x, vals, bottom=bottom, width=0.72,
                               color=color_map[ctry], edgecolor="none", label=ctry)
                    bottom += vals

                ax.set_ylim(0, 100)
                ax.set_ylabel("Share of SAPP total [%]")
                ax.set_title(f"{mac} — {yr}")
                ax.set_xticks(x)
                ax.set_xticklabels(scenarios, fontsize=10)
                ax.grid(axis="y", linestyle="--", alpha=0.35)

            # legenda unica con i 12 paesi (in ordine predefinito)
            handles = [Patch(facecolor=color_map[c], edgecolor="none", label=c) for c in SAPP_COUNTRY_ORDER]
            fig.legend(handles=handles, ncol=min(6, len(handles)),
                       loc="upper center", bbox_to_anchor=(0.5, 1.03),
                       frameon=False, fontsize=9)
            fig.subplots_adjust(top=0.86, bottom=0.12, left=0.07, right=0.98, wspace=0.28)

            out_path = gdir / f"{g}_{yr}_investment_share.png"
            fig.savefig(out_path, dpi=220, bbox_inches="tight")
            plt.close(fig)
            print(f"[OK] Saved: {out_path}")

# ===== COSTRUZIONE DF & PLOT =====
inv_share_df = _build_investment_share_df(GROUP_NAMES, YEARS, SCENARIO_NAMES)
assert not inv_share_df.empty, "inv_share_df è vuoto: controlla i file Annualized_Investments_*."
plot_investment_share_bars(inv_share_df, out_dir=OUT_BASE, groups=GROUP_NAMES, years=YEARS)

# %% ============================================================================
# SEZIONE 10 — GDP SHARE per Paese (%): solo Annualized Investments / GDP(B$)
#   - Una figura per SCENARIO (=> 36 figure: 3 group × 12 scenari)
#   - Ogni figura: 12 gruppi (Paesi); per ciascuno 3 barre (anni 1,2,3)
#   - Numeratore: Annualized_Investments_<group>.xlsx (somma su TUTTE le tech, NO Transmission)
#   - Denominatore: GDP (B$) inserito manualmente qui sotto
#   - Y auto; legenda: 1=2030, 2=2035, 3=2040
# ============================================================================

# === GDP (B$) in constant 2025 US$ ===
GDP_BILLION: dict[str, float] = {
    "AGO": 108.4090062,
    "BWA": 21.1628758,
    "DRC": 73.3973295,
    "LSO":  2.8005087,
    "MOZ": 25.2930898,
    "MWI": 14.4769845,
    "NAM": 14.7917781,
    "SWZ":  5.7634720,
    "TZA": 90.1005083,
    "ZAF": 442.1518475,
    "ZMB": 34.7219422,
    "ZWE": 28.5973457,
}

# Ordine fisso paesi (12)
SAPP_COUNTRY_ORDER = ["AGO","BWA","DRC","LSO","MOZ","MWI","NAM","SWZ","TZA","ZAF","ZMB","ZWE"]

# ---- Costruzione DF: Investimenti annualizzati per Paese (M$/yr) -> % su GDP ----
def build_gdp_share_df(groups: list[str],
                       years: list[str],
                       scenarios: list[str]) -> pd.DataFrame:
    """
    Ritorna DF lungo:
      [group, scenario, macro, sub, country, year, inv_Myr, gdp_B$, share_pct]
    Con 'year' ∈ {'2030','2035','2040'} e share_pct = (Inv[B$/yr] / GDP[B$]) * 100
    """
    parts = []
    for g in groups:
        # riuso parser della Sezione 9 (somma per Paese su tutte le tech, escludendo SAPP)
        inv_long = _read_investments_long(g, years, scenarios)
        if inv_long.empty:
            continue

        # tieni solo i 12 Paesi SAPP nell’ordine desiderato
        inv_long = inv_long[inv_long["location"].isin(SAPP_COUNTRY_ORDER)].copy()

        # somma su scenario/location/year
        agg = (inv_long.groupby(["scenario","macro","sub","location","year"], observed=True)["inv_Myr"]
                        .sum(min_count=1).reset_index())

        # calcola % su GDP (convertendo M$ -> B$)
        rows = []
        for _, r in agg.iterrows():
            loc = str(r["location"]).upper()
            y   = str(r["year"])
            inv_Byr = float(r["inv_Myr"]) / 1000.0  # M$/yr -> B$/yr
            gdp = float(GDP_BILLION.get(loc, np.nan))
            share = (inv_Byr / gdp * 100.0) if (gdp and np.isfinite(gdp) and gdp > 0) else 0.0
            rows.append({
                "group": g,
                "scenario": str(r["scenario"]),
                "macro": str(r["macro"]),
                "sub": str(r["sub"]),
                "country": loc,
                "year": y,
                "inv_Myr": float(r["inv_Myr"]),
                "gdp_B$": gdp,
                "share_pct": share
            })
        df_g = pd.DataFrame(rows)
        if not df_g.empty:
            df_g["country"] = pd.Categorical(df_g["country"], categories=SAPP_COUNTRY_ORDER, ordered=True)
        parts.append(df_g)

    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(
        columns=["group","scenario","macro","sub","country","year","inv_Myr","gdp_B$","share_pct"]
    )

# ---- Plot: una figura per scenario (per ogni group) ----
def plot_gdp_share_by_scenario(share_df: pd.DataFrame,
                               out_dir: Path,
                               groups: list[str] = GROUP_NAMES,
                               scenarios: list[str] = SCENARIO_NAMES,
                               years: list[str] = YEARS):
    """
    Salva in: .../PLOTS/gdp_share_by_country/<GROUP>/<SCENARIO>_gdp_share.png
    Figura: 12 Paesi × 3 barre (anni=1,2,3). Y in % auto.
    """
    base = Path(out_dir) / "gdp_share_by_country"
    base.mkdir(parents=True, exist_ok=True)

    # mapping anno -> numero breve
    year_code = {"2030": "1", "2035": "2", "2040": "3"}
    # ordine fisso anni
    years_ord = [y for y in ["2030","2035","2040"] if y in years]

    # colori per i 3 anni (stabili in tutte le figure)
    year_colors = {"2030": "#6aa5ff", "2035": "#66c56c", "2040": "#f2b84b"}

    for g in groups:
        gdir = base / g
        gdir.mkdir(parents=True, exist_ok=True)

        # scenari effettivamente presenti nel DF per il group
        scen_present = sorted(set(share_df.loc[share_df["group"] == g, "scenario"]))
        for sc in scenarios:
            if sc not in scen_present:
                continue

            subdf = share_df[(share_df["group"] == g) &
                             (share_df["scenario"] == sc)].copy()
            if subdf.empty:
                continue

            # matrice: index=country, columns=year (2030/35/40), valori=share%
            mat = (subdf.pivot_table(index="country", columns="year", values="share_pct",
                                     aggfunc="sum", fill_value=0.0)
                          .reindex(index=SAPP_COUNTRY_ORDER, columns=years_ord, fill_value=0.0))

            # layout barre: 12 gruppi × 3 barre
            n_ctry = len(SAPP_COUNTRY_ORDER)
            bar_w = 0.22
            gap_country = 0.38  # spazio tra gruppi paese

            x_positions = []
            x_labels = []  # "1/2/3" ripetuti
            centers_per_country = []  # per scrivere il codice paese sotto

            # calcolo posizioni
            for i, ctry in enumerate(SAPP_COUNTRY_ORDER):
                base_x = i * (len(years_ord) * bar_w + gap_country)
                # 3 barrette affiancate per anno
                for j, y in enumerate(years_ord):
                    x = base_x + j * bar_w
                    x_positions.append(x)
                    x_labels.append(year_code.get(y, y))
                # centro del gruppetto
                left = base_x
                right = base_x + (len(years_ord)-1) * bar_w if years_ord else base_x
                centers_per_country.append(( (left+right)/2.0, ctry ))

            # plotting
            fig, ax = plt.subplots(figsize=(14.5, 6.2))
            for j, y in enumerate(years_ord):
                vals = mat[y].to_numpy(dtype=float)
                xs_j = [i * (len(years_ord) * bar_w + gap_country) + j * bar_w for i in range(n_ctry)]
                ax.bar(xs_j, vals, width=bar_w*0.92, edgecolor="none", color=year_colors[y], label=year_code[y])

            # asse e griglia
            ax.set_ylabel("Annualized investments / GDP [%]")
            ax.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.6)

            # tick delle barrette (1/2/3)
            ax.set_xticks(x_positions)
            ax.set_xticklabels(x_labels, fontsize=9)

            # scritte Paese molto in basso, centrate sotto ciascun gruppetto
            # (aumentiamo il margine inferiore per non sovrapporre)
            y_max = max(1.0, float(np.nanmax(mat.to_numpy())))
            ax.set_ylim(0, y_max * 1.15)
            fig.subplots_adjust(bottom=0.28, top=0.84, left=0.08, right=0.98)

            ymin, ymax = ax.get_ylim()
            text_y = ymin - (ymax - ymin) * 0.18
            for xc, ctry in centers_per_country:
                ax.text(xc, text_y, ctry, ha="center", va="top",
                        fontsize=10.5, fontweight="bold", transform=ax.transData)

            # titolo e legenda anni (1=2030,2=2035,3=2040) in alto
            ax.set_title(f"{g} — {sc} — GDP share by country", pad=12)
            handles = [
                Patch(facecolor=year_colors["2030"], edgecolor="none", label="1 = 2030"),
                Patch(facecolor=year_colors["2035"], edgecolor="none", label="2 = 2035"),
                Patch(facecolor=year_colors["2040"], edgecolor="none", label="3 = 2040"),
            ]
            fig.legend(handles=handles, ncol=3, loc="upper center",
                       bbox_to_anchor=(0.5, 0.995), frameon=False, fontsize=10)

            # salva
            out_path = gdir / f"{sc}_gdp_share.png"
            fig.savefig(out_path, dpi=220, bbox_inches="tight")
            plt.close(fig)
            print(f"[OK] Saved: {out_path}")

# ===== COSTRUZIONE DF & PLOT =====
gdp_share_df = build_gdp_share_df(GROUP_NAMES, YEARS, SCENARIO_NAMES)
assert not gdp_share_df.empty, "gdp_share_df è vuoto: verifica i file Annualized_Investments_* e i GDP."

plot_gdp_share_by_scenario(gdp_share_df, out_dir=OUT_BASE,
                           groups=GROUP_NAMES, scenarios=SCENARIO_NAMES, years=YEARS)

# END OF GRAPHS

# %% ============================================================================
# SEZIONE 7 — ANNUAL COSTS (B$/yr): PV / Wind / Hydro / Gas / BESS / PHES (+ Transmission)
# Solo SAPP (niente per-paese), overlay LCOE. Assi fissi ma *per-gruppo*:
# - stesso ymax (costi e LCOE) per tutti gli anni del *gruppo*
# - diverso tra gruppi (Autarky, Existing_Transmission, Transmission_Expansion)
# ============================================================================

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from pandas import ExcelWriter

# === CONFIG base di questa sezione ===
COSTS_BASE = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\Results")
LCOE_BASE  = Path(r"C:\Users\giorg\Desktop\PoliMi\Tesi\21_PostProcessing\4_Final_Post_Processing\LCOE")

COSTS_FILES = {
    "annualized": "Annualized_Investments",
    "fixed_om":  "O&M_Fixed_Yearly_Costs",
    "var_om":    "O&M_Variable_Costs",
}
TX_PAIR_FILE_BASENAME = "Transmission_Costs"  # Transmission_Costs_<group>.xlsx

COST_TECHS = ["PV_New","W_New","Hydro_New","OCGT_New","BESS_New","PHES_New"]
TECH_LABEL_COSTS = {
    "PV_New":"PV","W_New":"Wind","Hydro_New":"Hydro","OCGT_New":"Gas",
    "BESS_New":"BESS","PHES_New":"PHES","Transmission_New":"Transmission",
}
COST_TECH_ORDER = ["PV_New","W_New","Hydro_New","OCGT_New","BESS_New","PHES_New","Transmission_New"]

# ---------- utility ----------
def _cost_excel_path_for_group(group: str, basename: str) -> Path:
    return COSTS_BASE / group / f"{basename}_{group}.xlsx"

def crf(r: float, n: int) -> float:
    return r * (1 + r)**n / ((1 + r)**n - 1)

TX_CRF = crf(0.10, 40)  # annualizzazione Transmission (10% / 40y)

def _prep_cost_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    if "location" in out:
        out["location"] = out["location"].astype(str).str.strip().str.upper()
    if "tech" in out:
        out["tech"] = out["tech"].astype(str).str.strip()
    return out

# ---------- lettura componenti tecnologia (in B$/yr) ----------
def _read_component_costs(group: str, component_key: str, years: list[str], scenarios: list[str]) -> pd.DataFrame:
    """
    Ritorna DF lungo: [group, scenario, location, tech, year, value_Byr] in B$/yr.
    """
    xlsx = _cost_excel_path_for_group(group, COSTS_FILES[component_key])
    if not xlsx.exists():
        return pd.DataFrame(columns=["group","scenario","location","tech","year","value_Byr"])

    sheets = pd.read_excel(xlsx, sheet_name=None, engine="openpyxl")
    rows = []
    for sc_name, raw in sheets.items():
        if sc_name not in scenarios or raw is None or raw.empty:
            continue
        df = _prep_cost_df(raw)
        yr_cols = [y for y in years if y in df.columns]
        if not yr_cols or "location" not in df.columns or "tech" not in df.columns:
            continue
        sub = df[df["tech"].isin(COST_TECHS + ["Transmission_New"])]
        if sub.empty:
            continue
        gsum = sub.groupby(["location","tech"], as_index=False)[yr_cols].sum()
        for _, r in gsum.iterrows():
            loc = str(r["location"])
            tech = str(r["tech"])
            for y in yr_cols:
                rows.append({
                    "group": group, "scenario": sc_name, "location": loc,
                    "tech": tech, "year": str(y), "value_Byr": float(r[y]) / 1000.0
                })
    return pd.DataFrame(rows)

# ---------- Transmission (SAPP only) in B$/yr ----------
def _read_transmission_pairs_costs_sapp(group: str, years: list[str], scenarios: list[str]) -> pd.DataFrame:
    """
    Legge Transmission_Costs_<group>.xlsx, annualizza 'Investment' (CRF 10%/40y),
    somma Investment_annualized + Fixed_O&M (+ Variable_O&M se presente) su tutte le coppie.
    Ritorna DF lungo per SAPP: [group, scenario, location='SAPP', tech='Transmission_New', year, value_Byr].
    """
    xlsx = _cost_excel_path_for_group(group, TX_PAIR_FILE_BASENAME)
    if not xlsx.exists():
        return pd.DataFrame(columns=["group","scenario","location","tech","year","value_Byr"])

    sheets = pd.read_excel(xlsx, sheet_name=None, engine="openpyxl")
    rows = []
    for sc_name, df in sheets.items():
        if sc_name not in scenarios or df is None or df.empty:
            continue
        t = df.copy()
        t.columns = [str(c).strip() for c in t.columns]
        assert all(c in t.columns for c in ["Country 1","Country 2","Parameter"]), "Transmission file: colonne mancanti"
        yr_cols = [y for y in years if y in t.columns]
        if not yr_cols:
            continue
        t["Parameter"] = t["Parameter"].astype(str).str.strip()
        tt = t[t["Parameter"].isin(["Investment","Fixed_O&M","Variable_O&M"])].copy()
        inv_mask = tt["Parameter"] == "Investment"
        if inv_mask.any():
            tt.loc[inv_mask, yr_cols] = tt.loc[inv_mask, yr_cols].astype(float) * TX_CRF

        sapp_sum = tt.groupby("Parameter", as_index=False)[yr_cols].sum()
        for _, r in sapp_sum.iterrows():
            for y in yr_cols:
                rows.append({
                    "group": group, "scenario": sc_name, "location": "SAPP",
                    "tech": "Transmission_New", "year": str(y),
                    "value_Byr": float(r[y]) / 1000.0
                })
    if not rows:
        return pd.DataFrame(columns=["group","scenario","location","tech","year","value_Byr"])
    out = (pd.DataFrame(rows)
             .groupby(["group","scenario","location","tech","year"], as_index=False)["value_Byr"]
             .sum())
    return out

# ---------- build cost DF SAPP ----------
def build_annual_costs_sapp_df(groups: list[str], years: list[str], scenarios: list[str]) -> pd.DataFrame:
    """
    Ritorna DF SAPP lungo: [group, scenario, macro, sub, location='SAPP', tech, year, value_Byr] (B$/yr).
    Richiede che SCENARIO_TO_MACRO, MACROS, SUBS siano definiti a livello globale.
    """
    comp = []
    for g in groups:
        for key in ["annualized","fixed_om","var_om"]:
            comp.append(_read_component_costs(g, key, years, scenarios))
    comp = pd.concat(comp, ignore_index=True) if comp else pd.DataFrame()
    if not comp.empty:
        comp = (comp.groupby(["group","scenario","location","tech","year"], as_index=False)["value_Byr"].sum())
        comp = comp[comp["tech"].isin(COST_TECHS)].copy()

    # SAPP = somma dei Paesi (tecnologie), + Transmission SAPP solo se available
    sapp = pd.DataFrame(columns=["group","scenario","tech","year","value_Byr","location"])
    if not comp.empty:
        sapp = (comp.groupby(["group","scenario","tech","year"], as_index=False)["value_Byr"].sum())
        sapp["location"] = "SAPP"

    if "Transmission_Expansion" in groups:
        tx_sapp = _read_transmission_pairs_costs_sapp("Transmission_Expansion", years, scenarios)
        sapp = pd.concat([sapp, tx_sapp], ignore_index=True)

    if sapp.empty:
        return sapp

    sapp[["macro","sub"]] = sapp["scenario"].map(SCENARIO_TO_MACRO).apply(pd.Series)
    sapp["tech"] = pd.Categorical(sapp["tech"], categories=COST_TECH_ORDER, ordered=True)
    sapp.sort_values(["group","year","macro","sub","scenario","tech"], inplace=True)
    return sapp

# ---------- LCOE (System = 'All_Techs') ----------
def build_lcoe_system_df(groups: list[str], years: list[str], scenarios: list[str]) -> pd.DataFrame:
    rows = []
    for g in groups:
        xlsx = LCOE_BASE / g / f"LCOE_System_AllTechs_{g}.xlsx"
        if not xlsx.exists():
            continue
        sheets = pd.read_excel(xlsx, sheet_name=None, engine="openpyxl")
        for sc_name, raw in sheets.items():
            if sc_name not in scenarios or raw is None or raw.empty:
                continue
            if sc_name not in SCENARIO_TO_MACRO:
                continue
            macro, sub = SCENARIO_TO_MACRO[sc_name]
            df = raw.copy()
            df.columns = [str(c).strip() for c in df.columns]
            if "location" not in df.columns or "tech" not in df.columns:
                continue
            df = df[df["tech"].astype(str).str.strip().eq("All_Techs")].copy()
            yr_cols = [y for y in years if y in df.columns]
            if not yr_cols:
                continue
            for _, r in df.iterrows():
                loc = str(r["location"]).strip().upper()
                for y in yr_cols:
                    val = r[y]
                    if pd.isna(val):
                        continue
                    rows.append({
                        "group": g, "scenario": sc_name, "macro": macro, "sub": sub,
                        "location": loc, "year": str(y), "lcoe_$MWh": float(val)
                    })
    out = pd.DataFrame(rows)
    if not out.empty:
        out["location"] = out["location"].astype(str).str.upper()
    return out

# ---------- scale fisse per-gruppo (solo SAPP) ----------
def _nice_round_up(x: float, step: float) -> float:
    return float(np.ceil(max(x, 1e-9) / step) * step)

def compute_groupwise_costs_ymax_sapp(costs_sapp_df: pd.DataFrame) -> dict[str, float]:
    """
    Ritorna {group: ymax} dove ymax è il massimo dei costi annuali (B$/yr)
    all'interno del gruppo su tutti gli anni e sub-scenari, con arrotondamento "nice".
    """
    if costs_sapp_df.empty:
        return {}
    out = {}
    for g, sub in costs_sapp_df.groupby("group", observed=True):
        tot = (sub.groupby(["year","macro","sub"], observed=True)["value_Byr"]
                 .sum(min_count=1))
        ymax = float(tot.max()) if not tot.empty else 0.1
        out[g] = _nice_round_up(ymax, 0.05)  # multipli di 0.05 B$ (= 50 M$)
    return out

def compute_groupwise_lcoe_ymax_sapp(lcoe_df: pd.DataFrame) -> dict[str, float]:
    """
    Ritorna {group: ymax} per LCOE ($/MWh) considerando solo location == 'SAPP'
    e arrotondando a multipli di 10.
    """
    if lcoe_df.empty:
        return {}
    out = {}
    sub_all = lcoe_df[lcoe_df["location"] == "SAPP"]
    for g, sub in sub_all.groupby("group", observed=True):
        vmax = float(sub["lcoe_$MWh"].max()) if not sub.empty else 100.0
        out[g] = _nice_round_up(vmax, 10.0)
    return out

# ---------- helper per plot ----------
def _prepare_costs_for_plot_sapp(df: pd.DataFrame, group: str, year: str, location: str = "SAPP") -> pd.DataFrame:
    sub = df[(df["group"] == group) &
             (df["year"].astype(str) == str(year)) &
             (df["location"] == location)].copy()
    idx = pd.MultiIndex.from_product([MACROS, SUBS, COST_TECH_ORDER], names=["macro","sub","tech"])
    agg = (sub.groupby(["macro","sub","tech"], observed=True)["value_Byr"]
             .sum(min_count=1)
             .reindex(idx, fill_value=0.0)
             .reset_index())
    return agg

def _get_lcoe_points(lcoe_df: pd.DataFrame, group: str, year: str, location: str = "SAPP") -> dict[tuple[str,str], float]:
    if lcoe_df.empty:
        return {}
    sub = lcoe_df[(lcoe_df["group"] == group) &
                  (lcoe_df["year"].astype(str) == str(year)) &
                  (lcoe_df["location"] == location)]
    pts = {}
    for macro in MACROS:
        for sublab in SUBS:
            v = float(sub.loc[(sub["macro"] == macro) & (sub["sub"] == sublab), "lcoe_$MWh"].mean()) if not sub.empty else 0.0
            pts[(macro, sublab)] = v if v > 0 else 0.0
    return pts

# ---------- disegno barre + etichette macro MOLTO in basso ----------
def _plot_macro_stacked_costs(ax: plt.Axes,
                              data: pd.DataFrame,
                              title: str,
                              ylabel: str = "Annual cost [B$/yr]",
                              bar_width: float = 0.18,
                              gap_macro: float = 0.70):
    x_positions, x_labels = [], []
    for i_macro, macro in enumerate(MACROS):
        base = i_macro * (4 * bar_width + gap_macro)
        for j, sublab in enumerate(SUBS):
            x_positions.append(base + j * bar_width)
            x_labels.append((macro, sublab))

    for i, (macro, sublab) in enumerate(zip([m for m in MACROS for _ in SUBS], SUBS * len(MACROS))):
        bottom = 0.0
        dbar = data[(data["macro"] == macro) & (data["sub"] == sublab)]
        for t in COST_TECH_ORDER:
            val = float(dbar.loc[dbar["tech"] == t, "value_Byr"].sum()) if not dbar.empty else 0.0
            if val <= 0:
                continue
            ax.bar(x_positions[i], val, width=bar_width * 0.92, bottom=bottom,
                   color=TECH_COLORS.get(t, "#999999"), edgecolor="none")
            bottom += val

    ax.set_title(title, pad=12)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.6)
    ax.set_xticks(x_positions)
    ax.set_xticklabels([lbl for (_, lbl) in x_labels])
    ax.tick_params(axis="x", labelsize=10)

    # Etichette macro molto in basso
    ax_ymax = ax.get_ylim()[1]
    for i_macro, macro in enumerate(MACROS):
        left = i_macro * (4 * bar_width + gap_macro)
        right = left + 3 * bar_width
        center = (left + right) / 2.0
        ax.text(center, -ax_ymax * 0.42, macro, ha="center", va="top",
                fontsize=13, fontweight="bold", transform=ax.transData)

def _add_costs_legends(fig, plot_data: pd.DataFrame):
    leg_techs = []
    for t in COST_TECH_ORDER:
        val = float(plot_data.loc[plot_data["tech"] == t, "value_Byr"].sum()) if not plot_data.empty else 0.0
        if val > 0:
            leg_techs.append(t)
    if not leg_techs:
        leg_techs = COST_TECH_ORDER

    handles = [Patch(facecolor=TECH_COLORS.get(t, "#999999"), edgecolor="none",
                     label=TECH_LABEL_COSTS.get(t, t.replace("_New","")) )
               for t in leg_techs]
    ncols = int(np.ceil(len(handles) / 2))
    fig.legend(handles=handles, ncol=ncols, loc="upper left",
               bbox_to_anchor=(0.005, 0.985), frameon=False, fontsize=10,
               columnspacing=0.9, handletextpad=0.4)

    # mini-leggenda N/B/P/B+P
    sublabels = ['N = NoStorage', 'B = BESS', 'P = PHES', 'B+P = BESS+PHES']
    dummy = [Patch(facecolor="none", edgecolor="none", label=s) for s in sublabels]
    fig.legend(handles=dummy, loc="upper right", bbox_to_anchor=(0.995, 0.985),
               frameon=False, fontsize=10)

# ---------- overlay LCOE (asse destro) ----------
def _overlay_lcoe_points(ax: plt.Axes,
                         lcoe_points: dict[tuple[str,str], float],
                         ylabel: str = "LCOE [$ / MWh]",
                         bar_width: float = 0.18,
                         gap_macro: float = 0.70,
                         color: str = "#860303",
                         fixed_ymin: float = 0.0,
                         fixed_ymax: float | None = None):
    x_positions = []
    for i_macro, macro in enumerate(MACROS):
        base = i_macro * (4 * bar_width + gap_macro)
        for j, sublab in enumerate(SUBS):
            x_positions.append((macro, sublab, base + j * bar_width))

    ax2 = ax.twinx()
    xs, ys = [], []
    for (macro, sublab, x) in x_positions:
        v = lcoe_points.get((macro, sublab), 0.0)
        if v and np.isfinite(v):
            xs.append(x); ys.append(v)

    if xs:
        ax2.scatter(xs, ys, s=36, marker="o", color=color, zorder=5)
    ax2.set_ylabel(ylabel, color=color)
    ax2.tick_params(axis="y", colors=color)
    if fixed_ymax is not None:
        ax2.set_ylim(fixed_ymin, fixed_ymax)
    else:
        y_min, y_max = (min(ys), max(ys)) if ys else (0.0, 100.0)
        pad = max(1.0, 0.06 * (y_max - y_min if y_max > y_min else y_max))
        ax2.set_ylim(max(0.0, y_min - pad), y_max + pad)
    return ax2

# ---------- plot SAPP (usa ymax per-gruppo) ----------
def plot_annual_costs_sapp(costs_sapp_df: pd.DataFrame,
                           lcoe_df: pd.DataFrame,
                           out_dir: Path,
                           groups: list[str],
                           years: list[str],
                           location: str,
                           cost_ymax_by_group: dict[str, float],
                           lcoe_ymax_by_group: dict[str, float]):
    base = Path(out_dir) / "annual_costs"
    base.mkdir(parents=True, exist_ok=True)

    for g in groups:
        gdir = base / g
        gdir.mkdir(parents=True, exist_ok=True)

        for yr in years:
            data = _prepare_costs_for_plot_sapp(costs_sapp_df, group=g, year=yr, location=location)
            fig, ax = plt.subplots(figsize=(12.5, 6.5))
            _plot_macro_stacked_costs(ax, data, title=f"{g} — {yr} — {location}", ylabel="Annual cost [B$/yr]")

            # ylim costi: specifico per gruppo
            ax.set_ylim(0.0, float(cost_ymax_by_group.get(g, 0.1)))

            # più spazio sotto per le etichette macro molto in basso
            fig.subplots_adjust(top=0.80, bottom=0.36, left=0.08, right=0.98)

            _add_costs_legends(fig, data)

            # overlay LCOE con ylim per gruppo
            lpts = _get_lcoe_points(lcoe_df, group=g, year=yr, location=location)
            _overlay_lcoe_points(ax, lpts, fixed_ymin=0.0, fixed_ymax=float(lcoe_ymax_by_group.get(g, 100.0)))

            out_path = gdir / f"{g}_{yr}_annual_costs_{location}.png"
            fig.savefig(out_path, dpi=220, bbox_inches="tight")
            plt.close(fig)

# ---------- export tabella SAPP in B$/yr ----------
def export_sapp_costs_tables(costs_sapp_df: pd.DataFrame,
                             out_dir: Path,
                             groups: list[str],
                             years: list[str],
                             location: str,
                             tech_cols: list[str]):
    base = Path(out_dir) / "annual_costs"
    base.mkdir(parents=True, exist_ok=True)

    for g in groups:
        d = costs_sapp_df[(costs_sapp_df["group"] == g) & (costs_sapp_df["location"] == location)].copy()
        if d.empty:
            continue
        p = base / f"Annual_Costs_SAPP_{g}.xlsx"
        with ExcelWriter(p, engine="openpyxl") as xw:
            for y in years:
                sub = d[d["year"].astype(str) == str(y)]
                if sub.empty:
                    pd.DataFrame(columns=["Macro","Sub","Scenario", *[TECH_LABEL_COSTS.get(t,t) for t in tech_cols]]).to_excel(xw, sheet_name=str(y), index=False)
                    continue

                pv = (sub.groupby(["macro","sub","scenario","tech"], observed=True)["value_Byr"]
                        .sum(min_count=1)
                        .reset_index())
                pv["tech"] = pd.Categorical(pv["tech"], categories=tech_cols, ordered=True)
                pv = pv.pivot_table(index=["macro","sub","scenario"], columns="tech", values="value_Byr", aggfunc="sum", fill_value=0.0)
                pv = pv.reindex(columns=[c for c in tech_cols if c in pv.columns])
                pv.columns = [TECH_LABEL_COSTS.get(c, c.replace("_New","")) for c in pv.columns]
                pv.sort_index().to_excel(xw, sheet_name=str(y))
        print(f"[OK] Tabella SAPP esportata (B$/yr): {p}")

# ===== ESECUZIONE (solo SAPP) =====
costs_sapp_df = build_annual_costs_sapp_df(GROUP_NAMES, YEARS, SCENARIO_NAMES)
lcoe_system_df = build_lcoe_system_df(GROUP_NAMES, YEARS, SCENARIO_NAMES)

# Scale fisse ma per-gruppo (SAPP)
COST_YMAX_BY_GROUP = compute_groupwise_costs_ymax_sapp(costs_sapp_df)
LCOE_YMAX_BY_GROUP = compute_groupwise_lcoe_ymax_sapp(lcoe_system_df)

print("[Scale per gruppo SAPP]")
for g in GROUP_NAMES:
    print(f"  - {g}: Costi={COST_YMAX_BY_GROUP.get(g, 'n/a')} B$/yr — LCOE={LCOE_YMAX_BY_GROUP.get(g, 'n/a')} $/MWh")

# Plot SAPP con LCOE e ylim per-gruppo
plot_annual_costs_sapp(costs_sapp_df, lcoe_system_df, OUT_BASE,
                       groups=GROUP_NAMES, years=YEARS, location="SAPP",
                       cost_ymax_by_group=COST_YMAX_BY_GROUP,
                       lcoe_ymax_by_group=LCOE_YMAX_BY_GROUP)

# Export tabella SAPP (invariata)
export_sapp_costs_tables(costs_sapp_df, OUT_BASE, GROUP_NAMES, YEARS, "SAPP", COST_TECH_ORDER)
