#!/bin/bash
set -e

cd digipres.github.io

VERSION=$(git describe --always --tag)

echo -e "\nDeploying into gh-pages branch:"
git pull origin master
git add --all .
git commit -am "New site version ${VERSION} deployed." --allow-empty 

git config credential.helper "store --file=../git-credentials"
echo "https://$GH_TOKEN:@github.com" > ../git-credentials

echo -e "\nPushing to gh-pages..."
git push origin gh-pages
