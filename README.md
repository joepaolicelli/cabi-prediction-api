# Capital Bikeshare Availability Predictions

## Data Collectors

### Bike Station Status

See `tools/cabi_recorder.py`.

### Weather

See `tools/weather_recorder.py`.

## Setup

A postgres database is required. The environmental variable `CABI_DB` should
be set to a connection string of the format
`username:password@host:port/db_name`.

The environmental variable `WUNDERGROUND_KEY` must be set to a valid API key
for the [Weather Underground
API](https://www.wunderground.com/weather/api/d/docs?d=index).

Dependencies can be installed with pip:

```
pip install -r requirements.txt
```
