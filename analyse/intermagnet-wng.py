import os
import numpy as np
import matplotlib.pyplot as plt
import csv
from hapiclient import hapi
import math
from tqdm import tqdm

def main():
    try:
        wng_demo()
    except Exception as e:
        print("\033[0;31mError:\033[0m " + str(e))

def wng_demo():
    server = 'https://imag-data.bgs.ac.uk/GIN_V1/hapi'
    dataset = 'wng/best-avail/PT1M/xyzf' 
    #iaga-code is the IAGA code for the INTERMAGNET observatory (WNG)
    #publication-state is one of:
    #reported for raw data from the sensor
    #adjusted for data with provisional adjustments made
    #quasi-def for data within 5nT of their final values
    #definitive for final published data
    #best-avail for the best available from the above data types (default)
    #cadence is one of pt1m for minute data or pt1s for second data
    #orientation is one of:
    #native for the orientation of the data as supplied by the data provider
    #xyzf for a Cartesian reference frame (default)
    #hdzf for a Cylindrical reference frame
    #diff for a Spherical reference frame
    parameters = 'Field_Vector'
    start = '2024-05-01T00:00:00Z'
    stop = '2024-11-30T00:00:00Z'
    opts = {'logging': True, 'usecache': True}

    # Daten und Metadaten abrufen
    data, meta = hapi(server, dataset, parameters, start, stop, **opts)

    # Überprüfen, ob die Daten als numpy.ndarray vorliegen und die richtige Dimension haben
    if isinstance(data, np.ndarray) and data.ndim == 1:
        # Extrahiere die Zeitstempel und die Vektorkomponenten aus den Daten
        timestamps = [item[0].decode('utf-8') for item in data]
        vectors = np.array([item[1] for item in data])

        # Verzeichnisse für die CSV-Datei und Diagramme erstellen
        csv_dir = '/Users/florianvonbargen/Desktop/analyseSQLpy/intermagnet/output'
        plot_dir = '/Users/florianvonbargen/Desktop/analyseSQLpy/intermagnet/output'
        monthly_plot_dir = os.path.join(plot_dir, 'monthly')
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(plot_dir, exist_ok=True)
        os.makedirs(monthly_plot_dir, exist_ok=True)

        # Intelligente Benennung der CSV-Datei nach dem Start- und Enddatum
        csv_filename = os.path.join(csv_dir, f'magnetic_field_data_{start[:10]}_to_{stop[:10]}.csv')
        
        # CSV-Datei erstellen und Daten speichern
        with open(csv_filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Timestamp', 'X-Komponente', 'Y-Komponente', 'Z-Komponente', 'Betrag'])
            for i, ts in tqdm(enumerate(timestamps), desc="Speichern der CSV-Daten", total=len(timestamps)):
                x = vectors[i, 0]
                y = vectors[i, 1]
                z = vectors[i, 2]
                magnitude = math.sqrt(x**2 + y**2 + z**2)  # Berechne den Betrag
                csvwriter.writerow([ts, x, y, z, magnitude])

        print(f'Die Daten wurden in der Datei {csv_filename} gespeichert.')

        # Einzelne Komponenten des Magnetfeldvektors plotten und speichern
        for i, component in tqdm(enumerate(['X', 'Y', 'Z']), desc="Generierung der Graphen", total=3):
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, vectors[:, i], label=f'{component}-Komponente')
            plt.xlabel('Zeit')
            plt.ylabel('Magnetfeldstärke (nT)')
            plt.title(f'Magnetfeld {component}-Komponente über Zeit bei Wingst, Deutschland (WNG)')
            #plt.legend()
            plt.grid(True)
            
            # Intelligente Auswahl der X-Achsenbeschriftungen
            num_ticks = min(len(timestamps), 20)  # Maximale Anzahl von Beschriftungen auf 20 begrenzen
            step = len(timestamps) // num_ticks  # Schrittweite berechnen

            plt.xticks(timestamps[::step], rotation=45)  # Nur jede x-te Beschriftung anzeigen
            plt.tight_layout()

            # Dateiname für das gespeicherte Diagramm
            plot_filename = os.path.join(plot_dir, f'magnetic_field_{component}_component.png')
            plt.savefig(plot_filename)
            plt.close()

            print(f'Plot der {component}-Komponente wurde gespeichert unter: {plot_filename}')

        # Plot für den Betrag des Magnetfeldvektors erstellen und speichern
        magnitudes = [math.sqrt(x**2 + y**2 + z**2) for x, y, z in vectors]
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, magnitudes, label='Betrag des Magnetfeldvektors')
        plt.xlabel('Zeit')
        plt.ylabel('Magnetfeldstärke (nT)')
        plt.title('Betrag des Magnetfeldvektors über Zeit bei Wingst, Deutschland (WNG)')
        #plt.legend()
        plt.grid(True)

        # Intelligente Auswahl der X-Achsenbeschriftungen für den Betrag
        plt.xticks(timestamps[::step], rotation=45)  # Nur jede x-te Beschriftung anzeigen
        plt.tight_layout()

        # Dateiname für den Betrag-Diagramm
        magnitude_plot_filename = os.path.join(plot_dir, 'magnetic_field_magnitude.png')
        plt.savefig(magnitude_plot_filename)
        plt.close()

        print(f'Plot des Betrags wurde gespeichert unter: {magnitude_plot_filename}')

        # Monatliche Graphen erstellen und speichern
        current_month = None
        monthly_data = []
        for i, ts in enumerate(timestamps):
            month = ts[:7]  # Extrahiere Jahr und Monat
            if month != current_month:
                if monthly_data:
                    save_monthly_plot(current_month, monthly_data, monthly_plot_dir)
                current_month = month
                monthly_data = []
            monthly_data.append((ts, vectors[i]))

        # Letzten Monat speichern
        if monthly_data:
            save_monthly_plot(current_month, monthly_data, monthly_plot_dir)

    else:
        print("Unexpected data type loaded or data format.")

def save_monthly_plot(month, data, plot_dir):
    timestamps, vectors = zip(*data)
    vectors = np.array(vectors)
    magnitudes = [math.sqrt(x**2 + y**2 + z**2) for x, y, z in vectors]
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, magnitudes, label='Betrag des Magnetfeldvektors')
    plt.xlabel('Zeit')
    plt.ylabel('Magnetfeldstärke (nT)')
    plt.title(f'Betrag des Magnetfeldvektors für {month} Station Wingst, Deutschland (WNG)')
        #plt.legend()
    plt.grid(True)
        # Intelligente Auswahl der X-Achsenbeschriftungen
    num_ticks = min(len(timestamps), 20)  # Maximale Anzahl von Beschriftungen auf 20 begrenzen
    step = len(timestamps) // num_ticks  # Schrittweite berechnen

    plt.xticks(timestamps[::step], rotation=45)  # Nur jede x-te Beschriftung anzeigen
    plt.tight_layout()

        # Dateiname für das gespeicherte Diagramm
    plot_filename = os.path.join(plot_dir, f'magnetic_field__component_{month}.png')
    plt.savefig(plot_filename)
    plt.close()

    print(f'Monatlicher Plot der-Komponente für {month} wurde gespeichert unter: {plot_filename}')

if __name__ == '__main__':
    main()
