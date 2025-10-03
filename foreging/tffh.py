import csv
import logging
from .models import Format, Registry, RegistryClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#
class TFFH(RegistryClient):
    source_file = "digipres.github.io/_sources/registries/tffh/tffh.csv"
    index_url = "https://github.com/digipres/digipres.github.io/blob/master/_sources/registries/tffh/tffh.csv"
    # Set up the Registry object for this class:
    registry_id = "tffh"
    registry = Registry(
        id=registry_id, 
        name="The File Formats Handbook (1995)", 
        url="https://github.com/digipres/digipres.github.io/blob/master/_sources/registries/tffh/README.md",
        id_prefix=None,
        index_data_url=index_url
        )

    def get_formats(self):
        fmts = []
        idx = 1
        with open(self.source_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                idx += 1
                primary_exts = row['Primary File'].strip()
                if primary_exts:
                    # Assemble all entries, skipping empties:
                    extensions = (primary_exts + " " +  row["Secondary Files"].strip()).split(" ")
                    extensions = [e for e in extensions if e]
                    # Set up as a format entity: 
                    f = Format(
                        registry_id=self.registry_id,
                        id=f"{self.registry_id}:{idx}",
                        name=row["Name"].strip(),
                        version=None,
                        summary=None,
                        genres=[row["Genre"].strip()],
                        extensions=extensions,
                        media_types=[],
                        has_magic=True,
                        primary_media_type=None,
                        parent_media_type=None,
                        registry_url=None,
                        registry_source_data_url=None,
                        registry_index_data_url=f"{self.index_url}#L{idx}",
                        created=None,
                        last_modified=None
                    )
                    # And record the entry:
                    fmts.append(f)

        # Now yield them, so all the log entries get stored too:
        for f in fmts:
            yield f