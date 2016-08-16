#!/bin/bash
cd $(dirname "$0")

# Set these here if not set in crontab
# export WUNDERGROUND_KEY=
# export CABI_DB=

mkdir -p ../log
python weather_recorder.py >> ../log/weather_recorder.log
