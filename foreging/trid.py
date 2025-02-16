import json
import yaml
import os
from lxml import etree
from io import BytesIO
import logging
from .models import Format, Software, Registry, Extension, Genre, MediaType, RegistryDataLogEntry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#
class TrID():
    source_dir = "digipres.github.io/_sources/registries/trid"
    source_url = ""
    index_url = "https://github.com/digipres/digipres.github.io/tree/master/_sources/registries/trid/triddefs_xml/"
    # Set up the Registry object for this class:
    registry_id = "trid"
    registry = Registry(
        id=registry_id, 
        name="TrID - File Identifier", 
        url="https://www.mark0.net/soft-trid-e.html",
        id_prefix=None,
        index_data_url=None
        )
    
    fmts = []

    def add_format(self, fid, finfo, exts, mts, gnrs):
        media_types = []
        for mt in finfo['mimetypes']:
            mts[mt] = mts.get(mt, MediaType(id=mt))
            media_types.append(mts[mt])
        extensions = []
        for ext in finfo['extensions']:
            exts[ext] = exts.get(ext, Extension(id=ext))
            extensions.append(exts[ext])
        # Set up as a format entity: 
        f = Format(
            registry=self.registry,
            id=f"{self.registry_id}:{fid}",
            name=finfo.get('name', None),
            version=None,
            summary=None,
            genres=[],
            extensions=extensions,
            media_types=media_types,
            has_magic=finfo['hasMagic'],
            primary_media_type=None,
            parent_media_type=None,
            registry_url=None,
            registry_source_data_url=self.source_url + finfo['source'],
            registry_index_data_url=self.index_url + finfo['source'],
            created=None,
            last_modified=None
        )
        # And record the entry:
        self.fmts.append(f)

 

    def get_formats(self, exts, mts, gnrs):
        for filename in os.listdir(f'{self.source_dir}/triddefs_xml'):
            if filename.endswith(".trid.xml"):
                # Get Identifier?
                with open(f'{self.source_dir}/triddefs_xml/'+filename, "r") as f:
                    finfo = {}
                    finfo['source'] = filename
                    root = etree.parse(f)
                    fid = filename[:-9]
                    finfo['name'] = root.findall('Info/FileType')[0].text
                    if root.find('FrontBlock') is not None:
                        finfo['hasMagic'] = True
                    else:
                        finfo['hasMagic'] = False
                    # Get extensions:
                    extensions = list()
                    for fe in root.findall('Info/Ext'):
                        if(fe.text != None):
                            for ext in fe.text.split("/"):
                                if ext not in extensions:
                                    extensions.append("%s" % ext.lower())
                    finfo['extensions'] = extensions
                    # Get MIME types:
                    finfo['mimetypes'] = list()
                    self.add_format(fid, finfo, exts, mts, gnrs)

        # Now yield them, so all the log entries get stored too:
        for f in self.fmts:
            yield f