
#%%
import pandas as pd
import matplotlib.pyplot as plt
from pull_pv_data import estrai_dati_orari

# --- INPUT ---
latitudine = 41.9028
longitudine = 12.4964
potenza_picco = 3.0 # kWp

# --- ESTRAZIONE DATI ---
df = estrai_dati_orari(lat=latitudine, lon=longitudine, peakpower=potenza_picco)

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

#%%
# --- GRAFICI ---

# Plot 1: Irradianza mensile
plt.subplot(1, 2, 2)
irradianza_mensile.plot(kind='bar', color='orange')
plt.title('Irradianza Totale Mensile')
plt.xlabel('Mese')
plt.ylabel('Irradianza (kWh/m²)')
plt.xticks(rotation=0)
plt.grid(axis='y')

plt.tight_layout()
plt.show()


# Filtriamo un giorno specifico (es. 15 Giugno)
giorno_scelto = df[(df['time'].dt.month == 6) & (df['time'].dt.day == 23)]

plt.figure(figsize=(12, 5))

# Plot 1: Produzione giornaliera
plt.subplot(1, 2, 1)
plt.plot(giorno_scelto['time'].dt.hour, giorno_scelto['P'] / 1000, color='blue')
plt.title('Produzione Oraria - 15 Giugno')
plt.xlabel('Ora del giorno')
plt.ylabel('Potenza (kW)')
plt.grid(True)



# %%
