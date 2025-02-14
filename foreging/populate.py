from .pronom import PRONOM
from .tcdb import TCDB
from .wikidata import WikiData
from sqlmodel import Session, SQLModel, create_engine


def populate_database(session, gen, exts, mts, genres):
        i = 0
        for f in gen.get_formats(exts, mts, genres):
            session.add(f)
            i += 1
            if i % 200 == 0:
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
        populate_database(session, PRONOM(), exts, mts, genres)
        populate_database(session, WikiData(), exts, mts, genres)
        populate_database(session, TCDB(), exts, mts, genres)


