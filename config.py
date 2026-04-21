import os

# ── Project root ──────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# ── Data paths ────────────────────────────────────────────────────────────────
DATA_RAW        = os.path.join(PROJECT_ROOT, "data", "raw")
DATA_PROCESSED  = os.path.join(PROJECT_ROOT, "data", "processed")

# ── Output paths ──────────────────────────────────────────────────────────────
FIGURES_DIR     = os.path.join(PROJECT_ROOT, "figures")
REPORTS_DIR     = os.path.join(PROJECT_ROOT, "reports")

# ── E-OBS file names (to be downloaded in notebook 01) ────────────────────────
EOBS_TG_FILE = os.path.join(DATA_RAW, "tg_ens_mean_0.25deg_reg_v31.0e.nc")
EOBS_RR_FILE = os.path.join(DATA_RAW, "rr_ens_mean_0.25deg_reg_v31.0e.nc")

# ── Country list (30 European countries) ──────────────────────────────────────
COUNTRIES = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Czechia",
    "Denmark", "Estonia", "Finland", "France", "Germany",
    "Greece", "Hungary", "Ireland", "Italy", "Latvia",
    "Lithuania", "Luxembourg", "Netherlands", "Norway", "Poland",
    "Portugal", "Romania", "Serbia", "Slovakia", "Slovenia",
    "Spain", "Sweden", "Switzerland", "Ukraine", "United Kingdom"
]

# ── Analysis parameters ───────────────────────────────────────────────────────
REFERENCE_PERIOD_START  = 1991
REFERENCE_PERIOD_END    = 2020
ANALYSIS_START          = 1950
ANALYSIS_END            = 2024
SIGNIFICANCE_LEVEL      = 0.05

# ── Figure settings ───────────────────────────────────────────────────────────
FIGURE_DPI      = 300
RANDOM_STATE    = 42