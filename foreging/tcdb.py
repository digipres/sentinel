import os
import csv
import logging
from .models import Format

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#
#
# TCDB CSV dump parser
#
class TCDB():
    registry_id = "tcdb"
    source_file = 'digipres.github.io/_sources/registries/tcdb/TCDB_2003.8_data-cleaned.csv'
    warnings = []

    def get_formats(self):
        logger.info("Getting transformed format records for registry ID %s..." % self.registry_id)

        # Open, coping with Unicode BOM
        with open(self.source_file, "r", encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                additionals = {
                    'mac-type': [row['Type']],
                    'mac-creator': [row['Creator']]
                }
                # Set up as a format entity: 
                f = Format(
                    registry_id=self.registry_id,
                    id=f"tcdb:{row['Type']}:{row['Creator']}",
                    name=row['File Name'],
                    version=None,
                    summary=f"Type: {row['Type']}, Creator: {row['Creator']}, Comments: {row['Comments']}",
                    genres=[row['Category']],
                    extensions=[row['Extension']],
                    iana_media_types=[],
                    has_magic=False,
                    primary_media_type=None,
                    parent_media_type=None,
                    registry_url=f"https://github.com/thorsted/Born-Digital-Scripts/tree/main/TC%20Identification",
                    registry_source_data_url=f"https://github.com/thorsted/Born-Digital-Scripts/blob/main/TC%20Identification/TCDB_2003.8_data-cleaned.csv",
                    registry_index_data_url=f"https://github.com/digipres/digipres.github.io/blob/master/_sources/registries/tcdb/TCDB_2003.8_data-cleaned.csv",
                    additional_fields=additionals,
                    created=None,
                    last_modified=None,
                )
                yield f


if __name__ == "__main__":
    gen = TCDB()
    for f in gen.get_formats():
        print(f.model_dump_json())