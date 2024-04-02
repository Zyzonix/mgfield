# MGFieldPy - Magnetic field measurement
This software has been developed with OCISLY-ds to measure magnetic fields with a Raspberry Pi.
For more details, please contact OCISLY-ds.

### Installation
**This software is designed to be run on a Debian machine!**
```
git clone https://github.com/Zyzonix/MGFieldPy.git
cd MGFieldPy/
```
To install the service type:
```
sudo cp services/MGFieldPy.service /etc/systemd/system/
sudo systemctl enable MGFieldPy.service
```
Install required python packages:
```
pip3 install mysql-connector
```
Create logfile directory:
```
mkdir -p /var/log/MGFieldPy/
```
**A working mySQL server is required! MariaDB is recommended.**

### Execution
Directly over the console (the programm will interrupt when the window will be closed)
```
python3 main.py
```
Or via the system service
```
sudo systemctl start MGFieldPy.service
```
To view the current status use:
```
sudo systemctl status MGFieldPy.service
```
To view the log/consoleout in realtime use:
```
sudo journalctl -u MGFieldPy.service
```

### Settings
The software can be configured through the config-file named ```config.py```. All values are described with comments above each setting!


### SQL Value Meanings
Table | Value Name | Meaning/Use type
---|---|---
```mgfield```|```avg_result```|Calculated average value from configured measurement interval
```mgfield```|```time_delta```|Time delta of the whole measurement interval, calculating interval: ```finishedTime - startTime - expectedIntervalRunningTime```. This value is actually expected to be ```0```.
```mgfieldraw```|```x_value```|X-Value per measurement
```mgfieldraw```|```y_value```|Y-Value per measurement
```mgfieldraw```|```z_value```|Z-Value per measurement
```mgfieldraw```|```measurement_result```|Calculated average value from the single measurement (calculated from x-,y-, and z-values)
```mgfieldraw```|```measurement_duration```|Time delta of the single measurement
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
