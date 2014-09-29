#!/bin/bash
set -e

SRC=$(pwd)/site
TEMP=$(mktemp -d -t jgd-XXX)
trap "rm -rf ${TEMP}" EXIT

VERSION=$(git describe --always --tag)

echo -e "\nBuilding Jekyll site:"

jekyll build --source $SRC --destination $TEMP

echo -e "\nPreparing gh-pages branch:"
if [ -z "$(git branch -a | grep origin/gh-pages)" ]; then
  git checkout --orphan gh-pages
else
  git checkout gh-pages
fi

echo -e "\nDeploying into gh-pages branch:"
git rm -rf --ignore-unmatch _site/*
mkdir _site
cp -R ${TEMP}/* _site
git add _site
#git config user.email "${USER_EMAIL}"
#git config user.name "${USER_NAME}"
git commit -m "new site version ${VERSION} deployed" --allow-empty _site
git push https://github.com/digipres/coptr.git gh-pages

# Return to master branch
git checkout master
