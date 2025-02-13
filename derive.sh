#!/bin/bash
set -e

source venv/bin/activate

make

cp data/registries.db digipres.github.io/_data/formats/

