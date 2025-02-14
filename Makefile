
DATAFILES := data/pronom.jsonl data/loc.jsonl data/nara.jsonl data/tcdb.jsonl data/wikidata.jsonl

all: data data/registries.db

data:
	mkdir -p data

data/pronom.jsonl: foreging/pronom.py digipres.github.io/_sources/registries
	python -m foreging.pronom > $@

data/loc_fdd.jsonl: foreging/loc_fdd.py digipres.github.io/_sources/registries
	python -m foreging.loc_fdd > $@

data/nara.jsonl: foreging/nara.py digipres.github.io/_sources/registries
	python -m foreging.nara > $@

data/tcdb.jsonl: foreging/tcdb.py digipres.github.io/_sources/registries
	python -m foreging.tcdb > $@

data/wikidata.jsonl: foreging/wikidata.py digipres.github.io/_sources/registries
	python -m foreging.wikidata > $@

data/registries.db: $(DATAFILES)
	rm -f $@
	sqlite-utils insert $@ formats --nl data/pronom.jsonl
	sqlite-utils insert $@ formats --nl data/loc_fdd.jsonl
	sqlite-utils insert $@ formats --nl data/nara.jsonl
	sqlite-utils insert $@ formats --nl data/tcdb.jsonl
	sqlite-utils insert $@ formats --nl data/wikidata.jsonl
	sqlite-utils enable-fts $@ formats name summary extensions iana_media_types genres readers writers additional_fields