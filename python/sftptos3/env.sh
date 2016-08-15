#!/usr/bin/env bash

set -e

# requires that you have python3 installed.  You can do this with pyenv by running:
# pyenv install 3.4.3
virtualenv --python=${HOME}/.pyenv/versions/3.4.3/bin/python3.4 venv
source venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
#pip3 freeze
#rm -rf venv/