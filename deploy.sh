#!/bin/bash
set -e

# This all happens in here:
cd digipres.github.io

# Grab a version ID:
VERSION=$(git describe --always --tag)

echo -e "\nDeploying into master branch:"
# Just in case something changed while we generated the data:
git checkout master
git pull origin master
# Add the new stuff:
git add --all .
git commit -am "New site version ${VERSION} deployed." --allow-empty 

# Set up the credentials for digipres.github.io
git config credential.helper "store --file=../git-credentials"
echo "https://$GH_TOKEN:@github.com" > ../git-credentials

# And PUSH IT
echo -e "\nPushing to master..."
git push origin master
echo -e "\n DONE."
