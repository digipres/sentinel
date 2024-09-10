import os
import logging
from bs4 import BeautifulSoup
from .models import Format

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocFDD():
    registry_id = "loc_fdd"
    source_folder = 'digipres.github.io/_sources/registries/fdd/fddXML'
    warnings = []
    show_parsed_xml_on_errors = False

    def get_formats(self):
        logger.info("Getting transformed format records for registry ID %s..." % self.registry_id)

        for filename in os.listdir(self.source_folder):
            if filename.endswith(".xml"):
                logger.info(f"Parsing {filename}...")
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
                        # If there's a version string, grab it:
                        f_version = None
                        if ", Version " in f_name:
                            f_version = f_name.split(", Version ", 1)[1]
                        # Genre:
                        f_genres = list()
                        for gns in root.findAll('gdfrGenreSelection'):
                            for gn in gns.findAll('gdfrGenre'):
                                f_genres.append(f"gdfr:{gn.text}")
                        # Haz Magic?
                        if root.find('magicNumbers'):
                            f_magic = True
                        else:
                            f_magic = False
                        # Get extensions:
                        extensions = list()
                        for fe in root.findAll('filenameExtension'):
                            for fev in fe.findAll('sigValue'):
                                extensions.append("%s" % fev.text)
                        f_extensions = extensions
                        # Get MIME types:
                        mimetypes = list()
                        for imts in root.findAll('internetMediaType'):
                            for mt in imts.findAll('sigValue'):
                                mimetypes.append(mt.text)
                        f_mimetypes = mimetypes
                        # Find the date:
                        edit_date = root.findAll('date')[-1].text
                        # Create record:
                        f = Format(
                            registry_id=self.registry_id,
                            id=ffd_id,
                            name=f_name,
                            version=f_version,
                            summary=root.find("shortDescription").text,
                            genres=f_genres,
                            extensions=f_extensions,
                            iana_media_types=f_mimetypes,
                            has_magic=f_magic,
                            primary_media_type=None,
                            parent_media_type=None,
                            registry_url=f"https://www.loc.gov/preservation/digital/formats/fdd/{ffd_id}.shtml",
                            registry_source_data_url=f"https://www.loc.gov/preservation/digital/formats/fdd/{ffd_id}.xml",
                            registry_index_data_url=f"https://github.com/digipres/digipres.github.io/blob/master/_sources/registries/fdd/fddXML/{ffd_id}.xml",
                            additional_fields= None,
                            created=edit_date,
                            last_modified=edit_date,
                        )
                        yield f
                    except Exception as e:
                        logger.error(f"Parsing {filename} failed: {e}")
                        self.warnings.append(f"Error when parsing XML from '{filename}': {e}")
                        # Emit extra debug info if possible:
                        if root and self.show_parsed_xml_on_errors:
                            logger.error("XML parsed as:")
                            logger.error(root.prettify())
                            #print(etree.tostring(root, pretty_print=True).decode('utf-8'))


if __name__ == "__main__":
    gen = LocFDD()
    for f in gen.get_formats():
        print(f.model_dump_json())