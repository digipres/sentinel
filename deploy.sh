#!/bin/bash
set -e

SRC=$(pwd)/site
TEMP=$(mktemp -d -t jgd-XXX)
trap "rm -rf ${TEMP}" EXIT

VERSION=$(git describe --always --tag)

echo -e "\nBuilding Jekyll site:"

jekyll build --source $SRC --destination $TEMP

echo -e "\nPreparing gh-pages branch:"
git remote add pages https://github.com/digipres/coptr.git
git fetch pages gh-pages
git checkout pages/gh-pages

echo -e "\nDeploying into gh-pages branch:"
rm -rf *
cp -R ${TEMP}/* .
git add --all .
git commit -am "New site version ${VERSION} deployed." --allow-empty 

git config credential.helper "store --file=./git-credentials"
echo "https://$GH_TOKEN:@github.com" > ./git-credentials

echo -e "\nPushing to gh-pages..."
git push pages pages/gh-pages
