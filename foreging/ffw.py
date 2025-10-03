import json
import yaml
import logging
from .models import Format, Registry, RegistryClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#
class FFW(RegistryClient):
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

    def get_formats(self):
        stream = open(self.source_file, 'r')
        ffw = yaml.safe_load(stream)
        stream.close()

        for fmt in ffw['formats']:
            f_info = {}
            f_info['extensions'] = set()
            f_info['mimetypes'] = set()
            f_info['categories'] = set()
            f_info['hasMagic'] = False
            ff_id = self.registry_id + ':' + fmt['name']
            for key in fmt:
                if key == 'extensions':
                    for ext in fmt[key]:
                        if ext:
                            ext=ext.lower().strip()
                            f_info['extensions'].add(ext)
                elif key == 'mimetypes':
                    f_info['mimetypes'] = fmt[key]
                elif key == 'categories':
                    f_info['categories'] = fmt[key]
                else:
                    f_info[key] = fmt[key]
            # Released...
            released_in: str = fmt.get('released', None)
            # Drop empty entries:
            if released_in == '':
                released_in = None
            # Drop any <ref>.... content:
            if released_in:
                ref_index = released_in.find("<ref")
                if ref_index > -1:
                    released_in = released_in[0:ref_index]
            
            # Set up as a format entity: 
            f = Format(
                registry_id=self.registry_id,
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
                released_in=released_in,
                registry_url=fmt['source'],
                registry_source_data_url=fmt['source'],
                registry_index_data_url=None,
                created=None,
                last_modified=None
            )
            yield f