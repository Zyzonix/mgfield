#Copyright: 2021- R.S. Weigel, 2025 - F. von Bargen
#as posted here: https://github.com/hapi-server/client-python
#orcid: https://orcid.org/0000-0002-9521-5228
#title: hapi-server/client-python: 
#version: v0.2.1
#date-released: 2021-10-06
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from hapiclient import hapi
import math
from tqdm import tqdm
import time
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime, timedelta, timezone
from geopy.geocoders import Nominatim

def calculate_distance(lat1, lat2):
    """Berechnet die Entfernung zwischen zwei Punkten auf der Erde nur auf der Latitude-Achse."""
    distance = abs(lat2 - lat1)
    return distance

def load_valid_observatories(csv_file):
    """Lädt die Liste der Observatorien aus der CSV-Datei und gibt nur die mit Status 'Open' zurück."""
    valid_observatories = {}
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Status'] == 'Open':
                valid_observatories[row['Code']] = {
                    'Name': row['Name'],
                    'Latitude': float(row['Latitude']),
                    'Longitude': float(row['Longitude'])
                }
    return valid_observatories

def get_date_range(option):
    """Gibt das Start- und Enddatum basierend auf der Benutzerauswahl zurück."""
    today = datetime.now(timezone.utc)
    if option == '1':
        start = today - timedelta(days=7)
        stop = today
    elif option == '2':
        start = today - timedelta(days=30)
        stop = today
    else:
        start = datetime.strptime(input("Bitte geben Sie das Startdatum (YYYY-MM-DD) ein: "), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        stop = datetime.strptime(input("Bitte geben Sie das Enddatum (YYYY-MM-DD) ein: "), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return start.strftime("%Y-%m-%dT00:00:00Z"), stop.strftime("%Y-%m-%dT00:00:00Z")

def auto_select_stations(valid_observatories, reference_lat, max_distance):
    """Automatisch alle offenen Stationen auswählen, die sich innerhalb einer bestimmten Entfernung auf der Latitude-Achse befinden."""
    selected_stations = []
    for code, details in valid_observatories.items():
        distance = calculate_distance(reference_lat, details['Latitude'])
        if distance <= max_distance:
            selected_stations.append(code)
    return selected_stations

def main():
    try:
        # CSV-Dateipfad anpassen
        csv_file = os.path.join(os.getcwd(), 'intermagnet/IAGAlist.csv')
        valid_observatories = load_valid_observatories(csv_file)
        
        # Benutzereingaben für den Zeitraum
        print("Bitte wählen Sie den Zeitraum:")
        print("1. Letzte Woche")
        print("2. Letzter Monat")
        print("3. Benutzerdefiniert")
        option = input("Ihre Auswahl (1/2/3): ")
        start, stop = get_date_range(option)
        
        # Abfrage für Intermagnet
        include_intermagnet = input("Möchten Sie Intermagnet-Daten mit einbeziehen? (ja/nein): ").strip().lower()
        if include_intermagnet == 'ja':
            auto_select = input("Möchten Sie alle offenen Stationen auf der Latitude von BUE und mit einer Entfernung von maximal 3 automatisch auswählen? (ja/nein): ").strip().lower()
            if auto_select == 'ja':
                iaga_codes = auto_select_stations(valid_observatories, 53.650, 2)
                print(f"Automatisch ausgewählte Stationen: {', '.join(iaga_codes)}")
            else:
                iaga_input = input("Bitte geben Sie die IAGA-Codes der Stationen ein (durch Kommas getrennt): ").upper()
                iaga_codes = [code.strip() for code in iaga_input.split(',')]
            
            # Validierung der IAGA-Codes
            for code in iaga_codes:
                if code not in valid_observatories:
                    print(f"\033[0;31mError:\033[0m Der IAGA-Code '{code}' ist ungültig oder die Station ist nicht 'Open'.")
                    return

            # Abfrage, ob die eigene Station inkludiert werden soll
            include_own_station = input(
                "Möchten Sie Ihre eigene Station (Latitude: 53.650, Longitude: 9.424) hinzufügen? (ja/nein): "
            ).strip().lower()
            if include_own_station == 'ja':
                own_station_code = 'BUE'
                valid_observatories[own_station_code] = {
                    'Name': 'Eigene Station',
                    'Latitude': 53.650,
                    'Longitude': 9.424
                }
                # BUE wird nicht zu iaga_codes hinzugefügt, um nicht an HAPI weitergegeben zu werden

            # Startzeit erfassen
            start_time = time.time()

            # Datenverarbeitung für Intermagnet starten
            combined_data = process_data(iaga_codes, start, stop, valid_observatories)
            
            # Endzeit erfassen und verstrichene Zeit berechnen
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Anzahl der Datenzeilen und Stationen ermitteln
            num_rows = len(next(iter(combined_data.values()))[0]) if combined_data else 0
            num_stations = len(combined_data)

            print(f"\033[0;32mInfo:\033[0m Verarbeitung abgeschlossen. Verarbeitete Daten: {num_stations} Station(en) mit {num_rows} Datenzeilen in {elapsed_time:.2f} Sekunden.")
            plot_observatory_locations(valid_observatories, iaga_codes)
            save_combined_data_to_csv(combined_data, start, stop)
        else:
            print("Intermagnet-Daten werden nicht einbezogen.")
        
    except Exception as e:
        print(f"\033[0;31mError:\033[0m {str(e)}")

    # Berechne und gebe die Abstände zu BUE aus
    bue_lat = 53.650
    bue_lon = 9.424
    for code in iaga_codes:
        if code in valid_observatories and code != 'BUE':
            obs_lat = valid_observatories[code]['Latitude']
            obs_lon = valid_observatories[code]['Longitude']
            distance = calculate_distance(bue_lat, obs_lat)
            print(f"Abstand von {code} zu BUE: {distance:.2f} ")

def process_data(iaga_codes, start, stop, valid_observatories):
    server = 'https://imag-data.bgs.ac.uk/GIN_V1/hapi'
    parameters = 'Field_Vector'
    opts = {'logging': True, 'usecache': True}

    combined_data = {}
    for iaga_code in tqdm(iaga_codes, desc="Processing data"):
        dataset = f'{iaga_code.lower()}/best-avail/PT1M/xyzf'
        observatory_name = valid_observatories[iaga_code]

        # Daten und Metadaten abrufen
        try:
            data, _ = hapi(server, dataset, parameters, start, stop, **opts)
        except Exception as e:
            print(f"\033[0;31mError:\033[0m {str(e)}")
            continue

        if isinstance(data, np.ndarray) and data.ndim == 1:
            timestamps = [item[0].decode('utf-8') for item in data]
            vectors = np.array([item[1] for item in data])

            # Betrag berechnen
            magnitudes = [math.sqrt(x**2 + y**2 + z**2) for x, y, z in vectors]
            combined_data[iaga_code] = (timestamps, magnitudes, observatory_name)

            # Einzelnen Graphen erstellen
            save_and_plot_magnitude(iaga_code, observatory_name, timestamps, magnitudes, start, stop)
        else:
            print(f"\033[0;31mError:\033[0m Unerwartetes Datenformat für Station {iaga_code}.")

    # Kombinierten Graph erstellen
    if len(combined_data) > 1:
        save_combined_magnitude_plot(combined_data, start, stop)
    
    return combined_data

def save_and_plot_magnitude(iaga_code, observatory_name, timestamps, magnitudes, start, stop):
    output_dir = os.path.join(os.getcwd(), 'intermagnet/output', iaga_code)
    plot_dir = os.path.join(output_dir, 'plots')
    os.makedirs(plot_dir, exist_ok=True)

    # Einzelnen Graph speichern
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, magnitudes, label=f'{observatory_name} ({iaga_code})', color='blue')
    plt.xlabel('Zeit')
    def get_country_from_lat_lon(lat, lon):
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse((lat, lon), language='en')
        if location and 'country' in location.raw['address']:
            return location.raw['address']['country']
        return 'unbekannt'

    country = get_country_from_lat_lon(observatory_name['Latitude'], observatory_name['Longitude'])
    plt.ylabel('Magnetfeldstärke (nT)')
    plt.title(f'Magnetfeldbetrag für {observatory_name["Name"]} ({iaga_code}) in {country}') 
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    # Limit the number of x-axis labels to avoid overloading
    max_xticks = 20
    if len(timestamps) > max_xticks:
        step = len(timestamps) // max_xticks
        plt.xticks(ticks=timestamps[::step], labels=timestamps[::step])

    plot_filename = os.path.join(plot_dir, f'{iaga_code}_magnitude_{start[:10]}_to_{stop[:10]}.png')
    plt.savefig(plot_filename)
    plt.close()

    print(f'Einzelner Graph gespeichert: {plot_filename}')

def save_combined_magnitude_plot(combined_data, start, stop):
    output_dir = os.path.join(os.getcwd(), 'intermagnet/output', 'combined')
    os.makedirs(output_dir, exist_ok=True)

    # Kombinierten Graph speichern
    plt.figure(figsize=(12, 6))
    colors = ['blue', 'green', 'red', 'orange', 'purple']
    for i, (iaga_code, (timestamps, magnitudes, observatory_name)) in enumerate(combined_data.items()):
        plt.plot(timestamps, magnitudes, label=f'{observatory_name} ({iaga_code})', color=colors[i % len(colors)])

    plt.xlabel('Zeit')
    plt.ylabel('Magnetfeldstärke (nT)')
    plt.title('Vergleich der Magnetfeldbeträge zwischen den Observatorien')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    max_xticks = 20
    if len(timestamps) > max_xticks:
        step = len(timestamps) // max_xticks
        plt.xticks(ticks=timestamps[::step], labels=timestamps[::step])
    plot_filename = os.path.join(output_dir, f'combined_magnitude_{start[:10]}_to_{stop[:10]}.png')
    plt.savefig(plot_filename)
    plt.close()

    print(f'Kombinierter Graph gespeichert: {plot_filename}')

def save_combined_data_to_csv(combined_data, start, stop):
    output_dir = os.path.join(os.getcwd(), 'intermagnet/output', 'combined')
    os.makedirs(output_dir, exist_ok=True)
    csv_filename = os.path.join(output_dir, f'combined_data_{start[:10]}_to_{stop[:10]}.csv')

    # Alle Zeitstempel sammeln
    all_timestamps = set()
    for timestamps, _, _ in combined_data.values():
        all_timestamps.update(timestamps)
    all_timestamps = sorted(all_timestamps)

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header = ['Timestamp'] + [f'{iaga_code} (nT)' for iaga_code in combined_data.keys()]
        writer.writerow(header)

        for timestamp in all_timestamps:
            row = [timestamp]
            for iaga_code in combined_data.keys():
                timestamps, magnitudes, _ = combined_data[iaga_code]
                if timestamp in timestamps:
                    index = timestamps.index(timestamp)
                    row.append(magnitudes[index])
                else:
                    row.append('')
            writer.writerow(row)

    print(f'CSV-Datei gespeichert: {csv_filename}')

def plot_observatory_locations(observatories, iaga_codes):
    """Plottet die Standorte der Observatorien auf einer Weltkarte, beschränkt auf die Umgebung der Stationen."""

    # Extrahiere die Längen- und Breitengrade der eingegebenen Stationen
    locations = []
    for code in iaga_codes:
        if code in observatories:
            lat = observatories[code]['Latitude']
            lon = observatories[code]['Longitude']
            locations.append((lon, lat, code))  # Nur ICAO-Kürzel verwenden

    # Füge die eigene Station 'BUE' hinzu, falls sie nicht bereits enthalten ist
    if 'BUE' not in iaga_codes:
        lat = 53.650
        lon = 9.424
        locations.append((lon, lat, 'BUE'))

    if not locations:
        print("Keine gültigen Stationen gefunden.")
        return

    # Erstelle einen GeoDataFrame
    gdf = gpd.GeoDataFrame(
        locations,
        columns=['Longitude', 'Latitude', 'Code'],
        geometry=[Point(lon, lat) for lon, lat, _ in locations]
    )

    # Lade die Weltkarte aus der angegebenen Datei
    natural_earth_file = 'intermagnet/data/ne_110m_admin_0_countries.zip'
    if not os.path.exists(natural_earth_file):
        raise FileNotFoundError(f"Die Datei '{natural_earth_file}' wurde nicht gefunden. Bitte stelle sicher, dass der Pfad korrekt ist.")

    world = gpd.read_file(natural_earth_file)

    # Berechne den Bereich der Karte
    fig, ax = plt.subplots(figsize=(25, 10))
    if fig is None or ax is None:
        raise RuntimeError("Failed to create subplots.")
    min_lon, max_lon = gdf['Longitude'].min() - 5, gdf['Longitude'].max() + 5
    min_lat, max_lat = gdf['Latitude'].min() - 5, gdf['Latitude'].max() + 5

    # Plot erstellen
    fig, ax = plt.subplots(figsize=(25, 10))
    world.plot(ax=ax, color='lightgrey')

    # Karte auf die Umgebung beschränken
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    # Plot der Observatorien
    for x, y, label in zip(gdf['Longitude'], gdf['Latitude'], gdf['Code']):
        gdf[gdf['Code'] == label].plot(ax=ax, color='blue', markersize=45)

    # Beschriftungen hinzufügen (nur ICAO-Kürzel)
    for x, y, label in zip(gdf['Longitude'], gdf['Latitude'], gdf['Code']):
        ha = 'right'
        ax.text(x, y, label, fontsize=12, ha=ha)

    plt.title('Standorte der Observatorien')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    output_dir = os.path.join(os.getcwd(), 'intermagnet/output', 'combined')
    plot_filename = os.path.join(output_dir, f'locations.png')
    plt.savefig(plot_filename)
    plt.close()

    print(f'Kombinierter Graph gespeichert: {plot_filename}')

if __name__ == '__main__':
    main()
