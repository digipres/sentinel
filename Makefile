
all: data/registries.db

data/registries.db: foreging/*.py
	rm -fr data
	mkdir -p data
	python -m foreging.populate data

