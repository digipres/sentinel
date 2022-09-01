#!/bin/sh

# Based on https://docs.github.com/en/actions/security-guides/encrypted-secrets#storing-large-secrets

# Decrypt the file
# --batch to prevent interactive command
# --yes to assume "yes" for questions
gpg --quiet --batch --yes --decrypt --passphrase="$FFW_PASSWORDFILE_SECRET" \
--output passwordfile passwordfile.gpg
