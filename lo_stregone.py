#%%
import pandas as pd
import functions as fc

# --- INPUT ---
latitudine = 41.9028
longitudine = 12.4964
potenza_picco = 3.0 # kWp

# --- ESTRAZIONE DATI ---
df = fc.estrai_dati_orari(lat=latitudine, lon=longitudine, peakpower=potenza_picco)

# --- CALCOLI TOTALI ---
df['mese'] = df['time'].dt.month

# P è in Watt, dividiamo per 1000 per avere kWh. G(i) è in W/m2.
produzione_mensile = df.groupby('mese')['P'].sum() / 1000 
irradianza_mensile = df.groupby('mese')['G(i)'].sum() / 1000 
produzione_annua = produzione_mensile.sum()

print(f"--- RISULTATI ---")
print(f"Produzione Totale Annua: {produzione_annua:.2f} kWh\n")
print("Produzione Mensile (kWh):")
print(produzione_mensile.round(2))

# --- GRAFICI ---
fc.plotting(df, irradianza_mensile, mese_scelto=6, giorno_scelto=23)