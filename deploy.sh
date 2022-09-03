#!/bin/bash
set -e

source venv/bin/activate

# This all happens in here:
cd digipres.github.io

# Grab a version ID:
VERSION=$(git describe --always --tag)

echo "\nDeploying into master branch:"
# Just in case something changed while we generated the data:
git checkout master
git pull origin master
# Add the new stuff:
git add --all .
git commit -am "New site version ${VERSION} deployed." --allow-empty 

# Set up the credentials for digipres.github.io
# if GITHUB_TOKEN
if [[ -z "${GITHUB_TOKEN}" ]]; then
  echo No GITHUB_TOKEN set: using standard remote.
  git remote get-url origin
else
  echo GITHUB_TOKEN set: using https://${GITHUB_ACTOR}:\${DIGIPRES_REPO_TOKEN}@github.com/digipres/digipres.github.io.git remote.
  git remote set-url --push origin https://${GITHUB_ACTOR}:${DIGIPRES_REPO_TOKEN}@github.com/digipres/digipres.github.io.git
fi

# And PUSH IT
echo "\nPushing to master..."
git push origin master
echo "\n DONE."
