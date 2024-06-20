from __future__ import with_statement
from __future__ import print_function
from lxml import etree
from bs4 import BeautifulSoup
from io import BytesIO
from operator import itemgetter
from collections import defaultdict
import yaml
import json
import sys
import os
import re


def parse_mime_type(mime_type):
    """Carves up a mime_type and returns a tuple of the
       (type, subtype, params) where 'params' is a dictionary
       of all the parameters for the media range.
       For example, the media range 'application/xhtml;q=0.5' would
       get parsed into:

       ('application', 'xhtml', {'q', '0.5'})
       """
    parts = mime_type.split(";")
    params = dict([tuple([s.strip() for s in param.split("=")]) for param in parts[1:] ])
    (type, subtype) = parts[0].split("/")
    return (type.strip(), subtype.strip(), params)

def addEntry(results,key,rid,fid):
    if not key in results:
        results[key] = {}
        results[key]['name'] = key
        results[key]['identifiers'] = []
    results[key]['identifiers'].append( { 'regId': rid, 'formatId': fid } )

def addMIMEType(rid,fid,mimetype,supertype):
    if not mimetype in mimes:
        mimes[mimetype] = {}
        mimes[mimetype]['id'] = mimetype
        mimes[mimetype]['identifiers'] = []
    mimes[mimetype]['identifiers'].append( { 'regId': rid, 'formatId': fid } )
    if supertype != None and supertype != '':
        mimes[mimetype]['supertype'] = supertype

def addFormat(rid,fid,finfo):
    # Convert possible sets to lists:
    for key in ['extensions', 'mimetypes', 'identifiers']:
        if key in finfo:
            finfo[key] = list(set(finfo[key]))

    # Add to the formats list:
    if not rid in fmts:
        fmts[rid] = {}
        fmts[rid]['id'] = rid
        fmts[rid]['formats'] = {}
        fmts[rid]['warnings'] = []
        fmts[rid]['stats'] = {}
        fmts[rid]['stats']['empty_names'] = 0
    if not fid in fmts[rid]['formats']:
        fmts[rid]['formats'][fid] = {}
    # Populate:
    if ('name' not in finfo) or finfo['name'] == "":
        fmts[rid]['stats']['empty_names'] += 1
    elif finfo['name'] != finfo['name'].strip():
        fmts[rid]['warnings'].append("Format name '%s' for entry %s contains leading and/or trailing whitespace." % (finfo['name'],fid))

    # Assemble cross-references:
    ext_pattern = re.compile("^\*?[\.|-]?[A-Za-z0-9_~\-\+\?\!\$][A-Za-z0-9_\% \-\+\.\?\!\$]*$")
    for extension in finfo['extensions']:
        extension = extension.lower()
        addEntry(exts,extension,rid,fid)
        # Also attempt to validate:
        if not ext_pattern.match(extension):
            fmts[rid]['warnings'].append("Glob '%s' for entry %s does not appear to be a valid filename specification." % (extension,fid))
    # MIME
    if 'supertype' not in finfo:
        finfo['supertype'] = None
    for mimetype in finfo['mimetypes']:
        mimetype = mimetype.lower()
        addMIMEType(rid,fid,mimetype,finfo['supertype'])
        # Also attempt to parse:
        try:
            (type, subtype, params) = parse_mime_type(mimetype)
        except:
            fmts[rid]['warnings'].append("Could not parse MIME type '%s' for entry %s" % (mimetype,fid))
    # And add:
    fmts[rid]['formats'][fid] = finfo




def aggregateTRiD():
    rid = "trid"
    print("Parsing %s..." % rid)

    for filename in os.listdir('digipres.github.io/_sources/registries/trid/triddefs_xml'):
        if filename.endswith(".trid.xml"):
            # Get Identifier?
            with open('digipres.github.io/_sources/registries/trid/triddefs_xml/'+filename, "r") as f:
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
                            extensions.append("*.%s" % ext.lower())
                finfo['extensions'] = extensions
                # Get MIME types:
                finfo['mimetypes'] = list()
                addFormat(rid,fid,finfo)

def aggregatePronom():
    rid = "pronom"
    print("Parsing %s..." % rid)

    # Get identifiers from DROID BinSigs:
    with open("digipres.github.io/_sources/registries/pronom/droid-signature-file.xml", "r") as f:
        parser = etree.XMLParser()
        root = etree.parse(f, parser)
        ffc = root.find('{http://www.nationalarchives.gov.uk/pronom/SignatureFile}FileFormatCollection')
        for ff in ffc.findall('{http://www.nationalarchives.gov.uk/pronom/SignatureFile}FileFormat'):
            finfo = {}
            puid = ff.get('PUID')
            finfo['source'] = "droid-signature-file.xml#L%s" % ff.sourceline
            # Build the name:
            finfo['name'] = ff.get('Name')
            if ff.get('Version') != None:
                finfo['name'] += " " + ff.get('Version')
            # Has Magic?
            if ff.find('{http://www.nationalarchives.gov.uk/pronom/SignatureFile}InternalSignatureID') is not None:
                finfo['hasMagic'] = True
            else:
                finfo['hasMagic'] = False
            # Look for extensions:
            extensions = list()
            for ext in ff.findall('{http://www.nationalarchives.gov.uk/pronom/SignatureFile}Extension'):
                extensions.append( "*.%s" % ext.text)
            finfo['extensions'] = extensions
            # Look for MIME Types:
            mimetypes = list()
            if ff.get('MIMEType') != None:
                for mime in ff.get('MIMEType').split(", "):
                    if ff.get('Version'):
                        mime = mime + "; version=\"%s\"" % ff.get('Version')
                    mimetypes.append(mime)
            if len(mimetypes) > 0:
                finfo['primary_mimetype'] = mimetypes[0]
                if ff.get('Version'):
                    finfo['supertype'] = mimetypes[0].split(';')[0]
            finfo['mimetypes'] = mimetypes
            addFormat(rid,puid,finfo)

def aggregateTika():
    rid = "tika"
    print("Parsing %s..." % rid)

    # Get identifiers from DROID BinSigs:
    with open("digipres.github.io/_sources/registries/tika/tika-mimetypes.xml", "rb") as f:
        xml = f.read()
        warnings = []
        try:
            parser = etree.XMLParser()
            root = etree.parse(BytesIO(xml), parser)
        except Exception as e:
            warnings.append("Error when parsing XML: "+str(e))
            parser = etree.XMLParser(recover=True)
            root = etree.parse(BytesIO(xml), parser)
        for ff in root.findall('mime-type'):
            finfo = {}
            fid = ff.get('type')
            finfo['id'] = fid
            finfo['source'] = "tika-mimetypes.xml#L%s" % ff.sourceline
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
                extension = ext.get('pattern')
                extensions.append(extension)
            finfo['extensions'] = extensions
            # Look for MIME Types:
            mimetypes = list()
            mimetypes.append(fid)
            if ff.find('alias') is not None:
                for alias in ff.findall('alias'):
                    if alias.get('type'):
                        if alias.get('type') not in mimetypes:
                            mimetypes.append(alias.get('type'))
                        else:
                            warnings.append("Duplicate MIME type %s for type %s." % (alias.get('type'), fid))
            # TODO Spot duplicate aliases.
            finfo['mimetypes'] = mimetypes
            # Relationships:
            if ff.find('sub-class-of') is not None:
                finfo['supertype'] = ff.find('sub-class-of').get('type')
                if finfo['supertype'] == fid:
                    warnings.append("Format %s has itself as a supertype!" % fid )
            addFormat(rid,fid,finfo)
        # Also record the XML error, if there was one:
        fmts[rid]['warnings'] += warnings

def aggregateFFW():
    rid = "ffw"
    print("Parsing %s..." % rid)
    stream = open("digipres.github.io/_sources/registries/mediawikis/ffw.yml", 'r')
    ffw = yaml.safe_load(stream)
    stream.close()

    for fmt in ffw['formats']:
        finfo = {}
        finfo['extensions'] = []
        finfo['mimetypes'] = []
        finfo['hasMagic'] = False
        fid = fmt['name'].lower()
        for key in fmt:
            if key == 'extensions':
                for ext in fmt[key]:
                    finfo['extensions'].append("*.%s" % ext)
            else:
                finfo[key] = fmt[key]
        #
        addFormat(rid,fid,finfo)

def aggregateGithubLinguist():
    rid = "githublinguist"
    print("Parsing %s..." % rid)
    stream = open("digipres.github.io/_sources/registries/githublinguist/languages.yml", 'r')
    gl = yaml.safe_load(stream)
    stream.close()

    for fmt in gl:
        finfo = {}
        finfo['name'] = fmt
        finfo['extensions'] = []
        finfo['mimetypes'] = []
        finfo['hasMagic'] = False
        fid = gl[fmt]['language_id']
        for key in gl[fmt]:
            if key == 'extensions':
                for ext in gl[fmt][key]:
                    finfo['extensions'].append("*%s" % ext)
            elif key == 'codemirror_mime_type':
                finfo['mimetypes'].append(gl[fmt][key])
            else:
                finfo[key] = gl[fmt][key]
        #
        addFormat(rid,fid,finfo)

def aggregateWikiData():
    rid = "wikidata"
    print("Parsing %s..." % rid)
    with open ("digipres.github.io/_sources/registries/wikidata/wikidata.json", 'r') as f:
        wd = json.load(f)

    current_fid = None

    for fmt in wd:
        fid = fmt['id']
        # items are ordered by ID, so we can aggregate as we go
        if fid != current_fid:
            # Store the last record:
            if current_fid:
                addFormat(rid,current_fid,finfo)
            current_fid = fid
            # Start a new record:
            finfo = {}
            finfo['name'] = fmt['name']
            finfo['source'] = fmt['source']
            finfo['extensions'] = set()
            finfo['mimetypes'] = set()
            finfo['hasMagic'] = False
        # Aggregate value for each ID
        for key in fmt:
            if key == 'extension' and fmt[key]:
                finfo['extensions'].add("*.%s" % fmt[key])
            if key == 'mimetype' and fmt[key]:
                finfo['mimetypes'].add(fmt[key])
            if key == 'sig' and fmt[key]:
                finfo['hasMagic'] = True

    # Add the final one:
    if current_fid:
        addFormat(rid,current_fid,finfo)


# Set up hashtables to fill:
exts = {}
mimes = {}
fmts = {}

# Grab the data:
aggregateFFW()
aggregateTika()
aggregatePronom()
aggregateTRiD()
aggregateFDD()
aggregateGithubLinguist()
aggregateWikiData()

# Resolve MIME heirarchy...
print("Resolving MIME type heirarchy...")
for mt in mimes:
    mimes[mt]['sort_key'] = mt
    mimes[mt]['sort_depth'] = 0
    current_type = mt
    while 'supertype' in mimes[current_type]:
        supertype = mimes[current_type]['supertype']
        if current_type == supertype:
            print("ERROR: There's a loop in the heirarchy! supertype(%s) == %s" % (current_type,supertype))
            break
        if supertype in mimes:
            current_type = supertype
            mimes[mt]['sort_key'] = supertype + " . " + mimes[mt]['sort_key']
            mimes[mt]['sort_depth'] += 1
        else:
            print("ERROR: Supertype %s not found!" % supertype )
            break

# Set output locations:
site_dir = "digipres.github.io/formats"
data_dir = "digipres.github.io/_data/formats"

# Output:
print("Outputting MIME types...")
mimetypes = {}
mimetypes['mimetypes'] = sorted(mimes.items(), key=lambda x: x[1]['sort_key'])
mimetypes['stats'] = {}
mimetypes['stats']['total_mimetypes'] = len(mimes)
with open("%s/mimetypes.yml" % data_dir, 'w') as outfile:
    outfile.write( yaml.safe_dump(mimetypes, default_flow_style=False) )

print("Outputting file extensions...")
extensions = {}
extensions['extensions'] = exts
extensions['stats'] = {}
extensions['stats']['total_extensions'] = len(exts)
with open("%s/extensions.yml" % data_dir, 'w') as outfile:
    outfile.write( yaml.safe_dump(extensions, default_flow_style=False) )

# Write out Venn data, starting from a list like [extension] -> Registry_ID:
print("Outputting Venn data based on extensions...")
# Key all the Registry_ID-to-integer mappings:
vennls = {}
i = 0
for fmt in fmts:
    vennls[fmt] = str(i)
    i += 1
# Now build up the counts, both overlaps and totals:
vennds = defaultdict(int)
venndsl = defaultdict(list)
vennlt = defaultdict(int)
vennids = {}
# Loop over all extensions:
for extension in exts:
    regs = set()
    regIds = set()
    # Loop over each registry the extension appears in:
    for ridder in exts[extension]['identifiers']:
        regs.add(vennls[ridder['regId']])
        regIds.add(ridder['regId'])
    for rid in regs:
        vennlt[rid] += 1
    # Build a unique key for each registry combination:
    key = ','.join(sorted(regs))
    # Use the key to build up each overlap set:
    vennids[key] = sorted(regIds)
    venndsl[key].append(extension)
    vennds[key] += 1
# Now assemble data to write out:
vennd = {}
vennd['sets'] = []
for fmt in fmts:
    vennd['sets'].append( { 'regId': fmt, 'size': vennlt[vennls[fmt]] } )
vennd['overlaps'] = []
for key, value in sorted(vennds.items(), key=itemgetter(1), reverse=True):
    vennd['overlaps'].append( { 'sets': "[%s]" % key, 'regIds': vennids[key], 'size': value, 'extensions': venndsl[key] } )
with open("%s/extensions-venn.yml" % data_dir, 'w') as outfile:
    outfile.write( yaml.safe_dump(vennd, default_flow_style=False) )


# Write out as a data file to feed into other systems:
for fmt in fmts:
    print("Outputting per-source format data for %s..." % fmt)
    # Skip through formats and make more stats:
    total_w_glob = 0
    total_w_magic = 0
    total_w_mime = 0
    all_extensions = []
    all_mimetypes = []
    for findex in fmts[fmt]['formats']:
        finfo = fmts[fmt]['formats'][findex]
        if finfo['hasMagic']:
            total_w_magic += 1
        if len(finfo['extensions']) > 0:
            total_w_glob += 1
            all_extensions.extend(finfo['extensions'])
        if len(finfo['mimetypes']) > 0:
            total_w_mime += 1
            all_mimetypes.extend(finfo['mimetypes'])
    fmts[fmt]['stats']['total_w_magic'] = total_w_magic
    fmts[fmt]['stats']['total_w_glob'] = total_w_glob
    fmts[fmt]['stats']['total_w_mime'] = total_w_mime
    fmts[fmt]['stats']['total_extensions'] = len(all_extensions) 
    fmts[fmt]['stats']['total_unique_extensions'] = len(set(all_extensions))
    fmts[fmt]['stats']['total_mimetypes'] = len(all_mimetypes) 
    fmts[fmt]['stats']['total_unique_mimetypes'] = len(set(all_mimetypes))
    # Warn about empty names:
    if fmts[fmt]['stats']['empty_names'] > 0:
        fmts[fmt]['warnings'].append("There are %i format records with empty 'name' fields." % fmts[fmt]['stats']['empty_names'])
    fmts[fmt]['warnings'] = sorted(fmts[fmt]['warnings'])
    fmts[fmt]['stats']['total_warnings'] = len(fmts[fmt]['warnings'])
    fmts[fmt]['stats']['total_formats'] = len(fmts[fmt]['formats'])
    with open("%s/%s.yml" % (data_dir,fmt), 'w') as outfile:
        outfile.write( yaml.safe_dump(fmts[fmt], default_flow_style=False) )


# Write out lots of pages for individual formats:
#for extension in exts:
#    if extension == '':
#        filename = '-no-extension-'
#    else:
#        filename = extension.replace('/','-')
#    with open("%s/extensions/%s.html" % (site_dir,filename), 'w') as outfile:
#        outdata = {}
#        outdata['permalink'] = "/formats/extensions/%s/" % extension
#        outdata['layout'] = "format"
#        outdata['title'] = "*.%s files" % extension
#        outdata['identifiers'] = exts[extension]
#        outfile.write("---\n")
#        outfile.write(yaml.safe_dump(outdata, default_flow_style=False))
#        outfile.write("---\n")
