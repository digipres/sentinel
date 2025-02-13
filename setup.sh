#!/bin/bash
# - openssl aes-256-cbc -K $encrypted_6e6cf0e3465b_key -iv $encrypted_6e6cf0e3465b_iv -in passwordfile.enc -out passwordfile -d 
# - sudo apt-get install -y unrar

set -e

python3 -m pip install -U pip setuptools wheel virtualenv


virtualenv -p python3 venv
source venv/bin/activate


cd pywikibot
pip install .
cd ..

pip install requests
pip install pyyaml
pip install beautifulsoup4
pip install lxml

# Running...
echo "And login..."

python pywikibot/pwb.py login -family:ff


