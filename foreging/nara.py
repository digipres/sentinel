import os
import logging
from rdflib import Graph, RDF, DCTERMS
from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef
from .models import Format

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#
# Define RDF entities needed to work with this source:
#
class NARA(DefinedNamespace):
    FileFormat: URIRef  # File Format
    category: URIRef
    formatName: URIRef 
    preservationAction: URIRef
    preservationPlan: URIRef
    riskLevel: URIRef
    tools: URIRef

    _NS = Namespace("https://www.archives.gov/data/lod/dpframework/def/")

class WDT(DefinedNamespace):
    p1163: URIRef # Media Type
    p1195: URIRef # File Extension
    p2748: URIRef # PRONOM link
    p3381: URIRef # File Formats Wiki link
    p973: URIRef  # Wikipedia link

    _NS = Namespace("http://www.wikidata.org/entity/")



#
# NARA File Format Preservation Plan parser
#
class NARA_FFPP():
    registry_id = "nara_ffpp"
    source_file = 'digipres.github.io/_sources/registries/nara/fileformats.ttl'
    warnings = []

    def get_formats(self):
        logger.info("Getting transformed format records for registry ID %s..." % self.registry_id)

        g = Graph()
        g.parse(self.source_file)


        for s, p, o in g.triples((None, RDF.type, NARA.FileFormat)):
            ff_id = g.value(s, DCTERMS.identifier)
            additionals = {}
            for p in [ NARA.preservationAction, NARA.preservationPlan, NARA.tools, WDT.p2748, WDT.p3381, WDT.p973]:
                value = g.value(s, p)
                if value:
                    additionals[p] = [o for s, p, o in g.triples((s, p, None))]
            # Set up as a format entity: 
            f = Format(
                registry_id=self.registry_id,
                id=ff_id,
                name=g.value(s, NARA.formatName),
                version=None,
                summary=g.value(s, DCTERMS.description),
                genres=[o for s, p, o in g.triples((s, NARA.category, None))],
                extensions=[o for s, p, o in g.triples((s, WDT.p1195, None))],
                iana_media_types=[o for s, p, o in g.triples((s, WDT.p1163, None))],
                has_magic=False,
                primary_media_type=None,
                parent_media_type=None,
                registry_url=f"https://www.archives.gov/preservation/digital-preservation/linked-data#{ff_id}",
                registry_source_data_url=f"https://www.archives.gov/files/lod/dpframework/id/{ff_id}.ttl",
                registry_index_data_url=f"https://github.com/digipres/digipres.github.io/blob/master/_sources/registries/nara/fileformats.ttl#{ff_id}",
                additional_fields=additionals,
                created=None,
                last_modified=None,
            )
            yield f


if __name__ == "__main__":
    gen = NARA_FFPP()
    for f in gen.get_formats():
        print(f.model_dump_json())