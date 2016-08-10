#!/bin/bash
cd $(dirname "$0")

# Set this here if not set in crontab
# export CABI_DB=

mkdir -p ../log
python cabi_recorder.py >> ../log/cabi_recorder.log
