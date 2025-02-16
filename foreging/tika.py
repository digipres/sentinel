import json
import yaml
from lxml import etree
from io import BytesIO
import logging
from .models import Format, Software, Registry, Extension, Genre, MediaType, RegistryDataLogEntry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#
class Tika():
    source_file = "digipres.github.io/_sources/registries/tika/tika-mimetypes.xml"
    source_url = "https://svn.apache.org/repos/asf/tika/trunk/tika-core/src/main/resources/org/apache/tika/mime/tika-mimetypes.xml"
    index_url = "https://github.com/digipres/digipres.github.io/blob/master/_sources/registries/tika/tika-mimetypes.xml"
    # Set up the Registry object for this class:
    registry_id = "tika"
    registry = Registry(
        id=registry_id, 
        name="Apache Tika", 
        url="https://tika.apache.org/",
        id_prefix=None,
        index_data_url=index_url
        )

    def get_formats(self, exts, mts, gnrs):
        fmts = []
        with open(self.source_file, "rb") as f:
            xml = f.read()
            log = []
            try:
                parser = etree.XMLParser()
                root = etree.parse(BytesIO(xml), parser)
            except Exception as e:
                log.append(
                    RegistryDataLogEntry(
                        level='warning', 
                        message="Error when parsing XML: "+str(e)
                    )
                )
                parser = etree.XMLParser(recover=True)
                root = etree.parse(BytesIO(xml), parser)
            for ff in root.findall('mime-type'):
                finfo = {}
                fid = ff.get('type')
                finfo['id'] = fid
                finfo['source'] = f"#L{ff.sourceline}"
                # Build the name:
                if ff.find('_comment') is not None:
                    finfo['name'] = ff.find('_comment').text
                # Has Magic?
                if ff.find('magic') is not None:
                    finfo['hasMagic'] = True
                else:
                    finfo['hasMagic'] = False
                # Look for extensions:
                extensions = list()
                for ext in ff.findall('glob'):
                    extension = ext.get('pattern').replace('*.','') # Strip the glob
                    exts[extension] = exts.get(extension, Extension(id=extension))
                    extensions.append(exts[extension])
                finfo['extensions'] = extensions
                # Look for MIME Types:
                mimetypes = list()
                mimetypes.append(fid)
                if ff.find('alias') is not None:
                    for alias in ff.findall('alias'):
                        mt = alias.get('type')
                        if mt:
                            if mt not in mimetypes:
                                mimetypes.append(mt)
                            else:
                                log.append(
                                    RegistryDataLogEntry(
                                        level='warning', 
                                        message="Duplicate MIME type %s for type %s." % (alias.get('type'), fid)
                                    ))
                # TODO Spot duplicate aliases.
                finfo['mimetypes'] = mimetypes
                # Relationships:
                if ff.find('sub-class-of') is not None:
                    finfo['supertype'] = ff.find('sub-class-of').get('type')
                    if finfo['supertype'] == fid:
                        log.append(
                            RegistryDataLogEntry(
                                level="warning",
                                message="Format %s has itself as a supertype!" % fid
                            ))
                #addFormat(rid,fid,finfo)
                # Also record the XML error, if there was one:
                self.registry.data_log.extend(log)

                # Post-process mimetypes:
                media_types = []
                for mt in finfo['mimetypes']:
                    mts[mt] = mts.get(mt, MediaType(id=mt))
                    media_types.append(mts[mt])
                parent = finfo.get('supertype', None)

                # Set up as a format entity: 
                f = Format(
                    registry=self.registry,
                    id=f"{self.registry_id}:{fid}",
                    name=finfo.get('name', None),
                    version=None,
                    summary=None,
                    genres=[],
                    extensions=list(finfo['extensions']),
                    media_types=media_types,
                    has_magic=finfo['hasMagic'],
                    primary_media_type=media_types[0].id,
                    parent_media_type=parent,
                    registry_url=None,
                    registry_source_data_url=self.source_url + finfo['source'],
                    registry_index_data_url=self.index_url + finfo['source'],
                    created=None,
                    last_modified=None
                )
                # And record the entry:
                fmts.append(f)

        # Now yield them, so all the log entries get stored too:
        for f in fmts:
            yield f