# obs-pi-tally
OBS Tally Lights using Raspberry Pi

[See them in action](https://imgur.com/TWroxMK)

In our use case we wanted lights attached to a specific camera that might appear in multiple scenes. To accomplish this, this script tracks a OBS source by name even if it appears in multiple scenes. 

If the source is live the tally light is red. If the source is in preview the light is yellow. And if the source is not in use in either location the light is green.

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

