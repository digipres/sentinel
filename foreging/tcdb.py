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
                logger.debug(f"Processing row: {row}")
                type_code = row['Type'].strip()
                creator_code = row['Creator'].strip()
                extension = row['Extension'].strip()
                category = row['Category'].strip()
                name = row['File Name'].strip()
                comments = row['Comments'].strip()
                # Store additional fields:
                additionals = {
                    'mac-type-code': [type_code],
                    'mac-creator-code': [creator_code],
                    'comments': [comments]
                }
                # Set up as a format entity: 
                f = Format(
                    registry_id=self.registry_id,
                    id=f"tcdb:{type_code}:{creator_code}",
                    name=name,
                    version=None,
                    summary=None,
                    genres=[category] if category else [],
                    extensions=[extension] if extension else [],
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
                logger.debug(f"Generated format: {f}")
                yield f


if __name__ == "__main__":
    gen = TCDB()
    for f in gen.get_formats():
        print(f.model_dump_json())