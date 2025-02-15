import json
import yaml
import logging
from .models import Format, Software, Registry, Extension, Genre, MediaType, RegistryDataLogEntry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#
class FFW():
    source_file =  "digipres.github.io/_sources/registries/mediawikis/ffw.yml"
    # Set up the Registry object for this class:
    registry_id = "ffw"
    registry = Registry(
        id=registry_id, 
        name="Just Solve The Problem File Formats Wiki", 
        url="http://fileformats.archiveteam.org/",
        id_prefix='http://fileformats.archiveteam.org/wiki/',
        index_data_url=f"https://github.com/digipres/digipres.github.io/blob/master/{source_file}"
        )

    def get_formats(self, exts, mts, gnrs):
        stream = open(self.source_file, 'r')
        ffw = yaml.safe_load(stream)
        stream.close()

        for fmt in ffw['formats']:
            f_info = {}
            f_info['extensions'] = set()
            f_info['mimetypes'] = set()
            f_info['categories'] = set()
            f_info['hasMagic'] = False
            ff_id = 'ffw:' + fmt['name']
            for key in fmt:
                if key == 'extensions':
                    for ext in fmt[key]:
                        if ext:
                            ext=ext.lower()
                            exts[ext] = exts.get(ext, Extension(id=ext))
                            f_info['extensions'].add(exts[ext])
                elif key == 'mimetypes':
                    for mt in fmt[key]:
                        mts[mt] = mts.get(mt, MediaType(id=mt))
                        f_info['mimetypes'].add(mts[mt])
                elif key == 'categories':
                    for cat in fmt[key]:
                        gnrs[cat] = gnrs.get(cat, Genre(name=cat))
                        f_info['categories'].add(gnrs[cat])
                else:
                    f_info[key] = fmt[key]
            
            # Set up as a format entity: 
            f = Format(
                registry=self.registry,
                id=ff_id,
                name=f_info['name'],
                version=None,
                summary=f_info.get('pageStartText', None),
                genres=list(f_info['categories']),
                extensions=list(f_info['extensions']),
                media_types=list(f_info['mimetypes']),
                has_magic=f_info['hasMagic'],
                primary_media_type=None,
                parent_media_type=None,
                registry_url=fmt['source'],
                registry_source_data_url=fmt['source'],
                registry_index_data_url=None,
                created=None,
                last_modified=None
            )
            yield f