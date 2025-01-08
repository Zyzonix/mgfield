import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from tqdm import tqdm

# Datei Pfade für beide Messstationen und Sysstats
file_paths = {
    'station1': 'path',
    'station2': 'path'
}
sysstats_paths = {
    'station1': 'path',
    'station2': 'path'
}

# Funktion zur Verarbeitung der Daten einer Messstation
def process_station_data(station_name, file_path, sysstats_path):
    # Datei laden (mit korrekt angegebenem Trennzeichen und Anführungszeichen)
    data = pd.read_csv(file_path, delimiter=';', quotechar='"')

    # Konvertiere die Zeitspalte in ein pandas-Datetime-Objekt
    data['time_utc'] = pd.to_datetime(data['time_utc'], format='%Y-%m-%d %H:%M:%S.%f')

    # Berechne den gleitenden Mittelwert der vorherigen Werte
    data['rolling_mean'] = data['out_value'].astype(float).rolling(window=5, min_periods=1).mean().shift(1)

    # Erkennen von Ausreißern (Abweichung > 55 vom gleitenden Mittelwert)
    ausreisser = data[np.abs(data['out_value'].astype(float) - data['rolling_mean']) > 55]

    # Speichern der Ausreißer in eine Textdatei mit Differenzen
    ausreisser[['time_utc', 'x_value', 'y_value', 'z_value', 'out_value', 'rolling_mean']].to_csv(
        f'ausreisser_{station_name}.txt', index=False, sep='\t'
    )

    # Entfernen der Ausreißer aus den Daten
    data = data[np.abs(data['out_value'].astype(float) - data['rolling_mean']) <= 55]

    # Zeitintervall auf 5-Minuten-Basis berechnen
    data['time_interval'] = data['time_utc'].dt.floor('5T')

    # Neue Spalte mit der gewünschten Berechnung
    data['avg_without'] = np.sqrt(
        (data['x_value'].astype(float) - data['out_value'].astype(float))**2 +
        (data['y_value'].astype(float) - data['out_value'].astype(float))**2 +
        (data['z_value'].astype(float) - data['out_value'].astype(float))**2
    )

    # Monatliche Gruppierung
    data['month'] = data['time_utc'].dt.to_period('M')  # Monatliches Intervall
    monthly_groups = data.groupby('month')

    # Wöchentliche Gruppierung
    data['week'] = data['time_utc'].dt.to_period('W')  # Wöchentliches Intervall
    weekly_groups = data.groupby('week')

    # Sicherstellen, dass die Ausgabeordner existieren
    monthly_output_dir = f'monthly_graphs_{station_name}'
    weekly_output_dir = f'weekly_graphs_{station_name}'
    os.makedirs(monthly_output_dir, exist_ok=True)
    os.makedirs(weekly_output_dir, exist_ok=True)

    # Generiere einen Graphen für jeden Monat
    print(f"Generiere monatliche Graphen für {station_name}...")
    for month, group in tqdm(monthly_groups, desc=f"Monatliche Graphen {station_name}"):
        monthly_result = group.groupby('time_interval')['avg_without'].mean().reset_index()

        plt.figure(figsize=(12, 6))
        plt.plot(monthly_result['time_interval'], monthly_result['avg_without'], label=f'Monat: {month}')
        plt.xlabel('Zeitintervall (alle 5 Minuten)')
        plt.ylabel('Durchschnittlicher Abstand (avg_without)')
        plt.title(f'Analyse der magnetischen Feldwerte - {month} - {station_name}')
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)

        # Setze die Ticks auf das Datum
        xticks = pd.date_range(start=monthly_result['time_interval'].min(), 
                               end=monthly_result['time_interval'].max(), 
                               freq='D')
        plt.xticks(xticks, xticks.strftime('%Y-%m-%d'), rotation=45)
        plt.tight_layout()

        graph_path = os.path.join(monthly_output_dir, f'magnetfeld_analyse_{month}.png')
        plt.savefig(graph_path)
        plt.close()

    # Generiere einen Graphen für jede Woche
    print(f"Generiere wöchentliche Graphen für {station_name}...")
    for week, group in tqdm(weekly_groups, desc=f"Wöchentliche Graphen {station_name}"):
        weekly_result = group.groupby('time_interval')['avg_without'].mean().reset_index()

        plt.figure(figsize=(12, 6))
        plt.plot(weekly_result['time_interval'], weekly_result['avg_without'], label=f'Woche: {week}')
        plt.xlabel('Zeitintervall (alle 5 Minuten)')
        plt.ylabel('Durchschnittlicher Abstand (avg_without)')
        plt.title(f'Analyse der magnetischen Feldwerte - Woche {week} - {station_name}')
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)

        # Setze die Ticks auf das Datum und die Uhrzeit
        xticks = pd.date_range(start=weekly_result['time_interval'].min(), 
                               end=weekly_result['time_interval'].max(), 
                               freq='12h')
        plt.xticks(xticks, xticks.strftime('%Y-%m-%d %H:%M'), rotation=45)
        plt.tight_layout()

        # Ersetze ungültige Zeichen im Dateinamen
        week_str = str(week).replace('/', '-')
        graph_path = os.path.join(weekly_output_dir, f'magnetfeld_analyse_{week_str}.png')
        plt.savefig(graph_path)
        plt.close()

    print(f"Alle Graphen für {station_name} wurden generiert und gespeichert.")

    # Laden der sysstats.csv Datei
    sysstats_data = pd.read_csv(sysstats_path, delimiter=';', quotechar='"')

    # Check if 'time_utc' column exists
    if 'time_utc' not in sysstats_data.columns:
        raise KeyError(f"The 'time_utc' column is not found in the {sysstats_path} file.")

    # Konvertiere die Zeitspalte in ein pandas-Datetime-Objekt
    sysstats_data['time_utc'] = pd.to_datetime(sysstats_data['time_utc'], format='%Y-%m-%d %H:%M:%S')

    # Generiere einen Graphen für sysstats
    plt.figure(figsize=(12, 6))
    plt.plot(sysstats_data['time_utc'], sysstats_data['cpu_usage'], label='CPU Usage')
    plt.xlabel('Zeit')
    plt.ylabel('CPU Usage')
    plt.title('Systemstatistiken')
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Speichern des Graphen
    sysstats_graph_path = f'sysstats_graph_{station_name}.png'
    plt.savefig(sysstats_graph_path)
    plt.close()

    print(f"Sysstats Graph für {station_name} wurde generiert und gespeichert.")

    # Berechne die Korrelation zwischen CPU Usage und avg_without für jeden Monat
    print(f"Berechne die Korrelation zwischen CPU Usage und avg_without für {station_name}...")
    data['avg_without'] = np.sqrt(
        (data['x_value'].astype(float) - data['out_value'].astype(float))**2 +
        (data['y_value'].astype(float) - data['out_value'].astype(float))**2 +
        (data['z_value'].astype(float) - data['out_value'].astype(float))**2
    )
    merged_data = pd.merge_asof(data.sort_values('time_utc'), sysstats_data.sort_values('time_utc'), on='time_utc')

    monthly_correlations = merged_data.groupby(merged_data['time_utc'].dt.to_period('M')).apply(
        lambda x: x['cpu_usage'].corr(x['avg_without'])
    )

    # Ausgabe der Korrelationen
    for month, corr in monthly_correlations.items():
        print(f"Korrelation für {month} ({station_name}): {corr}")

# Verarbeite die Daten für beide Messstationen
for station_name, file_path in file_paths.items():
    process_station_data(station_name, file_path, sysstats_paths[station_name])
