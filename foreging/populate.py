from .ffw import FFW
from .linguist import Linguist
from .loc_fdd import LocFDD
from .nara import NARA_FFPP
from .pronom import PRONOM
from .tcdb import TCDB
from .tika import Tika
from .wikidata import WikiData

from sqlmodel import Session, SQLModel, create_engine
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Size of the chunks of data to commit (makes things faster but more memory load)
COMMIT_SIZE = 2000

# Push in the data:
def populate_database(session, gen, exts, mts, genres):
    logger.info("Getting transformed format records for registry ID %s..." % gen.registry_id)
    # Counter to stage commits in chunks
    i = 0
    for f in gen.get_formats(exts, mts, genres):
        session.add(f)
        i += 1
        if i % COMMIT_SIZE == 0:
            session.commit()
            i = 0
    # And get the last few in:
    if i > 0:
        session.commit()

if __name__ == "__main__":
    # Registries
    registries = {}
    for r in [FFW(), Linguist(), LocFDD(), NARA_FFPP(), PRONOM(), TCDB(), Tika(), WikiData()]:
        registries[r.registry.id] = r
    # TO-ADD: TRiD

    # Args
    parser = argparse.ArgumentParser()
    parser.add_argument('--only', required=False, choices=registries.keys())
    parser.add_argument('output_file')
    args = parser.parse_args()


    # Cache the cross-referenced entities:
    exts = {}
    mts = {}
    genres = {}

    # Set up the session
    sqlite_file_name = args.output_file
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    engine = create_engine(sqlite_url, echo=False)

    SQLModel.metadata.create_all(engine)

    with Session(engine).no_autoflush as session:
        for reg_id in registries:
            reg = registries[reg_id]
            if args.only == None or args.only == reg_id:
                populate_database(session, reg, exts, mts, genres)




