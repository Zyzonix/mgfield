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
