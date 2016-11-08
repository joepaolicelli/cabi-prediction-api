# Capital Bikeshare Availability Predictions

An API to provide predictions of bike availability for Washington D.C.'s
[Capital Bikeshare](https://www.capitalbikeshare.com/).

### Table of Contents
- [Overview](#overview)
- [API Format](#api-format)
- [Prediction Methodology](#prediction-methodology-overview)
- [Data](#data)
- [Setup](#setup)

## Overview

This API uses [Capital Bikeshare](https://www.capitalbikeshare.com/) data and
weather data to predict the chances a bikeshare station will have at least one
bike available and at least one empty bike dock available, given a date and
time. For each bikeshare station, models are built using [random
forests](https://en.wikipedia.org/wiki/Random_forest) based on historical
station status data and historical weather data. The API then accepts a
datetime string and a location string (such as a street address or
neighborhood), and returns the closest stations and the availability
predictions.

This project uses Python 3. Data analysis and machine learning were done using
[Pandas](http://pandas.pydata.org/) and
[scikit-learn](http://scikit-learn.org/stable/). The API was built using
[Falcon](https://falconframework.org/).

[I](https://joepaolicelli.com/) built this project during the summer of 2016
while I was an intern at [Mission Data](https://www.missiondata.com/). I
greatly appreciate their permission to open source this project and post it
here on GitHub, as well as their help and guidance on this project.

Mission Data is currently hosting this API (not currently for public use), with
some minor enhancements, as well as [a web application where you can get
predictions](https://labs.missiondata.com/CapitalBikeshareML). The original
version of the web application was written by me in Angular 2 with TypeScript,
but significant UI and style improvements have since been made by others at
Mission Data.

A series of three lab notes have been published detailing the progression of
this project. The
[first](https://journal.missiondata.com/lab-notes-machine-learning-and-capital-bikeshare-c240125c0a1)
[two](https://journal.missiondata.com/lab-notes-machine-learning-part-ii-724dc1628faf)
explain the machine learning that is used to make the predictions, and [the
third](https://journal.missiondata.com/introduction-1be76e0e8b35) discusses a
conversational Slack bot (which I did not have a part in building) that uses
the API. I also gave a brief presentation about the project at the [sixth CaBi
Hack Night
meetup](https://www.meetup.com/Transportation-Techies/events/234652961/) in
November 2016, slides are available
[here](https://joepaolicelli.com/files/cabi_presentation.pdf).

This project was my first time using Python and doing any machine learning.
Given that, I'm pretty happy with how it turned out. As with any complex
project (but perhaps this one in particular due to my inexperience and limited
timeframe), there are many potential improvements and expansions. This code is
licensed under the open source MIT License, and you are more than welcome to
build on it or adapt it for your own uses.

## API Format

The API accepts a POST request and expects a json body of the following
structure:

```
{
  "datetime": string (date and time),
  "location": string[,
  "station_count": integer]
}
```

The `datetime` string is passed to Panda's `to_datetime` method, so any
reasonable format (including unix timestamps) should be fine.

The `location` string is passed to the Google Maps API to get
coordinates, so specific addresses or general neighboorhoods (anything
that works with Google Maps, actually) will work.

An optional `station_count` parameter can be passed to specify the
number of closest stations that should be returned. The default is
five.

For example:
```
{
  "datetime": "November 08, 2016 5:00 pm",
  "location": "Capitol Hill",
  "station_count": 5
}
```

The response may look like this (some stations removed for brevity):

```
{
  "address": "Capitol Hill, Washington, DC, USA",
  "date": "Tuesday November 08, 2016",
  "time": "05:00 PM",
  "forecast": {
    "tempC": 17,
    "tempF": 62,
    "condition": "Partly Cloudy"
  },
  "status": "success",
  "stations": [
    {
      "name": "Eastern Market \/ 7th & North Carolina Ave SE",
      "distance": 256.5717285669,
      "prediction": {
        "empty": 0.20066666666667,
        "full": 0
      }
    },
    ...
  ]
}
```

## Prediction Methodology Overview

For each bikeshare station, models are built using [random
forests](https://en.wikipedia.org/wiki/Random_forest) based on historical
station status data and historical weather data. Specifically, the features
used are:
- Seven binary features, one for each day of the week
- Minute of the day
- Month
- Temperature
- Hourly Precipitation

Values are roughly scaled to be between 0 and 1, inclusive. (The one exception
is temperature, which is scaled to be between -1 and 1.)

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
automatically that include recent data. Alternatively, you can just import
historical data once with `import_data.py` and `import_weather_data.py`, and
then run `build_models.sh` once. However, your models will likely get less
accurate as time progresses.

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
