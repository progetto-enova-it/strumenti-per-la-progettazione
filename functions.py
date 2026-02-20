import requests
import pandas as pd
import matplotlib.pyplot as plt

def estrai_dati_orari(lat, lon, peakpower, loss=14, tilt=35, azimuth=0):
    url = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"
    parametri = {
        "lat": lat, "lon": lon, "peakpower": peakpower,
        "loss": loss, "angle": tilt, "aspect": azimuth,
        "outputformat": "json", "startyear": 2020, "endyear": 2020,
        "pvcalculation": 1
    }
    
    risposta = requests.get(url, params=parametri)
    risposta.raise_for_status()
    
    dati = risposta.json()['outputs']['hourly']
    df = pd.DataFrame(dati)
    df['time'] = pd.to_datetime(df['time'], format='%Y%m%d:%H%M')
    
    return df

def plotting(df, irradianza_mensile, mese_scelto=6, giorno_scelto=23):
    plt.figure(figsize=(12, 5))

    # Plot 1: Produzione giornaliera
    giorno_filtrato = df[(df['time'].dt.month == mese_scelto) & (df['time'].dt.day == giorno_scelto)]
    
    plt.subplot(1, 2, 1)
    plt.plot(giorno_filtrato['time'].dt.hour, giorno_filtrato['P'] / 1000, color='blue')
    plt.title(f'Produzione Oraria - {giorno_scelto}/{mese_scelto}')
    plt.xlabel('Ora del giorno')
    plt.ylabel('Potenza (kW)')
    plt.grid(True)

    # Plot 2: Irradianza Mensile
    plt.subplot(1, 2, 2)
    irradianza_mensile.plot(kind='bar', color='orange')
    plt.title('Irradianza Totale Mensile')
    plt.xlabel('Mese')
    plt.ylabel('Irradianza (kWh/m²)')
    plt.xticks(rotation=0)
    plt.grid(axis='y')

    plt.tight_layout()
    plt.show()