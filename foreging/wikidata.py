from collections import defaultdict
import os
import json
import logging
from .models_sql import Format, Software, Registry, Extension, Genre, MediaType, RegistryDataLogEntry
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#
# WikiData dumps parser
#
class WikiData():
    registry_id = "wikidata"
    registry = Registry(id=registry_id, name="WikiData")

    source_file_dir = "digipres.github.io/_sources/registries/wikidata"
    fmt_source_file = f"{source_file_dir}/wikidata.json"
    sw_r_source_file = f"{source_file_dir}/wikidata-reads.json"
    sw_w_source_file = f"{source_file_dir}/wikidata-writes.json"

    def get_formats(self):
        logger.info("Getting transformed format records for registry ID %s..." % self.registry_id)

        with open (self.fmt_source_file, 'r') as f:
            wd = json.load(f)

        fmts = {}
        exts = {}
        mts = {}
        warnings = set()

        current_qid = None

        for fmt in wd:
            qid = f"wikidata:{fmt['id']}"
            # items are ordered by ID, so we can aggregate as we go
            if qid != current_qid:
                # Store the previous record:
                if current_qid:
                    fmts[current_qid] = finfo
                current_qid = qid
                # Start a new record:
                finfo = {}
                finfo['name'] = fmt['name']
                finfo['source'] = fmt['source']
                finfo['extensions'] = set()
                finfo['mimetypes'] = set()
                finfo['hasMagic'] = False
                finfo['readers'] = set()
                finfo['writers'] = set()
            # Aggregate value for each ID
            for key in fmt:
                if key == 'extension' and fmt[key]:
                    # Making sure we reuse the same object for an extension to keep the model consistent:
                    ext = fmt[key]
                    exts[ext] = exts.get(ext, Extension(id=ext))
                    finfo['extensions'].add(exts[ext])
                if key == 'mimetype' and fmt[key]:
                    mt = fmt[key]
                    mts[mt] = mts.get(mt, MediaType(id=mt))
                    finfo['mimetypes'].add(mts[mt])
                if key == 'sig' and fmt[key]:
                    finfo['hasMagic'] = True

        # Add the final one:
        if current_qid:
            fmts[current_qid] = finfo

        # Now get the software:

        # Load the 'what reads this' and 'what writes this' data:
        with open (self.sw_r_source_file, 'r') as f:
            sw_r = json.load(f)
        with open (self.sw_w_source_file, 'r') as f:
            sw_w = json.load(f)
        
        # Process the software data:
        sws = {}
        for mode, sw_i in [('reads', sw_r), ('writes', sw_w)]:
            for sw in sw_i:
                qid = sw['format'].replace("http://www.wikidata.org/entity/","wikidata:")
                sw_qid = sw['id']
                # Check it's in the set:
                if qid not in fmts:
                    warning = f"Software entry '{sw_qid}: {sw['formatLabel']}' references missing format '{qid}'"
                    logger.warning( warning )
                    warnings.add( RegistryDataLogEntry(level="warning", message=warning, url=sw['source'] ) )
                    continue
                if sw_qid not in sws:
                    sws[sw_qid] = sw
                    sws[sw_qid]['reads'] = []
                    sws[sw_qid]['writes'] = []
                sws[sw_qid][mode].append(qid)

        # Now add the software to the formats:
        for sw in sws.values():
                s = self.make_software(sw)
                for qid in sw['reads']:
                    fmts[qid]['readers'].add(s)
                for qid in sw['writes']:
                    fmts[qid]['writers'].add(s)

        # Store the warnings:
        self.registry.data_log = list(warnings)

        # And return the format:
        for qid in fmts:
            info = fmts[qid]
            yield self.make_format(qid,info)
        
    
    def make_format(self, current_qid, finfo):
        
        # Set up as a format entity: 
        f = Format(
            id=f"{current_qid}",
            registry=self.registry,
            name=finfo['name'],
            version=None,
            summary=None,
            genres= [],
            extensions=list(finfo['extensions']),
            media_types=list(finfo['mimetypes']),
            has_magic=finfo['hasMagic'],
            #primary_media_type=None,
            #parent_media_type=None,
            #registry_url=finfo['source'],
            #registry_source_data_url=f"{finfo['source']}.jsonld",
            #registry_index_data_url=f"https://github.com/digipres/digipres.github.io/blob/master/{self.fmt_source_file}",
            #additional_fields={},
            #created=None,
            #last_modified=None,
            readers=list(finfo['readers']),
            writers=list(finfo['writers'])
        )
        logger.debug(f"Generated format: {f}")
        return f

        
    def make_software(self, info):
        s = Software(
            #registry_id=self.registry_id,
            id=f"wikidata:{info['id']}",
            name=info['name'],
            #version=None,
            #summary=None,
            #registry_url=info['source'],
            #license=info['licenseLabel'],
        )
        logger.debug(f"Generated software: {s}")
        return s


if __name__ == "__main__":
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    engine = create_engine(sqlite_url, echo=False)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:

        gen = WikiData()
        i = 0
        for f in gen.get_formats():
            session.add(f)
            i += 1
            if i % 100 == 0:
                session.commit()
