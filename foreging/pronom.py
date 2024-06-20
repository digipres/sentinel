import os
import logging
import datetime
from bs4 import BeautifulSoup
from .models import Format

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PRONOM():
    registry_id = "pronom"
    source_folder = 'digipres.github.io/_sources/registries/pronom/'
    warnings = []
    show_parsed_xml_on_errors = False

    def _date_parser(self, pronom_date):
        # PRONOM uses '11 Apr 2024' format so this needs parsing here:
        date = datetime.datetime.strptime(pronom_date, "%d %b %Y")
        return date

    def get_formats(self):
        logger.info("Getting transformed format records for registry ID %s..." % self.registry_id)

        for source_folder_name in ['fmt', 'x-fmt']:
            source_folder = os.path.join(self.source_folder, source_folder_name)

            for filename in os.listdir(source_folder):
                if filename.endswith(".xml"):
                    logger.info(f"Parsing {filename}...")
                    with open(f"{source_folder}/{filename}", "rb") as f:
                        xml = f.read()
                        root = None
                        try:
                            # Alternative code that was more difficult to work with:
                            #parser = etree.XMLParser()
                            #root = etree.parse(BytesIO(xml), parser)
                            root = BeautifulSoup(xml, "xml")
                            ffd_id = f"{source_folder_name}/{filename[0:-4]}"
                            # To Do check FileFormatIdentifier.Identifier matches for FileFormatIdentifier.Identifier.Type == 'PUID'
                            f_name = root.find('FormatName').text
                            if root.find('InternalSignature'):
                                f_magic = True
                            else:
                                f_magic = False
                            # Get extensions:
                            extensions = list()
                            for fe in root.findAll('ExternalSignature'):
                                if fe.find('SignatureType', string='File extension'):
                                    extensions.append(fe.find('Signature').text)
                            f_extensions = extensions
                            # Get MIME types:
                            mimetypes = list()
                            for ffi in root.findAll('FileFormatIdentifier'):
                                if ffi.find('IdentifierType', string='MIME'):
                                    mimetypes.append(ffi.find('Identifier').text)
                            f_mimetypes = mimetypes
                            # Create record:
                            f = Format(
                                registry_id=self.registry_id,
                                id=ffd_id,
                                name=f_name,
                                summary=root.find("FormatDescription").text,
                                extensions=f_extensions,
                                media_types=f_mimetypes,
                                has_magic=f_magic,
                                primary_media_type=None,
                                parent_media_type=None,
                                registry_url=f"https://www.nationalarchives.gov.uk/pronom/{ffd_id}",
                                registry_source_data_url=f"https://www.nationalarchives.gov.uk/pronom/{ffd_id}.xml",
                                registry_index_data_url=f"https://github.com/digipres/digipres.github.io/blob/master/_sources/registries/pronom/{ffd_id}.xml",
                                additional_fields= None,
                                created=self._date_parser(root.find('ProvenanceSourceDate').text),
                                last_modified=self._date_parser(root.find('LastUpdatedDate').text),
                            )
                            yield f
                        except Exception as e:
                            logger.exception(f"Parsing {filename} failed", e)
                            self.warnings.append(f"Error when parsing XML from '{filename}': {e}")
                            # Emit extra debug info if possible:
                            if root and self.show_parsed_xml_on_errors:
                                logger.error("XML parsed as:")
                                logger.error(root.prettify())
                                #print(etree.tostring(root, pretty_print=True).decode('utf-8'))
                            break


if __name__ == "__main__":
    gen = PRONOM()
    gen.show_parsed_xml_on_errors = True
    for f in gen.get_formats():
        print(f.model_dump_json())