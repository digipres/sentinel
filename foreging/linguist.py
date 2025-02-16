import json
import yaml
import logging
from .models import Format, Software, Registry, Extension, Genre, MediaType, RegistryDataLogEntry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#
class Linguist():
    source_file = "digipres.github.io/_sources/registries/githublinguist/languages.yml"
    # Set up the Registry object for this class:
    registry_id = "linguist"
    registry = Registry(
        id=registry_id, 
        name="GitHub Linguist", 
        url="http://fileformats.archiveteam.org/",
        id_prefix='http://fileformats.archiveteam.org/wiki/',
        index_data_url=f"https://github.com/digipres/digipres.github.io/blob/master/{source_file}"
        )

    def get_formats(self, exts, mts, gnrs):
        stream = open(self.source_file, 'r')
        ghl = yaml.safe_load(stream)
        stream.close()

        for fmt_name in ghl:
            fmt = ghl[fmt_name]
            f_info = {}
            f_info['name'] = fmt_name
            f_info['extensions'] = set()
            f_info['mimetypes'] = set()
            f_info['hasMagic'] = False
            ff_id = f"{self.registry_id}:{fmt['language_id']}"
            for key in fmt:
                if key == 'extensions':
                    for ext in fmt[key]:
                        if ext:
                            ext=ext.strip('.') # Drop the prefix dot
                            exts[ext] = exts.get(ext, Extension(id=ext))
                            f_info['extensions'].add(exts[ext])
                elif key == 'codemirror_mime_type':
                    mt = fmt[key]
                    mts[mt] = mts.get(mt, MediaType(id=mt))
                    f_info['mimetypes'].add(mts[mt])
                else:
                    f_info[key] = fmt[key]
            
            # Set up as a format entity: 
            f = Format(
                registry=self.registry,
                id=ff_id,
                name=f_info['name'],
                version=None,
                summary=None,
                genres=[],
                extensions=list(f_info['extensions']),
                media_types=list(f_info['mimetypes']),
                has_magic=f_info['hasMagic'],
                primary_media_type=None,
                parent_media_type=None,
                registry_url=None,
                registry_source_data_url=None,
                registry_index_data_url=None,
                created=None,
                last_modified=None
            )
            yield f