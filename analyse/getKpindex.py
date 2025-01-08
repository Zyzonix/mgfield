#!/usr/bin/env python3

"""
getKpindex.py
===================================
GFZ German Research Centre for Geosciences (CC BY 4.0)
Author I. Wehner
created with Python 3.8.10
last modified on 25 May 2022
to run getKpindex function run:  from getKpindex import getKpindex
-----------------------------------
"""

from datetime import datetime
import json, urllib.request
import csv

# Zeitraum
starttime = '2024-12-01'
endtime = '2024-12-05'
index = 'Kp'
status = 'all'

def __checkdate__(starttime, endtime):
    if starttime > endtime:
        raise NameError("Error! Start time must be before or equal to end time")
    return True

def __checkIndex__(index):
    if index not in ['Kp', 'ap', 'Ap', 'Cp', 'C9', 'Hp30', 'Hp60', 'ap30', 'ap60', 'SN', 'Fobs', 'Fadj']:
        raise IndexError("Error! Wrong index parameter! \nAllowed are only the string parameter: 'Kp', 'ap', 'Ap', 'Cp', 'C9', 'Hp30', 'Hp60', 'ap30', 'ap60', 'SN', 'Fobs', 'Fadj'")
    return True

def __checkstatus__(status):
    if status not in ['all', 'def']:
        raise IndexError("Error! Wrong option parameter! \nAllowed are only the string parameter: 'def'")
    return True

def __addstatus__(url, status):
    if status == 'def':
        url = url + '&status=def'
    return url

def getKpindex(starttime, endtime, index, status='all'):
    """
    Download 'Kp', 'ap', 'Ap', 'Cp', 'C9', 'Hp30', 'Hp60', 'ap30', 'ap60', 'SN', 'Fobs' or 'Fadj' index data from kp.gfz-potsdam.de
    date format for starttime and endtime is 'yyyy-mm-dd' or 'yyyy-mm-ddTHH:MM:SSZ'
    """
    result_t = 0
    result_index = 0
    result_s = 0

    if len(starttime) == 10 and len(endtime) == 10:
        starttime = starttime + 'T00:00:00Z'
        endtime = endtime + 'T23:59:00Z'

    try:
        d1 = datetime.strptime(starttime, '%Y-%m-%dT%H:%M:%SZ')
        d2 = datetime.strptime(endtime, '%Y-%m-%dT%H:%M:%SZ')

        __checkdate__(d1, d2)
        __checkIndex__(index)
        __checkstatus__(status)

        time_string = "start=" + d1.strftime('%Y-%m-%dT%H:%M:%SZ') + "&end=" + d2.strftime('%Y-%m-%dT%H:%M:%SZ')
        url = 'https://kp.gfz-potsdam.de/app/json/?' + time_string + "&index=" + index
        if index not in ['Hp30', 'Hp60', 'ap30', 'ap60', 'Fobs', 'Fadj']:
            url = __addstatus__(url, status)

        webURL = urllib.request.urlopen(url)
        binary = webURL.read()
        text = binary.decode('utf-8')

        try:
            data = json.loads(text)
            result_t = tuple(data["datetime"])
            result_index = tuple(data[index])
            if index not in ['Hp30', 'Hp60', 'ap30', 'ap60', 'Fobs', 'Fadj']:
                result_s = tuple(data["status"])
        except:
            print(text)

    except NameError as er:
        print(er)
    except IndexError as er:
        print(er)
    except ValueError:
        print("Error! Wrong datetime string")
        print("Both dates must be the same format.")
        print("Datetime strings must be in format yyyy-mm-dd or yyyy-mm-ddTHH:MM:SSZ")
    except urllib.error.URLError:
        print("Connection Error\nCan not reach " + url)
    finally:
        return result_t, result_index, result_s

# Daten abrufen
time, index_values, status_values = getKpindex(starttime, endtime, index, status)

# Ergebnisse in CSV-Datei schreiben
output_file = "Kpindex_output.csv"

try:
    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Header schreiben
        writer.writerow(["datetime", index, "status"])
        # Daten schreiben
        for t, i, s in zip(time, index_values, status_values):
            writer.writerow([t, i, s])
    print(f"Daten erfolgreich in {output_file} gespeichert.")
except Exception as e:
    print(f"Fehler beim Schreiben der CSV-Datei: {e}")

# Ergebnis anzeigen
print(time, index_values, status_values)
