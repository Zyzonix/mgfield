from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit
from werkzeug.utils import safe_join
import plotly.graph_objects as go
import os
import pandas as pd
from hapiclient import hapi
from datetime import datetime, timedelta, timezone
import csv
import numpy as np
import math
from tqdm import tqdm

app = Flask(__name__)
socketio = SocketIO(app)

# Ordner für gespeicherte Plots (zum Download)
DOWNLOAD_FOLDER = '/tmp/plots'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Benutzerdefinierter Filter für die Datumsformatierung
@app.template_filter('datetimeformat')
def datetimeformat(value):
    dt = datetime.strptime(value, '%Y-%m-%dT%H:%M')
    return dt.strftime('%d.%m.%Y %H:%M')

def load_valid_observatories(csv_file):
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
    print(f"Valid observatories loaded: {valid_observatories}")  # Debugging-Ausgabe
    return valid_observatories

def process_data(iaga_codes, start, stop, valid_observatories):
    server = 'https://imag-data.bgs.ac.uk/GIN_V1/hapi'
    parameters = 'Field_Vector'
    opts = {'logging': True, 'usecache': True}

    combined_data = {}
    for i, iaga_code in enumerate(tqdm(iaga_codes, desc="Processing data")):
        dataset = f'{iaga_code.lower()}/best-avail/PT1M/xyzf'
        observatory_name = valid_observatories[iaga_code]['Name']

        try:
            data, _ = hapi(server, dataset, parameters, start, stop, **opts)
        except Exception as e:
            print(f"Error: {str(e)}")
            continue

        if isinstance(data, np.ndarray) and data.ndim == 1:
            timestamps = [item[0].decode('utf-8') for item in data]
            vectors = np.array([item[1] for item in data])

            magnitudes = [math.sqrt(x**2 + y**2 + z**2) for x, y, z in vectors]
            filtered_data = [(t, m) for t, m in zip(timestamps, magnitudes) if m <= 160000]

            if filtered_data:
                filtered_timestamps, filtered_magnitudes = zip(*filtered_data)
                combined_data[iaga_code] = (filtered_timestamps, filtered_magnitudes, observatory_name)
            else:
                print(f"Error: Alle Datenpunkte für Station {iaga_code} überschreiten den Schwellenwert von 160.000.")
        else:
            print(f"Error: Unerwartetes Datenformat für Station {iaga_code}.")

        # Senden Sie den Fortschritt an den Client
        socketio.emit('progress', {'progress': int((i + 1) / len(iaga_codes) * 100)})

    if combined_data:
        save_and_plot_magnitude(combined_data, start, stop, valid_observatories)
    
    return combined_data

def save_and_plot_magnitude(combined_data, start, stop, valid_observatories):
    output_dir = os.path.join(app.config['DOWNLOAD_FOLDER'], 'combined')
    os.makedirs(output_dir, exist_ok=True)

    # Plot der Magnetfeldstärke
    fig = go.Figure()
    for iaga_code, (timestamps, magnitudes, observatory_name) in combined_data.items():
        fig.add_trace(go.Scatter(x=timestamps, y=magnitudes, mode='lines', name=f'{observatory_name} ({iaga_code})'))

    fig.update_layout(
        title='Vergleich der Magnetfeldbeträge zwischen den Observatorien',
        xaxis_title='Zeit',
        yaxis_title='Magnetfeldstärke (nT)',
        xaxis=dict(tickangle=45),
        legend_title='Observatorien',
        template='plotly_white',  # Setzen des Plotly White Themes
        margin=dict(l=0, r=0, t=0, b=0)  # Entfernen der Ränder
    )

    plot_filename = os.path.join(output_dir, f'combined_magnitude_{start[:10]}_to_{stop[:10]}.html')
    fig.write_html(plot_filename)

    print(f'Kombinierter Graph gespeichert: {plot_filename}')

    # Plot der Weltkarte mit den Stationen
    map_fig = go.Figure()

    # Manuell hinzugefügte Station BUE
    bue_station = {'Longitude': 9.424, 'Latitude': 53.651, 'Name': 'BUE'}
    map_fig.add_trace(go.Scattergeo(
        lon=[bue_station['Longitude']],
        lat=[bue_station['Latitude']],
        text='BUE',
        mode='markers+text',
        textposition='top center',  # Text über dem Marker
        marker=dict(
            size=8,
            color='red',
            symbol='circle'
        ),
        name='BUE'
    ))

    for iaga_code in combined_data.keys():
        observatory = valid_observatories[iaga_code]
        map_fig.add_trace(go.Scattergeo(
            lon=[observatory['Longitude']],
            lat=[observatory['Latitude']],
            text=iaga_code,
            mode='markers+text',
            textposition='top center',  # Text über dem Marker
            marker=dict(
                size=8,
                color='blue',
                symbol='circle'
            ),
            name=f"{observatory['Name']} ({iaga_code})"
        ))

    map_fig.update_layout(
        title='Position der ausgewählten Stationen',
        geo=dict(
            showland=True,
            landcolor='rgb(243, 243, 243)',
            subunitcolor='rgb(217, 217, 217)',
            countrycolor='rgb(217, 217, 217)',
            showcountries=True,
            showcoastlines=True,
            coastlinecolor='rgb(217, 217, 217)',
            projection_type='equirectangular',
            lonaxis=dict(
                range=[-20, 40]  # Längengradbereich anpassen
            ),
            lataxis=dict(
                range=[30, 70]  # Breitengradbereich anpassen
            )
        ),
        template='plotly_white',
        margin=dict(l=0, r=0, t=0, b=0)  # Entfernen der Ränder
    )

    map_plot_filename = os.path.join(output_dir, f'stations_map_{start[:10]}_to_{stop[:10]}.html')
    map_fig.write_html(map_plot_filename)

    print(f'Weltkarte der Stationen gespeichert: {map_plot_filename}')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        stations = request.form.getlist('station')
        custom_station = request.form.get('custom_station').upper()
        if custom_station and len(custom_station) == 3:
            stations.append(custom_station)
        start = request.form.get('start', '2024-09-01T00:00')
        stop = request.form.get('stop', '2024-10-01T00:00')
        
        print(f"Benutzer hat folgende Zeiten eingegeben: Start = {start}, End = {stop}, Stationen = {stations}")

        csv_file = os.path.join(os.getcwd(), 'intermagnet/IAGAlist.csv')
        valid_observatories = load_valid_observatories(csv_file)

        invalid_stations = [station for station in stations if station not in valid_observatories]
        if invalid_stations:
            print(f"Fehler: Stationen {invalid_stations} nicht in valid_observatories")  # Debugging-Ausgabe
            return render_template('index.html', message=f"Fehler: Ungültige Stationen {invalid_stations}.", start=start, stop=stop)

        # Fügen Sie die manuell hinzugefügte Station BUE hinzu
        if 'BUE' not in stations:
            stations.append('BUE')
            valid_observatories['BUE'] = {'Name': 'BUE', 'Latitude': 53.651, 'Longitude': 9.424}

        combined_data = process_data(stations, start, stop, valid_observatories)

        if combined_data:
            plot_filename = f'combined_magnitude_{start[:10]}_to_{stop[:10]}.html'
            map_plot_filename = f'stations_map_{start[:10]}_to_{stop[:10]}.html'
            return render_template('index.html', message="Plots erfolgreich erstellt!", plot_url=f'combined/{plot_filename}', map_plot_url=f'combined/{map_plot_filename}', start=start, stop=stop)
        else:
            return render_template('index.html', message="Fehler: Keine Daten gefunden.", start=start, stop=stop)
    
    return render_template('index.html', message="Bitte die Start- und Endzeit eingeben.", start=None, stop=None)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
