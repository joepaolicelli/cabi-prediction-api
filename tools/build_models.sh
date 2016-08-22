#!/bin/bash
cd $(dirname "$0")
cd ..

python build_models.py >> log/build_models.log
