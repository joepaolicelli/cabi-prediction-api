# Capital Bikeshare Availability Predictions

An API to provide predictions of bike availability for Washington D.C.'s
[Capital Bikeshare](https://www.capitalbikeshare.com/).

## Data

All dates in the database are stored in US/Eastern time. Included scripts to
import data convert dates and times to US/Eastern (if needed) before storing
the data.

### Scripts to Record Data

Scripts are provided to store current bikeshare and weather data for future
use in building models. See the Setup section of this file for setup
instructions.

Data Sources are the [official Capital Bikeshare station status
feed](https://feeds.capitalbikeshare.com/stations/stations.xml) and the
[Weather Underground
API](https://www.wunderground.com/weather/api/d/docs?d=index).

### Tools to Import Historical Data

#### Capital Bikeshare

Data Source: [Capital Bikeshare
Tracker](http://cabitracker.com/outage_history.php)
- Times are in US/Eastern.
- Data can be exported into CSV files.

Import with `tools/import_data.py`.

#### Weather

Data Source: NOAA's
[ISD Lite Datasets](http://www1.ncdc.noaa.gov/pub/data/noaa/isd-lite/)
- Times are in UTC.

Import with `tools/import_weather_data.py`.

### Database Tables

- bike_count: Bike station data in the format of counts of bikes and empty
  spaces. This is the format saved by the `cabi_recorder` script.
- outage: Bike station data in the format of outages (instances of empty or
  full stations) This is the format imported by the `import_data` tool.
- weather: Weather data saved by the `weather_recorder` script.
- weather_isd: Weather data imported by the `import_weather_data` tool.
- forecast: Upcoming hourly forecasts.
- station_info: Stores metadata about stations.

## Setup

Python 3 must be installed.

A postgres database is required. The environmental variable `CABI_DB` should
be set to a connection string of the format
`username:password@host:port/db_name`.

The environmental variable `WUNDERGROUND_KEY` must be set to a valid API key
for the [Weather Underground
API](https://www.wunderground.com/weather/api/d/docs?d=index).

The environmental variable `GMAPS_KEY` must be set to a valid API key for
[Google Maps Web
Services](https://developers.google.com/maps/web-services/overview).

The environmental variables `API_USER` and `API_PASS` must be set to the
username and password that is required to access the prediction API.

Dependencies can be installed with pip:

```
pip install -r requirements.txt
```

### API

The API is built using [Falcon](https://falconframework.org/), and can be
run on any [WSGI server](https://www.python.org/dev/peps/pep-3333/).

Review the start of the `passenger_wsgi.py` file and modify it to fit your
setup. `INTERP` allows the correct Python executable to be found if you are
using [virtualenv](https://virtualenv.pypa.io/en/stable/), and must be set
correctly (or removed along with the corresponding code if not needed).

The API is set up to run easily on
[Passenger](https://www.phusionpassenger.com/) using `passenger_wsgi.py`.

Alternatively, to run on [Gunicorn](http://gunicorn.org/):

```
pip install gunicorn
gunicorn passenger_wsgi:app
```

### Scripts

A number of scripts should be run regularly to keep the data and models
updated. Shell scripts are provided in the `tools` folder to run the proper
python code and keep logs in the `log` folder. These scripts should be kept
in the `tools` folder, otherwise the paths of the files they refer to will
have to be changed.

The included scripts are:

- `cabi_recorder.sh`: Stores current bikeshare station data, for future use
in building models.
- `weather_recorder.sh`: Stores current weather data, for future use in
building models.
- `get_station_info.sh`: Stores the current list of bikeshare stations.
- `build_models.sh`: Builds models for all bikeshare stations.
- `get_forecast.sh`: Stores upcoming hourly forecasts.

Technically, the only script that must be run regularly is `get_forecast.sh`.
Hourly weather forecasts are only available for ten days, so the API will only
be able to make predictions for ten days from the last time the script was
run.

`get_station_info.sh` must be run at least once, but should be run more often,
as Capital Bikeshare adds and removes stations somewhat often.

Running `cabi_recorder.sh` and `weather_recorder.sh` regularly, and then
running `build_models.sh` occasionally, will allow new models to be created
automatically will recent data. Alternatively, you can just import historical
data once with `import_data.py` and `import_weather_data.py`, and then run
`build_models.sh` once. However, your models will likely get less accurate
as time progresses.

All scripts are quick except for `build_models.sh`, which may take several
hours to run. We recommend running this weekly or every other week.

Running the scripts with cron can be done as follows:
```
# Feel free to change the frequencies as needed.
@weekly /full/path/CapitalBikeshareML/tools/build_models.sh
*/5 * * * * /full/path/CapitalBikeshareML/tools/cabi_recorder.sh
*/20 * * * * /full/path/CapitalBikeshareML/tools/get_forecast.sh
@daily /full/path/CapitalBikeshareML/tools/get_station_info.sh
*/30 * * * * /full/path/CapitalBikeshareML/tools/weather_recorder.sh
```

cron must be set up so the scripts can find the `python` command and can
access the `CABI_DB` environmental variable. `weather_recorder.sh` also needs
to access the `WUNDERGROUND_KEY` variable. The environmental variables (and the
PATH, if needed) can be set in the crontab with some versions of cron. Other
options [can be found
here](http://stackoverflow.com/questions/2229825/where-can-i-set-environment-variables-that-crontab-will-use).
