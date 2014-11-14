# Make sure the branch is up to date
cd digipres.github.io
git checkout master
git pull origin master
cd ..
# Update tool info etc.
python projections/download-coptr-tools.py
python projections/tools-to-grid.py
python projections/mw-contribs.py
# Update format registry sources and output
cd registries
./refresh-sources.sh
cd ..
python registries/aggregates.py

