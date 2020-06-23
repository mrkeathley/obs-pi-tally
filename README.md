# obs-pi-tally
OBS Tally Lights using Raspberry Pi

## Instructions

Install the required dependencies on the Raspberry Pi:

`apt-get install python-pip3`

`pip3 install RPi.GPIO`

`pip3 install websocket_client`
    
Move the files onto the Rapsberry Pi -- the default location is `/home/pi`

Edit the `config.ini` to contain the OBS host address and the source to watch.

Run with `python3 obs_tally.py`

## Run on start

Configure the `obs_tally.service` file to contain the path and working directory where the tally service lives.

Copy the `obs_tally.service` file into `/etc/systemd/system/`

Then enable it with `sudo systemctl enable obs_tally.service`

