import os
import csv
import logging
from .models import Format, Software

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#
#
# TCDB CSV dump parser
#
class TCDB():
    registry_id = "tcdb"
    registry_url = f"https://github.com/thorsted/Born-Digital-Scripts/tree/main/TC%20Identification"
    source_file = 'digipres.github.io/_sources/registries/tcdb/TCDB_2003.8_data-cleaned.csv'
    warnings = []

    def get_formats(self):
        logger.info("Getting transformed format records for registry ID %s..." % self.registry_id)

        # First, gather rows by type_code...
        rows_by_type_code = {}
        # Open, coping with Unicode BOM
        with open(self.source_file, "r", encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                logger.debug(f"Processing row: {row}")
                type_code = row['Type'].strip()
                if type_code not in rows_by_type_code:
                    rows_by_type_code[type_code] = []
                rows_by_type_code[type_code].append(row)

        # Now, process each type_code:
        for type_code, rows in rows_by_type_code.items():
            readers = []
            extensions = []
            categories = []
            names = []
            for row in rows:
                logger.debug(f"Processing row: {row}")
                creator_code = row['Creator'].strip()
                extensions.append(row['Extension'].strip())
                categories.append(row['Category'].strip())
                names.append(row['File Name'].strip())
                s = Software(
                    registry_id=self.registry_id,
                    id=f"tcdb:{type_code}:{creator_code}",
                    name=row['File Name'].strip(),
                    version=None,
                    summary=row['Comments'].strip(),
                    registry_url=self.registry_url,
                    reads=[f"tcdb:{type_code}"]
                )
                readers.append(s)
            # Set up as a format entity: 
            f = Format(
                registry_id=self.registry_id,
                id=f"tcdb:{type_code}",
                name= ", ".join(names),
                version=None,
                summary=None,
                genres=[x for x in categories if x],
                extensions=[x.lower() for x in extensions if x],
                iana_media_types=[],
                has_magic=False,
                primary_media_type=None,
                parent_media_type=None,
                registry_url=self.registry_url,
                registry_source_data_url=f"https://github.com/thorsted/Born-Digital-Scripts/blob/main/TC%20Identification/TCDB_2003.8_data-cleaned.csv",
                registry_index_data_url=f"https://github.com/digipres/digipres.github.io/blob/master/_sources/registries/tcdb/TCDB_2003.8_data-cleaned.csv",
                created=None,
                last_modified=None,
                readers=readers,
            )
            logger.debug(f"Generated format: {f}")
            yield f


if __name__ == "__main__":
    gen = TCDB()
    for f in gen.get_formats():
        print(f.model_dump_json())