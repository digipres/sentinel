#!/bin/bash
set -e

SRC=$(pwd)/site
TEMP=$(mktemp -d -t jgd-XXX)
trap "rm -rf ${TEMP}" EXIT

VERSION=$(git describe --always --tag)

echo -e "\nBuilding Jekyll site:"

jekyll build --source $SRC --destination $TEMP

echo -e "\nPreparing gh-pages branch:"
git fetch https://github.com/digipres/coptr.git
git checkout origin/gh-pages

echo -e "\nDeploying into gh-pages branch:"
rm -rf *
cp -R ${TEMP}/* .
git add --all .
git commit -am "new site version ${VERSION} deployed" --allow-empty 

git config credential.helper "store --file=./git-credentials"
echo "https://$GH_TOKEN:@github.com" > ./git-credentials

git push https://github.com/digipres/coptr.git gh-pages

# Return to master branch
git checkout master
