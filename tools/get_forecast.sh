#!/bin/bash
cd $(dirname "$0")

python get_forecast.py >> ../log/get_forecast.log
