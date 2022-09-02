#!/bin/sh

# Set git pull style:
git config --global pull.rebase false

# Also set up Git commit info:
git config --global user.email "${GITHUB_ACTOR}"
git config --global user.name "${GITHUB_ACTOR}@users.noreply.github.com"

