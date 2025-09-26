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
    parser.add_argument('output_file')
    args = parser.parse_args()

    # Get the output file:
    output_file = Path(args.output_file)

    # Gather the data:
    formats = []
    for reg_id in registries:
        reg = registries[reg_id]
        if args.only == None or args.only == reg_id:
            log.info(f"Parsing data from Registry ID = {reg.registry_id}")
            for f in reg.get_formats():
                formats.append(f)

    # Generate raw JSONL output
    if args.jsonl:
        log.info("Generating JSONL export...")
        with open( output_file.with_suffix(".jsonl"), "w") as f:
            for ir in formats:
                f.write(ir.model_dump_json())
                f.write("\n")

    # Generate SQLite DB
    log.info("Generating SQLite export...")
    sql_path = output_file
    db = Database(sql_path, recreate=True)
    for ir in formats:
        db["formats"].insert(ir.model_dump())
    db["formats"].enable_fts(['name', 'version', 'summary', 'genres', 'extensions', 'media_types', 'writers', 'readers'])

    log.info("Generating Parquet export...")
    plain_records = [item.model_dump() for item in formats]
    table = pa.Table.from_pylist(plain_records)
    pq.write_table(table,  output_file.with_suffix(".parquet"))

