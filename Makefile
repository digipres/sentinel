
DATAFILES := data/pronom.jsonl data/loc.jsonl data/nara.jsonl data/tcdb.jsonl

all: data/registries.db

data/pronom.jsonl: foreging digipres.github.io/_sources/registries
	python -m foreging.pronom > $@

data/loc.jsonl: foreging digipres.github.io/_sources/registries
	python -m foreging.loc_fdd > $@

data/nara.jsonl: foreging digipres.github.io/_sources/registries
	python -m foreging.nara > $@

data/tcdb.jsonl: foreging digipres.github.io/_sources/registries
	python -m foreging.tcdb > $@

data/registries.db: $(DATAFILES)
	rm -f $@
	sqlite-utils insert $@ formats --nl data/pronom.jsonl
	sqlite-utils insert $@ formats --nl data/loc.jsonl
	sqlite-utils insert $@ formats --nl data/nara.jsonl
	sqlite-utils insert $@ formats --nl data/tcdb.jsonl
	sqlite-utils enable-fts $@ formats name summary extensions iana_media_types genres