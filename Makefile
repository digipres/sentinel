
all: registries.db

registries.db: foreging/*.py digipres.github.io/_sources/registries/*
	rm -fr data
	mkdir -p data
	python -m foreging.populate --json data
	cp data/registries.db digipres.github.io/_data/formats/registries.db
	cp data/*.parquet digipres.github.io/_data/formats/index/
