import pandas as pd
import functions as fc

# --- INPUT ---
latitude = 41.9028
longitude = 12.4964
peak_power = 3.0 # kWp

# --- DATA EXTRACTION ---
# 1. Hourly Data (for plots and irradiance)
df_hourly = fc.get_hourly_data(lat=latitude, lon=longitude, peakpower=peak_power)

# 2. Solar Productivity Data (New API call)
productivity_data = fc.get_solar_productivity(lat=latitude, lon=longitude, peakpower=peak_power)

# --- CALCULATIONS ---
df_hourly['month'] = df_hourly['time'].dt.month
monthly_irradiance = df_hourly.groupby('month')['G(i)'].sum() / 1000 # kWh/m2

# Parse the JSON response from PVcalc for productivity
annual_production = productivity_data['totals']['fixed']['E_y']
monthly_production = {item['month']: item['E_m'] for item in productivity_data['monthly']['fixed']}

# --- RESULTS ---
print("--- RESULTS ---")
print(f"Total Annual Production: {annual_production:.2f} kWh\n")

print("Monthly Production (kWh):")
for month, production in monthly_production.items():
    print(f"Month {month:02d}: {production:.2f}")

# --- PLOTTING ---
fc.plot_data(df_hourly, monthly_irradiance, selected_month=6, selected_day=23)

# --- ECONOMIC ANALYSIS ---
# Compute basic economic performance metrics for the photovoltaic system.
# The calculations below use the energy output obtained above along with
# assumed financial parameters. Adjust the financial parameters as needed
# for your specific project.

# Convert the annual energy to a capacity factor. This expresses
# how effectively the installed power is utilised over the year.
capacity_factor_value = fc.capacity_factor(
    annual_energy_kwh=annual_production,
    rated_power_kw=peak_power
)

# Set up financing assumptions for weighted average cost of capital (WACC).
# Here we assume half of the investment is financed by debt and half by
# equity. Interest and return rates are expressed as fractions (e.g. 0.04 for 4%).
debt_share = 0.5
equity_share = 0.5
debt_interest_rate = 0.04  # 4% annual interest on debt
return_on_equity = 0.08    # 8% required return on equity
wacc_value = fc.wacc(
    debt_share=debt_share,
    equity_share=equity_share,
    debt_interest_rate=debt_interest_rate,
    return_on_equity=return_on_equity
)

# Project lifetime and cost assumptions. CAPEX represents the upfront
# investment cost of the PV system and OPEX represents yearly operating costs.
lifetime_years = 25
capex_eur = 6500.0     # example upfront investment in EUR
opex_annual_eur = 50.0  # example annual operating cost in EUR

# Compute the Levelized Cost of Energy (LCOE) based on a constant cost
# approach. This provides the average cost per kWh over the project lifetime.
lcoe_value = fc.lcoe(
    capex_eur=capex_eur,
    opex_annual_eur=opex_annual_eur,
    annual_energy_kwh=annual_production,
    discount_rate=wacc_value,
    lifetime_years=lifetime_years
)

# Additional economic indicators via a cash-flow model. These parameters
# account for annual degradation, self‑consumption of produced energy,
# remuneration for exported energy, and escalation of prices over time.
escalation_rate = 0.02         # 2% annual price escalation
degradation_rate = 0.005       # 0.5% annual energy degradation
self_consumption_ratio = 0.4    # 40% of energy is self consumed
feed_in_tariff = 0.10          # revenue per kWh exported to the grid (EUR/kWh)
import_price = 0.25            # avoided cost per kWh self consumed (EUR/kWh)
grid_fee = 0.0                 # grid fee per kWh generated

cashflows = fc.cash_flows_model(
    rated_power_kw=peak_power,
    cap_factor=capacity_factor_value,
    lifetime_years=lifetime_years,
    capex_eur=capex_eur,
    opex_year1_eur=opex_annual_eur,
    discount_rate=wacc_value,
    escalation_rate=escalation_rate,
    degradation_rate=degradation_rate,
    self_consumption_ratio=self_consumption_ratio,
    feed_in_tariff_eur_per_kwh=feed_in_tariff,
    import_price_eur_per_kwh=import_price,
    grid_fee_eur_per_kwh=grid_fee
)

# Compute the Net Present Value (NPV), Internal Rate of Return (IRR), and
# simple payback period. These metrics evaluate the profitability of the
# investment using the cash flows defined above.
npv_value = fc.npv(cash_flows=cashflows, discount_rate=wacc_value)
irr_value = fc.irr(cash_flows=cashflows)
payback_year = fc.payback_period(cash_flows=cashflows)

# Compute equivalent uniform annual cost (annuity) for the investment.
annuity_value = fc.annuity(capex_eur=capex_eur, lifetime_years=lifetime_years, discount_rate=wacc_value)

# --- ECONOMIC RESULTS ---
print("\n--- ECONOMIC ANALYSIS ---")
print(f"Capacity factor: {capacity_factor_value:.2%}")
print(f"Weighted average cost of capital (WACC): {wacc_value:.2%}")
print(f"Levelized cost of energy (LCOE): {lcoe_value:.4f} EUR/kWh")
print(f"Net present value (NPV): {npv_value:.2f} EUR")
if irr_value is not None:
    print(f"Internal rate of return (IRR): {irr_value:.2%}")
else:
    print("Internal rate of return (IRR): not computable")
if payback_year is not None:
    print(f"Simple payback period: {payback_year} years")
else:
    print("Simple payback period: no payback within project lifetime")
print(f"Equivalent uniform annual cost (annuity): {annuity_value:.2f} EUR/year")