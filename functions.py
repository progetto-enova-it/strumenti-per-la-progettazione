import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import numpy_financial as npf
from typing import List, Optional


def get_hourly_data(lat, lon, peakpower, loss=14, tilt=None, azimuth=None, tech=None, mountingplace=None):
    url = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"
    params = {
        "lat": lat, "lon": lon, "peakpower": peakpower,
        "loss": loss, "outputformat": "json", 
        "startyear": 2020, "endyear": 2020, "pvcalculation": 1
    }
    
    if tilt is not None: params["angle"] = tilt
    if azimuth is not None: params["aspect"] = azimuth
    if tilt is None or azimuth is None: params["optimalangles"] = 1
    if tech is not None: params["pvtechchoice"] = tech
    if mountingplace is not None: params["mountingplace"] = mountingplace
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()['outputs']['hourly']
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'], format='%Y%m%d:%H%M')
    return df

def get_solar_productivity(lat, lon, peakpower, loss=14, tilt=None, azimuth=None, tech=None, mountingplace=None):
    url = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"
    params = {
        "lat": lat, "lon": lon, "peakpower": peakpower,
        "loss": loss, "outputformat": "json"
    }
    
    if tilt is not None: params["angle"] = tilt
    if azimuth is not None: params["aspect"] = azimuth
    if tilt is None or azimuth is None: params["optimalangles"] = 1
    if tech is not None: params["pvtechchoice"] = tech
    if mountingplace is not None: params["mountingplace"] = mountingplace
    
    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()['outputs']

def plot_data(df, monthly_irradiance, monthly_production, selected_month=6, selected_day=23):
    plt.figure(figsize=(15, 5))

    # Grafico 1: Produzione Oraria
    filtered_day = df[(df['time'].dt.month == selected_month) & (df['time'].dt.day == selected_day)]
    plt.subplot(1, 3, 1)
    plt.plot(filtered_day['time'].dt.hour, filtered_day['P'] / 1000, color='blue')
    plt.title(f'Produzione Oraria - {selected_day}/{selected_month}')
    plt.xlabel('Ora del giorno')
    plt.ylabel('Potenza (kW)')
    plt.grid(True)

    # Grafico 2: Irradianza Mensile
    plt.subplot(1, 3, 2)
    monthly_irradiance.plot(kind='bar', color='orange')
    plt.title('Irradianza Mensile Totale')
    plt.xlabel('Mese')
    plt.ylabel('Irradianza (kWh/m²)')
    plt.xticks(rotation=0)
    plt.grid(axis='y')

    # Grafico 3: Produzione Mensile
    plt.subplot(1, 3, 3)
    pd.Series(monthly_production).plot(kind='bar', color='green')
    plt.title('Produzione Mensile Totale')
    plt.xlabel('Mese')
    plt.ylabel('Energia (kWh)')
    plt.xticks(rotation=0)
    plt.grid(axis='y')

    plt.tight_layout()
    plt.show()

    #ECONOMIC ANALYSIS
def capacity_factor(annual_energy_kwh: float, rated_power_kw: float) -> float:
    """Compute capacity factor from annual energy and installed power.

    Args:
        annual_energy_kwh: Energy produced in one year (kWh).
        rated_power_kw: Installed (rated) power (kW).

    Returns:
        Capacity factor (dimensionless): annual_energy / (rated_power * 8,760 h).
    """
    if rated_power_kw <= 0:
        raise ValueError("Rated power must be greater than zero.")
    return annual_energy_kwh / (rated_power_kw * 8760.0)


def wacc(
    debt_share: float,
    equity_share: float,
    debt_interest_rate: float,
    return_on_equity: float,
) -> float:
    """Compute WACC (Weighted Average Cost of Capital).

    Args:
        debt_share: Share financed by debt (0..1).
        equity_share: Share financed by equity (0..1). debt_share + equity_share must be 1.
        debt_interest_rate: Annual interest rate on debt (fraction, e.g., 0.04 for 4%).
        return_on_equity: Required annual return on equity (fraction).

    Returns:
        WACC as an annual fraction.
    """
    if not np.isclose(debt_share + equity_share, 1.0):
        raise ValueError("debt_share + equity_share must equal 1.")
    return debt_share * debt_interest_rate + equity_share * return_on_equity


def crf(discount_rate: float, lifetime_years: int) -> float:
    """Capital recovery factor (CRF).

    CRF is used to annualize a one-time CAPEX into an equivalent constant
    annual payment over the asset lifetime.

    Args:
        discount_rate: Discount rate (fraction).
        lifetime_years: Economic lifetime in years.

    Returns:
        CRF = i(1+i)^n / ((1+i)^n - 1). If i=0, returns 1/n.
    """
    i = float(discount_rate)
    n = int(lifetime_years)
    if n <= 0:
        raise ValueError("lifetime_years must be positive.")
    if i == 0:
        return 1.0 / n
    return (i * (1 + i) ** n) / ((1 + i) ** n - 1)


def lcoe(
    capex_eur: float,
    opex_annual_eur: float,
    annual_energy_kwh: float,
    discount_rate: float,
    lifetime_years: int,
) -> float:
    """Levelized Cost of Energy (LCOE) using a CRF-based approximation.

    Assumes:
      - Single upfront CAPEX.
      - Constant annual OPEX.
      - Constant annual energy (no degradation).

    For a more detailed model (degradation, escalation, multiple replacements),
    use ``cash_flows_model`` and compute LCOE as PV(costs) / PV(energy).

    Args:
        capex_eur: Total upfront cost (EUR).
        opex_annual_eur: Constant annual operating cost (EUR/year).
        annual_energy_kwh: Constant annual energy (kWh/year).
        discount_rate: Discount rate (fraction).
        lifetime_years: Project lifetime (years).

    Returns:
        LCOE in EUR/kWh.
    """
    if annual_energy_kwh <= 0:
        raise ValueError("annual_energy_kwh must be greater than zero.")
    annualized_cost = capex_eur * crf(discount_rate, lifetime_years) + opex_annual_eur
    return annualized_cost / annual_energy_kwh


def npv(cash_flows: List[float], discount_rate: float) -> float:
    """Net Present Value (NPV) of a cash-flow series.

    Args:
        cash_flows: Annual cash flows where cash_flows[0] is year-0 (typically negative CAPEX).
        discount_rate: Discount rate (fraction).

    Returns:
        NPV (EUR).
    """
    return float(npf.npv(discount_rate, cash_flows))


def irr(cash_flows: List[float]) -> Optional[float]:
    """Internal Rate of Return (IRR) for a cash-flow series.

    Args:
        cash_flows: Annual cash flows where cash_flows[0] is year-0 (negative CAPEX).

    Returns:
        IRR as a fraction, or None if it cannot be computed.
    """
    try:
        value = npf.irr(cash_flows)
    except Exception:
        return None
    return float(value) if value is not None else None


def payback_period(cash_flows: List[float]) -> Optional[int]:
    """Simple payback period (non-discounted).

    Computes the first year where cumulative cash flow becomes >= 0.

    Args:
        cash_flows: Annual cash flows.

    Returns:
        Year index (0..n) where payback occurs, or None if never paid back.
    """
    cumulative = 0.0
    for year, cf in enumerate(cash_flows):
        cumulative += cf
        if cumulative >= 0:
            return year
    return None



def cash_flows_model(
    rated_power_kw: float,
    cap_factor: float,
    lifetime_years: int,
    capex_eur: float,
    opex_year1_eur: float,
    discount_rate: float,
    escalation_rate: float,
    degradation_rate: float,
    self_consumption_ratio: float,
    feed_in_tariff_eur_per_kwh: float,
    import_price_eur_per_kwh: float,
    grid_fee_eur_per_kwh: float = 0.0,
) -> List[float]:
    """Generate annual project cash flows for a simplified PV business case.

    Model assumptions:
      - Energy in year 1: rated_power_kw * cap_factor * 8,760.
      - Energy degrades each year by degradation_rate.
      - Prices/costs escalate each year by escalation_rate.
      - Revenue comes from:
           * Self-consumed energy valued at import_price (avoided purchase).
           * Exported energy valued at feed-in tariff.
      - OPEX is an annual cost (year 1 value) that escalates.
      - Grid fee is a variable cost per kWh generated (applied to total generation).

    Args:
        rated_power_kw: Installed PV power (kW).
        cap_factor: Average capacity factor (0..1).
        lifetime_years: Project lifetime (years).
        capex_eur: Upfront investment (EUR) applied as year-0 negative cash flow.
        opex_year1_eur: OPEX in year 1 (EUR/year).
        discount_rate: Discount rate (fraction). Not used inside this function, but kept
            for convenience/consistency with analyses that use the same parameter set.
        escalation_rate: Annual escalation rate for prices and costs (fraction).
        degradation_rate: Annual degradation rate of energy output (fraction).
        self_consumption_ratio: Fraction of generated energy self-consumed (0..1).
        feed_in_tariff_eur_per_kwh: Export remuneration (EUR/kWh).
        import_price_eur_per_kwh: Retail electricity import price (EUR/kWh).
        grid_fee_eur_per_kwh: Variable grid fee applied to generated energy (EUR/kWh).

    Returns:
        List of annual cash flows (length lifetime_years+1). Index 0 is year 0.
    """
    if rated_power_kw <= 0:
        raise ValueError("rated_power_kw must be greater than zero.")
    if not (0 <= cap_factor <= 1):
        raise ValueError("cap_factor must be between 0 and 1.")
    if not (0 <= self_consumption_ratio <= 1):
        raise ValueError("self_consumption_ratio must be between 0 and 1.")
    if lifetime_years <= 0:
        raise ValueError("lifetime_years must be positive.")

    year1_energy_kwh = rated_power_kw * cap_factor * 8760.0
    # Note: discount_rate is not used here; it is applied when computing NPV.
    cashflows: List[float] = [-float(capex_eur)]

    for year in range(1, lifetime_years + 1):
        annual_energy = year1_energy_kwh * (1.0 - degradation_rate) ** (year - 1)
        self_energy = annual_energy * self_consumption_ratio
        exported_energy = annual_energy - self_energy

        esc = (1.0 + escalation_rate) ** (year - 1)

        revenue = (
            self_energy * import_price_eur_per_kwh
            + exported_energy * feed_in_tariff_eur_per_kwh
        ) * esc

        opex = float(opex_year1_eur) * esc
        grid_cost = float(grid_fee_eur_per_kwh) * annual_energy * esc

        cashflows.append(revenue - opex - grid_cost)

    return cashflows


def annuity(capex_eur: float, lifetime_years: int, discount_rate: float) -> float:
    """Equivalent uniform annual cost (annuity) for a given CAPEX.

    Args:
        capex_eur: Upfront investment (EUR).
        lifetime_years: Project lifetime (years).
        discount_rate: Discount rate (fraction).

    Returns:
        Equivalent annual payment (EUR/year).
    """
    return float(capex_eur) * crf(discount_rate, lifetime_years)