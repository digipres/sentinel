#!/bin/bash
set -e

# This all happens in here:
cd digipres.github.io

# Grab a version ID:
VERSION=$(git describe --always --tag)

echo "Deploying into master branch:"
# Just in case something changed while we generated the data:
git checkout master
git pull origin master
# Add the new stuff:
git add --all .
git commit -am "New site version ${VERSION} deployed." --allow-empty 

# Set up the credentials for digipres.github.io deploy key, if set:
if [[ -z "${DIGIPRES_REPO_DEPLOY_PRIVATE_KEY}" ]]; then
  echo No DIGIPRES_REPO_DEPLOY_PRIVATE_KEY set: using standard remote.
  git remote get-url origin
else
  echo DIGIPRES_REPO_DEPLOY_PRIVATE_KEY set: git config --local core.sshCommand \"ssh -i keyfile ...\"
  echo "${DIGIPRES_REPO_DEPLOY_PRIVATE_KEY}" > ~/ssh_id_ed25519
  chmod 600 ~/ssh_id_ed25519
  head -2 ~/ssh_id_ed25519
  git config --local core.sshCommand "ssh -i ~/ssh_id_ed25519 -o 'IdentitiesOnly yes' -o 'StrictHostKeyChecking no'"
  # Add an SSH remote:
  git remote add origin_ssh git@github.com:digipres/digipres.github.io.git
  # Avoid Git forcing ssh remoted over to https:
  git config --local --unset-all url."https://github.com/".insteadof
fi

# And PUSH IT
echo "Pushing to origin_ssh master..."
git push origin_ssh master
echo "DONE."
