import json
import yaml
from lxml import etree
from io import BytesIO
import logging
from .models import Format, Software, Registry, Genre, MediaType, RegistryDataLogEntry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#
class File():
    source_file = "digipres.github.io/_sources/registries/file/polyfile-magic.jsonl"
    source_url = "https://github.com/trailofbits/polyfile/tree/master/polyfile/magic_defs"
    index_url = "https://github.com/digipres/digipres.github.io/blob/master/_sources/registries/file/polyfile-magic.jsonl"
    # Set up the Registry object for this class:
    registry_id = "file"
    registry = Registry(
        id=registry_id, 
        name="file libmagic (via polyfile 0.55)", 
        url="https://www.darwinsys.com/file/",
        id_prefix=None,
        index_data_url=index_url
        )

    def get_formats(self, mts, gnrs):
        fmts = []
        idx = 0
        with open(self.source_file, "r") as f:
            for line in f.readlines():
                idx += 1
                entry = json.loads(line)
                if 'extensions' in entry or 'types' in entry:
                    # Do the ugly book-keeping to make the SQL work:
                    extensions = list()
                    for extension in set(entry.get('extensions', [])):
                        extensions.append(extension)
                    media_types = []
                    for mt in set(entry.get('types', [])):
                        mts[mt] = mts.get(mt, MediaType(id=mt))
                        media_types.append(mts[mt])
                    # Set up as a format entity: 
                    f = Format(
                        registry=self.registry,
                        id=f"{self.registry_id}:{idx}",
                        name=entry["name"],
                        version=None,
                        summary=None,
                        genres=[],
                        extensions=extensions,
                        media_types=media_types,
                        has_magic=True,
                        primary_media_type=None,
                        parent_media_type=None,
                        registry_url=None,
                        registry_source_data_url=self.source_url,
                        registry_index_data_url=f"{self.index_url}#L{idx}",
                        created=None,
                        last_modified=None
                    )
                    # And record the entry:
                    fmts.append(f)

        # Now yield them, so all the log entries get stored too:
        for f in fmts:
            yield f