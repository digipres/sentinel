from .loc_fdd import LocFDD
from .nara import NARA
from .pronom import PRONOM
from .tcdb import TCDB
from .wikidata import WikiData

from sqlmodel import Session, SQLModel, create_engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Size of the chunks of data to commit (makes things faster but more memory load)
COMMIT_SIZE = 200

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
    # And get the last few in:
    session.commit()

if __name__ == "__main__":

    # Cache the cross-referenced entities:
    exts = {}
    mts = {}
    genres = {}

    # Set up the session
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    engine = create_engine(sqlite_url, echo=False)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # FFW
        
        # GithubLinguist
        
        # LC FDD
        populate_database(session, LocFDD(), exts, mts, genres)
        # NARA
        ##populate_database(session, NARA(), exts, mts, genres)
        # PRONOM
        populate_database(session, PRONOM(), exts, mts, genres)
        # TCDB
        populate_database(session, TCDB(), exts, mts, genres)
        # Tika
        
        # TRiD

        # WikiData
        populate_database(session, WikiData(), exts, mts, genres)




