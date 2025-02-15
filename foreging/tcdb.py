import os
import csv
import logging
from .models import Format, Software, Registry, Extension, Genre, MediaType, RegistryDataLogEntry

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
    registry = Registry(
        id=registry_id,
        name="Macintosh Type/Creator Codes Database",
        url=registry_url,
        id_prefix=None,
        index_data_url=source_file
        )

    def get_formats(self, exts, mts, genres):
        # First, gather rows by type_code...
        rows_by_type_code = {}
        # Open, coping with Unicode BOM
        line = 1
        with open(self.source_file, "r", encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                logger.debug(f"Processing row: {row}")
                type_code = row['Type'].strip()
                rows_by_type_code[type_code] = rows_by_type_code.get(type_code, [])
                rows_by_type_code[type_code].append(row)
                line += 1
                row['_line_number'] = line

        # Now, process each type_code:
        sws = {}
        for type_code, rows in rows_by_type_code.items():
            readers = []
            extensions = set()
            categories = set()
            names = []
            for row in rows:
                logger.debug(f"Processing row: {row}")
                creator_code = row['Creator'].strip()
                #
                ext = row['Extension'].strip().lower()
                if ext:
                    exts[ext] = exts.get(ext,Extension(id=ext))
                    extensions.add(exts[ext])
                #
                cat = row['Category'].strip()
                if cat:
                    genres[cat] = genres.get(cat, Genre(name=cat))
                    categories.add(genres[cat])
                #
                names.append(row['File Name'].strip())
                # Record the Software ID, adding a line number to make sure everything has distinct IDs.
                sw_id = f"tcdb:{type_code}:{creator_code}@L{row['_line_number']}"
                sws[sw_id] = sws.get(sw_id,
                    Software(
                        registry=self.registry,
                        id=sw_id,
                        name=row['File Name'].strip(),
                        version=None,
                        summary=row['Comments'].strip()
                    )
                )
                readers.append(sws[sw_id])
            # Set up as a format entity for this type_code: 
            f = Format(
                registry=self.registry,
                id=f"tcdb:{type_code}",
                name= ", ".join(names)[:256], # FIXME Limit size as this includes too much software information and is very slow to work with!
                version=None,
                summary=None,
                genres=list(categories),
                extensions=list(extensions),
                media_types=[],
                has_magic=False,
                primary_media_type=None,
                parent_media_type=None,
                registry_url=None,
                registry_source_data_url=None,
                registry_index_data_url=None,
                created=None,
                last_modified=None,
                readers=readers
            )
            logger.debug(f"Generated format: {f}")
            yield f
