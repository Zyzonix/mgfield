# MGFieldPy - Magnetic field measurement
This software has been developed with OCISLY-ds to measure magnetic fields with a Raspberry Pi.
For more details, please contact OCISLY-ds.

[![OS-Type](https://img.shields.io/badge/OS%20Type-Linux-blue)]()
[![Python-Version](https://img.shields.io/badge/Python-3.9.2-blue)]()

### Installation
**This software is designed to be run on a Debian machine (e.g. Raspberry Pi)!**
First navigate to ```/opt/```:
```
cd /opt
```
Then install all required APT-packages:
```
sudo apt install mariadb-server git 
```
If required, also install ```phpmyadmin``` and ```libapache2-mod-php``` to make PHP work with Apache. After that clone the repository:
```
git clone https://github.com/Zyzonix/MGFieldPy.git
cd MGFieldPy/
```
Now all required software is downloaded.

To install the service type:
```
sudo cp services/MGField.service /etc/systemd/system/
```

Enable the service with:
```
sudo systemctl enable MGField.service
```

Install required python packages:
```
sudo apt install python3-psutil i2c-tools libgpiod-dev python3-libgpiod ./packages/* 
```
The usage of ```pip3``` depends on your system's configuration. Python packages on some systems like Debian are managed via ```apt```.
```
sudo pip3 install mysql-connector
```
Install additional python packages for physical sensor:
```
sudo pip3 install --upgrade RPi.GPIO adafruit-blinka
```
And  finally create the logfile directory:
```
sudo mkdir -p /var/log/MGField/
```


### Execution
Directly over the console (the programm will interrupt when the window will be closed)
```
python3 main.py
```
Or via the system service
```
sudo systemctl start MGField.service
```
To view the current status use:
```
sudo systemctl status MGField.service
```
To view the log/consoleout in realtime use:
```
sudo journalctl -u MGField.service
```

### Settings
The software can be configured through the config-file named ```config.py```. All values are described with comments above each setting!

- Thereby that collecting all values from each measurement (x, y, z and out) might be to heavy for a Raspberry Pi, there's a switch called ```storeAllRawData``` in the config that can be used to en-/disable the storing of this data.
- Also a specific path to the temperature sensor must be provided config. If the device can't be opened the return value of the sensor will be 0.00. The right format of the sensor's path is for example: ```/sys/bus/w1/devices/28-01204b515089/w1_slave```


### SQL Value Meanings
**Each table contains two rows:**
Value Name | Meaning/Use type
---|---
```time_utc```|Timestamp of value in **UTC**
```time_local```|Timestamp of value in local time (```Europe/Berlin```/ ```+02:00```)

**All other values are table-specific:**
Table | Value Name | Meaning/Use type
---|---|---
```main```|```avg_result```|Calculated average value from configured measurement interval
```main```|```time_delta```|Time delta of the whole measurement interval, calculating interval: ```finishedTime - startTime - expectedIntervalRunningTime```. This value is actually expected to be ```0```.
```rawmeasurements```|```x_value```|X-Value per measurement
```rawmeasurements```|```y_value```|Y-Value per measurement
```rawmeasurements```|```z_value```|Z-Value per measurement
```rawmeasurements```|```out_value```|OUT-Value per measurement
```allmeasurements```|```measurement_result```|Calculated average value from the single measurement (calculated from x-,y-, and z-values)
```allmeasurements```|```measurement_duration```|Time delta of the single measurement
```netstats```|```hostname```|Local hostname from ```/etc/hosts```
```netstats```|```local_ip```|Local IP
```sysstats```|```cpu_speed```|CPU Speed in MHz
```sysstats```|```cpu_usage```|Current CPU usage in %
```sysstats```|```ram_total```|Total RAM in MB
```sysstats```|```ram_free```|Free RAM in MB
```sysstats```|```ram_used```|Used RAM in MB
```sysstats```|```ram_cached```|Cached RAM in MB
```sysstats```|```ram_free_wcache_perc```|Free RAM in % with cache
```sysstats```|```ram_free_wocache_perc```|Free RAM in % without cache
```temperature```|```temperature_value```|Current temperature in °C
