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
fc.plot_data(df_hourly, monthly_irradiance, monthly_production, selected_month=6, selected_day=23)