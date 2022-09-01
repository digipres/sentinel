#!/bin/sh
set -e

source venv/bin/activate

# Make sure the branch is up to date
cd digipres.github.io
git checkout master
git pull origin master
cd ..
# Update tool info etc.
#python projections/download-coptr-tools.py
#python projections/tools-to-grid.py
python projections/mw-contribs.py
# Update format registry sources and output
cd digipres.github.io/_sources/registries
./refresh-sources.sh
cd -
python aggregates.py

