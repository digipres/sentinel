import mwclient as mw
from mwclient.listing import Category, PageList
import mwparserfromhell

from .models import Software

import logging
logging.basicConfig(level=logging.WARNING)


coptr_host = 'coptr.digipres.org'
user_agent = 'DigiPresFormatIndexClient/0.1 (andrew.jackson@dpconline.org)'
site = mw.Site(coptr_host, path='/', clients_useragent=user_agent)

#for tool_page in site.allpages():
#    pass

#category = site.categories[u"Tool Grid"]
#for page in category:
#    print(page.name)


# {{Infobox tool
# |image=JHOVE.gif
# |purpose=JHOVE provides functions to perform format-specific identification, validation, and characterization of digital objects.
# |homepage=http://jhove.openpreservation.org/
# |license=GNU Lesser General Public License (LGPL)
# |platforms=JHOVE should be usable on any UNIX, Windows, or OS X platform with an appropriate J2SE installation. It should run on any operating system that supports Java 1.5 and has a directory-based file system.
# |formats_in=EPUB, GIF, JP2, JPEG, PDF, PNG, PREMIS (Preservation Metadata Implementation Strategies), TIFF, WARC, XML, AIFF, WAVE, GZIP, ASCII, UTF-8, HTML, MP3
# |function=Encryption Detection, File Format Identification, Metadata Extraction, Validation
# }}

# FIXME this does both at once! One should write the page info needed to JSON. The other should use it.
# But, we don't know everything we need yet, I guess?

category: PageList = site.categories[u"Tools"]
for page in category:
    print(page.name)
    text = page.text()
    wikicode = mwparserfromhell.parse(text)
    templates = wikicode.filter_templates(matches='infobox tool')
    template = templates[0]
    formats = template.get("formats_in", None)
    if formats:
        formats = [f.strip() for f in formats.value.split(",")]
        print(f"  <  {formats}")
    formats = template.get("formats_out", None)
    if formats:
        formats = [f.strip() for f in formats.value.split(",")]
        print(f"  >  {formats}")
    print(page.pageid)
    if isinstance(page, Category):
        for member in page.members():
            print(f"{page.name} > {member.name}")
    else:
        pass
        s = Software(
            id=f"coptr:pageid:{page.pageid}",
            name=page.name,
            version=None,
            license=None,
            registry_url=f"https://{coptr_host}/Special:Redirect/page/{page.pageid}"
        )
        license = template.get('license', None)
        if license:
            s.license = license.value.strip()
        print(s)



# Workflows in Workflow namespace
# Formats is another potential category, but needs patching in via external IDs.