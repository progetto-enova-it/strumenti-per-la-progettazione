
import requests
import pandas as pd

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

    # Converte la stringa del tempo in formato data/ora
    df['time'] = pd.to_datetime(df['time'], format='%Y%m%d:%H%M')
    return df