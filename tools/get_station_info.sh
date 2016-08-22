#!/bin/bash
cd $(dirname "$0")

python get_station_info.py >> ../log/get_station_info.log
