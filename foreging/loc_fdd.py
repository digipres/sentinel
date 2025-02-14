import os
import logging
from bs4 import BeautifulSoup
from .models import Format, Software, Registry, Extension, Genre, MediaType, RegistryDataLogEntry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocFDD():
    registry_id = "lcfdd"
    source_folder = 'digipres.github.io/_sources/registries/fdd/fddXML'
    show_parsed_xml_on_errors = False
    registry = Registry(
        id=registry_id,
        name="LC FDD"
    )

    def get_formats(self, exts, mts, genres):

        fmts = {}

        for filename in os.listdir(self.source_folder):
            if filename.endswith(".xml"):
                logger.debug(f"Parsing {filename}...")
                with open(f"{self.source_folder}/{filename}", "rb") as f:
                    xml = f.read()
                    root = None
                    try:
                        # Alternative code that was more difficult to work with:
                        #parser = etree.XMLParser()
                        #root = etree.parse(BytesIO(xml), parser)
                        root = BeautifulSoup(xml, "xml")
                        ffd_id = root.find('FDD').get('id')
                        f_name = root.find('FDD').get('titleName')

                        # Check if we should keep this one, or if something seems to have gone wrong:
                        if filename != f"{ffd_id}.xml":
                            self.registry.data_log.append(
                                RegistryDataLogEntry(
                                    level="error",
                                    message=f"File name of {filename} does not match embedded FDD ID of {ffd_id}",
                                    url=f"https://www.loc.gov/preservation/digital/formats/fddXML/{filename}"
                                )
                            )
                            continue

                        # If there's a version string, grab it:
                        f_version = None
                        if ", Version " in f_name:
                            f_version = f_name.split(", Version ", 1)[1]
                        # Genre:
                        f_genres = list()
                        for gns in root.findAll('gdfrGenreSelection'):
                            for gn in gns.findAll('gdfrGenre'):
                                f_genres.append(Genre(name=f"gdfr:{gn.text}"))
                        # Haz Magic?
                        if root.find('magicNumbers'):
                            f_magic = True
                        else:
                            f_magic = False
                        # Get extensions:
                        f_extensions = set()
                        for fe in root.findAll('filenameExtension'):
                            for fev in fe.findAll('sigValue'):
                                ext = f"{fev.text}"
                                exts[ext] = exts.get(ext, Extension(id=ext))
                                f_extensions.add(exts[ext])
                        # Get MIME types:
                        f_mimetypes = set()
                        for imts in root.findAll('internetMediaType'):
                            for mt in imts.findAll('sigValue'):
                                f_mimetypes.add(mt.text)
                        # Find the date:
                        edit_date = root.findAll('date')[-1].text
                        # Create record:
                        f = Format(
                            registry=self.registry,
                            id=f"{self.registry_id}:{ffd_id}",
                            name=f_name,
                            version=f_version,
                            summary=root.find("shortDescription").text,
                            genres=f_genres,
                            extensions=list(f_extensions),
                            #iana_media_types=f_mimetypes,
                            has_magic=f_magic,
                            primary_media_type=None,
                            parent_media_type=None,
                            registry_url=f"https://www.loc.gov/preservation/digital/formats/fdd/{ffd_id}/",
                            registry_source_data_url=f"https://www.loc.gov/preservation/digital/formats/fddXML/{filename}",
                            registry_index_data_url=f"https://github.com/digipres/digipres.github.io/blob/master/_sources/registries/fdd/fddXML/{ffd_id}.xml",
                            additional_fields= None,
                            #created=edit_date,
                            #last_modified=edit_date,
                        )
                        fmts[ffd_id] = f

                    except Exception as e:
                        logger.error(f"Parsing {filename} {ffd_id} failed: {e}")
                        self.registry.data_log.append(
                            RegistryDataLogEntry(
                                level='error',
                                message=f"Error when parsing XML from '{filename}': {e}"
                            )
                        )
                        # Emit extra debug info if possible:
                        if root and self.show_parsed_xml_on_errors:
                            logger.error("XML parsed as:")
                            logger.error(root.prettify())
                            #print(etree.tostring(root, pretty_print=True).decode('utf-8'))

        # Return the values:
        for id in fmts:
            f = fmts[id]
            yield f

