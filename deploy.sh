#!/bin/bash
set -e

SRC=$(pwd)/site
TEMP=$(mktemp -d -t jgd-XXX)
trap "rm -rf ${TEMP}" EXIT

VERSION=$(git describe --always --tag)

echo "\n We have got..."
ls -l site

echo -e "\nBuilding Jekyll site:"

jekyll build --source $SRC --destination $TEMP

echo -e "\nPreparing gh-pages branch:"
git remote -v
git remote add publish https://github.com/digipres/coptr.git
git fetch publish gh-pages
git checkout gh-pages

echo -e "\nDeploying into gh-pages branch:"
rm -rf *
cp -R ${TEMP}/* .
git add --all .
git commit -am "New site version ${VERSION} deployed." --allow-empty 

git config credential.helper "store --file=./git-credentials"
echo "https://$GH_TOKEN:@github.com" > ./git-credentials

echo -e "\nPushing to gh-pages..."
git push publish gh-pages
