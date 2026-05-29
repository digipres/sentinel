#!/bin/bash
# - openssl aes-256-cbc -K $encrypted_6e6cf0e3465b_key -iv $encrypted_6e6cf0e3465b_iv -in passwordfile.enc -out passwordfile -d 
# - sudo apt-get install -y unrar

set -e

echo Install platform packages...
python3 -m pip install -U pip setuptools wheel virtualenv

echo Set up a virtual environment...
virtualenv -p python3 venv
source venv/bin/activate
echo WARNING setuptools pinned at 81 as the included pywikibot is not compatible with later versions 
pip install setuptools==81.0.0

echo Run install in pywikibot...
cd pywikibot
pip install .
cd ..

echo Run install at the top level...
pip install .

# Running...
echo "And login..."

python pywikibot/pwb.py login -family:ff


