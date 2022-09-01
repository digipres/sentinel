#!/bin/sh

# Decrypt the file
# --batch to prevent interactive command
# --yes to assume "yes" for questions
gpg --quiet --batch --yes --decrypt --passphrase="$FFS_PASSWORDFILE_SECRET" \
--output passwordfile passwordfile.gpg
