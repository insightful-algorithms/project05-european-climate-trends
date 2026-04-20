"""
src/analysis.py
---------------
Reusable functions for P05 European Climate Trends.

All functions are documented with docstrings. Mathematics is derived
in the notebooks before these functions are called.
"""

import numpy as np
import pandas as pd
import pymannkendall as mk
from scipy import stats


def compute_annual_mean(da, year_start, year_end):
    """
    Compute annual mean of an xarray DataArray over a given year range.

    Parameters
    ----------
    da : xarray.DataArray
        Daily time series with a 'time' dimension.
    year_start : int
        First year of the analysis period (inclusive).
    year_end : int
        Last year of the analysis period (inclusive).

    Returns
    -------
    pandas.Series
        Annual mean values indexed by year.
    """
    da_slice = da.sel(time=slice(str(year_start), str(year_end)))
    annual = da_slice.resample(time="YE").mean()
    years = annual.time.dt.year.values
    values = annual.values
    return pd.Series(values, index=years, name="annual_mean")


def compute_anomaly(series, ref_start, ref_end):
    """
    Compute anomaly series relative to a reference period mean.

    The anomaly for year t is defined as:
        a_t = T_t - T_bar_ref
    where T_bar_ref is the mean over [ref_start, ref_end].

    Parameters
    ----------
    series : pandas.Series
        Annual mean values indexed by year.
    ref_start : int
        First year of the reference period (inclusive).
    ref_end : int
        Last year of the reference period (inclusive).

    Returns
    -------
    pandas.Series
        Anomaly values indexed by year.
    """
    ref_mean = series.loc[ref_start:ref_end].mean()
    return series - ref_mean


def ols_trend(series):
    """
    Fit OLS linear trend to an annual time series.

    Model: y_t = beta_0 + beta_1 * t + epsilon_t

    The slope beta_1 is the trend rate in units per year.
    Multiply by 10 for units per decade.

    Parameters
    ----------
    series : pandas.Series
        Annual values indexed by year (integer index).

    Returns
    -------
    dict with keys:
        slope        : float - trend rate per year
        slope_decade : float - trend rate per decade
        intercept    : float
        r_squared    : float
        p_value      : float
        ci_lower     : float - 95% CI lower bound (per decade)
        ci_upper     : float - 95% CI upper bound (per decade)
        slope_se     : float - standard error of slope
    """
    years = series.index.values.astype(float)
    values = series.values.astype(float)

    mask = ~np.isnan(values)
    years_clean = years[mask]
    values_clean = values[mask]

    n = len(years_clean)
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        years_clean, values_clean
    )

    t_crit = stats.t.ppf(0.975, df=n - 2)
    ci_lower = (slope - t_crit * std_err) * 10
    ci_upper = (slope + t_crit * std_err) * 10

    return {
        "slope":        slope,
        "slope_decade": slope * 10,
        "intercept":    intercept,
        "r_squared":    r_value ** 2,
        "p_value":      p_value,
        "ci_lower":     ci_lower,
        "ci_upper":     ci_upper,
        "slope_se":     std_err,
    }


def mann_kendall_trend(series):
    """
    Apply Mann-Kendall trend test and Sen's slope estimator.

    The Mann-Kendall test is non-parametric. It tests whether there is
    a monotonic trend without assuming any distributional form.

    Sen's slope is the median of all pairwise slopes:
        Q_ij = (y_j - y_i) / (t_j - t_i) for all i < j

    Parameters
    ----------
    series : pandas.Series
        Annual values indexed by year (integer index).

    Returns
    -------
    dict with keys:
        trend        : str  - 'increasing', 'decreasing', or 'no trend'
        z_stat       : float - standardised Mann-Kendall Z statistic
        p_value      : float
        sens_slope   : float - Sen's slope per year
        sens_decade  : float - Sen's slope per decade
        significant  : bool - True if p_value < 0.05
    """
    values = series.dropna().values.astype(float)

    result = mk.original_test(values)

    return {
        "trend":       result.trend,
        "z_stat":      result.z,
        "p_value":     result.p,
        "sens_slope":  result.slope,
        "sens_decade": result.slope * 10,
        "significant": result.p < 0.05,
    }


def trend_summary(series, country, variable):
    """
    Compute full trend summary for one country and one variable.

    Combines OLS and Mann-Kendall results into a single summary dict
    suitable for building a results DataFrame.

    Parameters
    ----------
    series : pandas.Series
        Annual values indexed by year.
    country : str
        Country name.
    variable : str
        Variable name, e.g. 'temperature' or 'precipitation'.

    Returns
    -------
    dict
        Combined OLS and Mann-Kendall results with country and variable labels.
    """
    ols = ols_trend(series)
    mk_result = mann_kendall_trend(series)

    return {
        "country":          country,
        "variable":         variable,
        "ols_slope_decade": ols["slope_decade"],
        "ols_ci_lower":     ols["ci_lower"],
        "ols_ci_upper":     ols["ci_upper"],
        "ols_r_squared":    ols["r_squared"],
        "ols_p_value":      ols["p_value"],
        "mk_z":             mk_result["z_stat"],
        "mk_p_value":       mk_result["p_value"],
        "mk_trend":         mk_result["trend"],
        "sens_decade":      mk_result["sens_decade"],
        "significant":      mk_result["significant"],
    }


def data_quality_report(da, country_name):
    """
    Assess data quality for a country's extracted time series.

    Checks for missing values by year and flags years where more than
    10% of daily observations are missing.

    Parameters
    ----------
    da : xarray.DataArray
        Daily time series for a single country (1D, time dimension only).
    country_name : str
        Country name for labelling.

    Returns
    -------
    pandas.DataFrame
        Year-level quality report with columns:
        year, n_obs, n_missing, pct_missing, quality_flag.
    """
    df = da.to_series().rename("value").reset_index()
    df["year"] = df["time"].dt.year

    quality = (
        df.groupby("year")["value"]
        .agg(
            n_obs="count",
            n_missing=lambda x: x.isna().sum()
        )
        .reset_index()
    )

    quality["pct_missing"] = (
        quality["n_missing"] / (quality["n_obs"] + quality["n_missing"]) * 100
    )
    quality["quality_flag"] = quality["pct_missing"].apply(
        lambda x: "FAIL" if x > 10 else "PASS"
    )
    quality.insert(0, "country", country_name)

    return quality