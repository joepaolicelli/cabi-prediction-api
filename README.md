# Capital Bikeshare Availability Predictions

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

For example, to run on [Gunicorn](http://gunicorn.org/):

```
pip install gunicorn
gunicorn api:app
```

### Data Collectors

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
