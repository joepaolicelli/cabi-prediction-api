# Capital Bikeshare Availability Predictions

An API to provide predictions of bike availability for Washington D.C.'s
[Capital Bikeshare](https://www.capitalbikeshare.com/).

## Data

All data in the database is stored in US/Eastern time. Included scripts to
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

## Setup

Python 3 must be installed.

A postgres database is required. The environmental variable `CABI_DB` should
be set to a connection string of the format
`username:password@host:port/db_name`.

The environmental variable `WUNDERGROUND_KEY` must be set to a valid API key
for the [Weather Underground
API](https://www.wunderground.com/weather/api/d/docs?d=index).

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

### Data Collector Scripts

Two scripts, `cabi_recorder.sh` and `weather_recorder.sh`, are provided in the
`tools` folder to collect and store current bikeshare station data and weather
data in the database. They are intended to be set as cron jobs, for example:

```
# Set both scripts to run every five minutes.
*/5 * * * * /full/path/CapitalBikeshareML/tools/cabi_recorder.sh
*/5 * * * * /full/path/CapitalBikeshareML/tools/weather_recorder.sh
```

cron must be set up so the scripts can find the `python` command and can
access the `CABI_DB` environmental variable. `weather_recorder.sh` also needs
to access the `WUNDERGROUND_KEY` variable. The environmental variables (and the
PATH, if needed) can be set in the crontab with some versions of cron. Other
options [can be found
here](http://stackoverflow.com/questions/2229825/where-can-i-set-environment-variables-that-crontab-will-use).
