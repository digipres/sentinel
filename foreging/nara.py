import json
import logging
from rdflib import Graph, RDF, DCTERMS
from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef
from .models import Format, Software, Registry, Extension, Genre, MediaType, RegistryDataLogEntry

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
    registry_id = "nara-ffpp"
    source_file = 'digipres.github.io/_sources/registries/nara/fileformats.ttl'
    warnings = []
    registry = Registry(
        id=registry_id,
        name="NARA FFPP",
        url="https://www.archives.gov/preservation/digital-preservation/linked-data"
    )

    def get_formats(self, exts, mts, grs):

        g = Graph()
        g.parse(self.source_file)

        for s, p, o in g.triples((None, RDF.type, NARA.FileFormat)):
            ff_id = f"{self.registry_id}:{g.value(s, DCTERMS.identifier)}"
            # Grab: Action, Plan, Tools, PUID, FFW, Described-At
            additional = {}
            for p in [ NARA.preservationAction, NARA.preservationPlan, WDT.p2748, WDT.p3381, WDT.p973]:
                value = g.value(s, p)
                if value:
                    additional[p] = [o for s, p, o in g.triples((s, p, None))]
            logger.debug("Additional fields: " + json.dumps(additional, indent=2))
            # Set up entities:
            extensions = set()
            for ext in [o for s, p, o in g.triples((s, WDT.p1195, None))]:
                ext = str(ext)
                exts[ext] = exts.get(ext, Extension(id=ext))
                extensions.add(exts[ext])
            genres = []
            for genre in [o for s, p, o in g.triples((s, NARA.category, None))]:
                genre = str(genre)
                grs[genre] = grs.get(genre, Genre(name=genre))
                genres.append(grs[genre])
            media_types = []
            for mt in [o for s, p, o in g.triples((s, WDT.p1163, None))]:
                mt = str(mt)
                mts[mt] = mts.get(mt, MediaType(id=mt))
                media_types.append(mts[mt])
            readers = []
            for tool in [o for s, p, o in g.triples((s, NARA.tools, None))]:
                s = Software(
                    registry=self.registry,
                    id=f"{ff_id}+{len(readers)}",
                    name=str(tool)
                )
                readers.append(s)
            
            # Set up as a format entity: 
            f = Format(
                registry_id=self.registry_id,
                id=ff_id,
                name=g.value(s, NARA.formatName),
                version=None,
                summary=g.value(s, DCTERMS.description),
                genres=genres,
                extensions=list(extensions),
                media_types=media_types,
                has_magic=False,
                primary_media_type=None,
                parent_media_type=None,
                registry_url=f"https://www.archives.gov/preservation/digital-preservation/linked-data#{ff_id}",
                registry_source_data_url=f"https://www.archives.gov/files/lod/dpframework/id/{ff_id}.ttl",
                registry_index_data_url=f"https://github.com/digipres/digipres.github.io/blob/master/_sources/registries/nara/fileformats.ttl#{ff_id}",
                created=None,
                last_modified=None,
                readers=readers
            )
            yield f


