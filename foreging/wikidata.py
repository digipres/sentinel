from collections import defaultdict
import os
import json
import logging
from .models import Format, Software
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#
#
# WikiData dumps parser
#
class WikiData():
    registry_id = "wikidata"
    source_file_dir = "digipres.github.io/_sources/registries/wikidata"
    fmt_source_file = f"{source_file_dir}/wikidata.json"
    sw_r_source_file = f"{source_file_dir}/wikidata-reads.json"
    sw_w_source_file = f"{source_file_dir}/wikidata-writes.json"
    warnings = []

    def get_formats(self):
        logger.info("Getting transformed format records for registry ID %s..." % self.registry_id)

        with open (self.fmt_source_file, 'r') as f:
            wd = json.load(f)

        fmts = {}

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
                finfo['readers'] = []
                finfo['writers'] = []
            # Aggregate value for each ID
            for key in fmt:
                if key == 'extension' and fmt[key]:
                    finfo['extensions'].add(fmt[key])
                if key == 'mimetype' and fmt[key]:
                    finfo['mimetypes'].add(fmt[key])
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
                if qid not in fmts:
                    logger.warning(f"Software entry for unknown format {qid}: {sw['formatLabel']}")
                    self.warnings.append(f"Software entry for unknown format {qid}: {sw['formatLabel']}")
                    continue
                sw_qid = sw['id']
                if sw_qid not in sws:
                    sws[sw_qid] = sw
                    sws[sw_qid]['reads'] = []
                    sws[sw_qid]['writes'] = []
                sws[sw_qid][mode].append(qid)

        # Now add the software to the formats:
        for sw in sws.values():
                s = self.make_software(sw)
                for qid in sw['reads']:
                    fmts[qid]['readers'].append(s)
                for qid in sw['writes']:
                    fmts[qid]['writers'].append(s)


        # And return the format:
        for qid in fmts:
            info = fmts[qid]
            yield self.make_format(qid,info)
        
    
    def make_format(self, current_qid, finfo):
        
        # Set up as a format entity: 
        f = Format(
            registry_id=self.registry_id,
            id=f"wikidata:{current_qid}",
            name=finfo['name'],
            version=None,
            summary=None,
            genres= [],
            extensions=list(finfo['extensions']),
            iana_media_types=list(finfo['mimetypes']),
            has_magic=finfo['hasMagic'],
            primary_media_type=None,
            parent_media_type=None,
            registry_url=finfo['source'],
            registry_source_data_url=f"{finfo['source']}.jsonld",
            registry_index_data_url=f"https://github.com/digipres/digipres.github.io/blob/master/{self.fmt_source_file}",
            additional_fields={},
            created=None,
            last_modified=None,
            readers=finfo['readers'],
            writers=finfo['writers']
        )
        logger.debug(f"Generated format: {f}")
        return f

        
    def make_software(self, info):
        s = Software(
            registry_id=self.registry_id,
            id=f"wikidata:{info['id']}",
            name=info['name'],
            version=None,
            summary=None,
            registry_url=info['source'],
            license=info['licenseLabel'],
            reads=info['reads'],
            writes=info['writes']
        )
        logger.debug(f"Generated software: {s}")
        return s


if __name__ == "__main__":
    gen = WikiData()
    for f in gen.get_formats():
        print(f.model_dump_json())
