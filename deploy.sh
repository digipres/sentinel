#!/bin/bash
set -e

cd digipres.github.io

VERSION=$(git describe --always --tag)

echo -e "\nDeploying into master branch:"
git checkout master
git pull origin master
git add --all .
git commit -am "New site version ${VERSION} deployed." --allow-empty 

git config credential.helper "store --file=../git-credentials"
echo "https://$GH_TOKEN:@github.com" > ../git-credentials

echo -e "\nPushing to master..."
git push origin master
echo -e "\n DONE."
