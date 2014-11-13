#!/bin/bash
set -e

cd digipres.github.io
git remote add origin-https https://github.com/digipres/sentinel.git

VERSION=$(git describe --always --tag)

echo -e "\nDeploying into master branch:"
git pull origin-https master
git add --all .
git commit -am "New site version ${VERSION} deployed." --allow-empty 

git config credential.helper "store --file=../git-credentials"
echo "https://$GH_TOKEN:@github.com" > ../git-credentials

echo -e "\nPushing to master..."
git push origin-https master
