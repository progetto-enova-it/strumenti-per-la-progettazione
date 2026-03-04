import requests
import pandas as pd
import matplotlib.pyplot as plt

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

def plot_data(df, monthly_irradiance, selected_month=6, selected_day=23):
    # ... (Il codice del plotting rimane invariato)
    pass