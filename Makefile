
all: registries.db

registries.db: foreging/*.py
	rm -fr data
	mkdir -p data
	python -m foreging.populate --json data

