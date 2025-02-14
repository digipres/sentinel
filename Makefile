
all: registries.db

registries.db: foreging/*.py
	rm -f $@ $@.tmp
	mkdir -p data
	python -m foreging.populate $@.tmp
	sqlite-utils enable-fts $@.tmp format name version summary
	sqlite-utils enable-fts $@.tmp media_type id
	sqlite-utils enable-fts $@.tmp extension id
	sqlite-utils enable-fts $@.tmp genre name
	sqlite-utils enable-fts $@.tmp software name version summary
	sqlite-utils enable-fts $@.tmp registry_data_log level message
	mv $@.tmp $@

