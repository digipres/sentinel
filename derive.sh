#!/bin/bash
set -e

source venv/bin/activate

make

cp registries.db digipres.github.io/_data/formats/

