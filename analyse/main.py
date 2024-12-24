import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Datei laden (mit korrekt angegebenem Trennzeichen und Anführungszeichen)
file_path = 'daten.csv'  # Pfad zur CSV-Datei
data = pd.read_csv(file_path, delimiter=';', quotechar='"')

# Konvertiere die Zeitspalte in ein pandas-Datetime-Objekt
data['time_utc'] = pd.to_datetime(data['time_utc'], format='%Y-%m-%d %H:%M:%S.%f')

# Berechnung der Differenzen zu vorherigem und nächstem Wert
data['diff_prev'] = data['out_value'].astype(float).diff().abs()
data['diff_next'] = data['out_value'].astype(float).diff(-1).abs()

# Erkennen von Ausreißern (Differenz > 50 zu vorherigem und nächstem Wert)
ausreisser = data[(data['diff_prev'] > 50) & (data['diff_next'] > 50)]

# Speichern der Ausreißer in eine Textdatei
ausreisser[['time_utc', 'x_value', 'y_value', 'z_value', 'out_value']].to_csv(
    'ausreisser.txt', index=False, sep='\t'
)

# Entfernen der Ausreißer aus den Daten
data = data[~((data['diff_prev'] > 50) & (data['diff_next'] > 50))]

# Zeitintervall auf 5-Minuten-Basis berechnen
data['time_interval'] = data['time_utc'].dt.floor('5T')

# Neue Spalte mit der gewünschten Berechnung
data['avg_without'] = np.sqrt(
    (data['x_value'].astype(float) - data['out_value'].astype(float))**2 +
    (data['y_value'].astype(float) - data['out_value'].astype(float))**2 +
    (data['z_value'].astype(float) - data['out_value'].astype(float))**2
)

# Daten gruppieren nach 5-Minuten-Intervallen und Mittelwert berechnen
result = data.groupby('time_interval')['avg_without'].mean().reset_index()

# Monatliche Gruppierung
data['month'] = data['time_utc'].dt.to_period('M')  # Monatliches Intervall
monthly_groups = data.groupby('month')

# Wöchentliche Gruppierung
data['week'] = data['time_utc'].dt.to_period('W')  # Wöchentliches Intervall
weekly_groups = data.groupby('week')

# Sicherstellen, dass der Ausgabeordner existiert
output_dir = 'weekly_monthly_graphs'
os.makedirs(output_dir, exist_ok=True)

# Generiere einen Graphen für jeden Monat
for month, group in monthly_groups:
    monthly_result = group.groupby('time_interval')['avg_without'].mean().reset_index()

    plt.figure(figsize=(12, 6))
    plt.plot(monthly_result['time_interval'], monthly_result['avg_without'], label=f'Monat: {month}')
    plt.xlabel('Zeitintervall (alle 5 Minuten)')
    plt.ylabel('Durchschnittlicher Abstand (avg_without)')
    plt.title(f'Analyse der magnetischen Feldwerte - {month}')
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    graph_path = os.path.join(output_dir, f'magnetfeld_analyse_{month}.png')
    plt.savefig(graph_path)
    plt.close()

# Generiere einen Graphen für jede Woche
for week, group in weekly_groups:
    weekly_result = group.groupby('time_interval')['avg_without'].mean().reset_index()

    plt.figure(figsize=(12, 6))
    plt.plot(weekly_result['time_interval'], weekly_result['avg_without'], label=f'Woche: {week}')
    plt.xlabel('Zeitintervall (alle 5 Minuten)')
    plt.ylabel('Durchschnittlicher Abstand (avg_without)')
    plt.title(f'Analyse der magnetischen Feldwerte - Woche {week}')
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Ersetze ungültige Zeichen im Dateinamen
    week_str = str(week).replace('/', '-')
    graph_path = os.path.join(output_dir, f'magnetfeld_analyse_{week_str}.png')
    plt.savefig(graph_path)
    plt.close()

print("Alle Graphen wurden generiert und gespeichert.")
