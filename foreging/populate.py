from .file import File
from .ffw import FFW
from .linguist import Linguist
from .loc_fdd import LocFDD
from .mediainfo import MediaInfo
from .nara import NARA_FFPP
from .pronom import PRONOM
from .tcdb import TCDB
from .tika import Tika
from .trid import TrID
from .wikidata import WikiData

from sqlite_utils import Database
import pyarrow as pa
import pyarrow.parquet as pq
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Push in the data:
def populate_database(session, gen, mts, genres):
    log.info("Getting transformed format records for registry ID %s..." % gen.registry_id)
    for f in gen.get_formats(mts, genres):
        session.add(f)

if __name__ == "__main__":
    # Registries
    registries = {}
    for r in [File(), FFW(), Linguist(), LocFDD(), MediaInfo(), NARA_FFPP(), PRONOM(), TCDB(), Tika(), TrID(), WikiData()]:
        registries[r.registry.id] = r

    # Args
    parser = argparse.ArgumentParser()
    parser.add_argument('--only', required=False, choices=registries.keys())
    parser.add_argument('--jsonl', action=argparse.BooleanOptionalAction)
    parser.add_argument('output_path')
    args = parser.parse_args()

    # Get the output file:
    output_path= Path(args.output_path)
    if not output_path.exists():
        output_path.mkdir()
    elif output_path.is_file():
        raise Exception("Output path should not be a file!")

    # Gather the data:
    formats = []
    for reg_id in registries:
        reg = registries[reg_id]
        if args.only == None or args.only == reg_id:
            log.info(f"Parsing data from Registry ID = {reg.registry_id}")
            for f in reg.get_formats():
                formats.append(f)

    # Define outputs:
    outputs = { 
        "formats": formats,
        "registries": [registries[id].registry for id in registries]
    }

    # Generate raw JSONL output
    if args.jsonl:
        log.info("Generating JSONL export...")
        for name, records in outputs.items():
            with open( output_path / f"{name}.jsonl", "w") as f:
                for r in records:
                    f.write(r.model_dump_json())
                    f.write("\n")

    # And generate Parquet version:
    log.info("Generating Parquet export...")
    for name, records in outputs.items():
        plain_records = [item.model_dump() for item in records]
        table = pa.Table.from_pylist(plain_records)
        pq.write_table(table,  output_path / f"{name}.parquet")

    # Generate SQLite DB
    log.info("Generating SQLite export...")
    sql_path = output_path / "registries.db"
    db = Database(sql_path, recreate=True)
    for r in formats:
        db["formats"].insert(r.model_dump(), pk="id")
    for r in outputs["registries"]:
        db["registries"].insert(r.model_dump(), pk="id")
    db["formats"].enable_fts(['name', 'version', 'summary', 'genres', 'extensions', 'media_types', 'writers', 'readers'])
    # sqlite-utils add-foreign-key data/registries.db formats registry_id registries id
    db["formats"].add_foreign_key('registry_id', 'registries', 'id')


