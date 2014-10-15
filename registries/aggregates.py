from __future__ import with_statement
from __future__ import print_function
from lxml import etree
from bs4 import BeautifulSoup
from StringIO import StringIO
import yaml
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

def addEntry(results,key,rid,fid,name):
    if not key in results:
        results[key] = {}
        results[key]['name'] = key
        results[key]['identifiers'] = []
    results[key]['identifiers'].append( { 'regId': rid, 'formatId': fid } )

def addFormat(rid,fid,name,hasMagic,extensions,mimetypes,supertype):
    # Add to the formats list:
    if not rid in fmts:
        fmts[rid] = {}
        fmts[rid]['id'] = rid
        fmts[rid]['formats'] = {}
        fmts[rid]['warnings'] = []
    if not fid in fmts[rid]['formats']:
        fmts[rid]['formats'][fid] = {}
    # Populate:
    fmts[rid]['formats'][fid]['name'] = name
    if name == None or name == "":
        fmts[rid]['warnings'].append("Format name for entry %s is empty." % fid)
    elif name != name.strip():
        fmts[rid]['warnings'].append("Format name '%s' for entry %s contains leading and/or trailing whitespace." % (name,fid))
    fmts[rid]['formats'][fid]['hasMagic'] = hasMagic
    fmts[rid]['formats'][fid]['supertype'] = supertype
    fmts[rid]['formats'][fid]['extensions'] = extensions
    fmts[rid]['formats'][fid]['mimetypes'] = mimetypes

    # Assemble cross-references:
    ext_pattern = re.compile("^[A-Za-z0-9_\-\+][A-Za-z0-9_\-\+\.]*$")
    for extension in extensions:
        extension = extension.lower()
        addEntry(exts,extension,rid,fid,name)
        # Also attempt to validate:
        if extension.startswith("."):
            fmts[rid]['warnings'].append("File extension '%s' for entry %s should not start with a '.' (by convention)." % (extension,fid))
        elif not ext_pattern.match(extension):
            fmts[rid]['warnings'].append("File extension '%s' for entry %s does not appear to be a valid file extension." % (extension,fid))
    for mimetype in mimetypes:
        mimetype = mimetype.lower()
        addEntry(mimes,mimetype,rid,fid,name)
        # Also attempt to parse:
        try:
            (type, subtype, params) = parse_mime_type(mimetype)
        except:
            fmts[rid]['warnings'].append("Could not parse MIME type '%s' for entry %s" % (mimetype,fid))



def aggregateFDD():
    rid = "fdd"
    print("Parsing %s..." % rid)

    for filename in os.listdir('fdd/fddXML'):
        if filename.endswith(".xml"):
            # Get Identifier?
            with open('fdd/fddXML/'+filename, "r") as f:
                xml = f.read()
                try:
                  parser = etree.XMLParser()
                  root = etree.parse(StringIO(xml), parser)
                except Exception as e:
                    fmts[rid]['warnings'].append("Error when parsing XML: "+str(e))
                root = BeautifulSoup(xml, "xml")
                #print(root.prettify())
                ffd_id = root.find('FDD').get('id')
                fname = root.find('FDD').get('titleName')
                if root.find('magicNumbers'):
                    hasMagic = True
                else:
                    hasMagic = False
                # Get extensions:
                extensions = list()
                for fe in root.findAll('filenameExtension'):
                    for fev in fe.findAll('sigValue'):
                        extensions.append(fev.text)
                # Get MIME types:
                mimetypes = list()
                for imts in root.findAll('internetMediaType'):
                    for mt in imts.findAll('sigValue'):
                        mimetypes.append(mt.text)
                addFormat(rid,ffd_id,fname,hasMagic,extensions,mimetypes,None)

def aggregateTRiD():
    rid = "trid"
    print("Parsing %s..." % rid)

    for filename in os.listdir('trid/triddefs_xml'):
        if filename.endswith(".trid.xml"):
            # Get Identifier?
            with open('trid/triddefs_xml/'+filename, "r") as f:
                root = etree.parse(f)
                fid = filename[:-9]
                fname = root.findall('Info/FileType')[0].text
                if root.find('FrontBlock') is not None:
                    hasMagic = True
                else:
                    hasMagic = False
                # Get extensions:
                extensions = list()
                for fe in root.findall('Info/Ext'):
                    if(fe.text != None):
                        extensions.append(fe.text)
                # Get MIME types:
                mimetypes = list()
                addFormat(rid,fid,fname,hasMagic,extensions,mimetypes,None)

def aggregatePronom():
    rid = "pronom"
    print("Parsing %s..." % rid)

    # Get identifiers from DROID BinSigs:
    with open("pronom/droid-signature-file.xml", "r") as f:
        root = BeautifulSoup(f, "xml")
        ffc = root.find('FileFormatCollection')
        for ff in ffc.findAll('FileFormat'):
            puid = ff.get('PUID')
            # Build the name:
            fname = ff.get('Name')
            if ff.get('Version') != None:
                fname += " " + ff.get('Version')
            # Has Magic?
            if ff.find('InternalSignatureID'):
                hasMagic = True
            else:
                hasMagic = False
            # Look for extensions:
            extensions = list()
            for ext in ff.findAll('Extension'):
                extensions.append(ext.text)
            # Look for MIME Types:
            mimetypes = list()
            if ff.get('MIMEType') != None:
                for mime in ff.get('MIMEType').split(", "):
                    mimetypes.append(mime)
            addFormat(rid,puid,fname,hasMagic,extensions,mimetypes,None)

def aggregateTika():
    rid = "tika"
    print("Parsing %s..." % rid)

    # Get identifiers from DROID BinSigs:
    with open("tika/tika-mimetypes.xml", "r") as f:
        xml = f.read()
        try:
            parser = etree.XMLParser()
            root = etree.parse(StringIO(xml), parser)
        except Exception as e:
            xml_error = "Error when parsing XML: "+str(e)
            parser = etree.XMLParser(recover=True)
            root = etree.parse(StringIO(xml), parser)
        for ff in root.findall('mime-type'):
            fid = ff.get('type')
            print(ff.sourceline, fid)
            # Build the name:
            fname = None
            if ff.find('_comment') is not None:
                fname = ff.find('_comment').text
            # Has Magic?
            if ff.find('match'):
                hasMagic = True
            else:
                hasMagic = False
            # Look for extensions:
            extensions = list()
            for ext in ff.findall('glob'):
                extension = ext.get('pattern')[2:]
                extensions.append(extension)
            # Look for MIME Types:
            mimetypes = list()
            mimetypes.append(fid)
            if ff.find('alias') is not None:
                for alias in ff.findall('alias'):
                    if alias.get('type'):
                        mimetypes.append(alias.get('type'))
            # Relationships:
            supertype = None
            if ff.find('sub-class-of') is not None:
                supertype = ff.find('sub-class-of').get('type')
            addFormat(rid,fid,fname,hasMagic,extensions,mimetypes,supertype)
        # Also record the XML error, if there was one:
        if ( xml_error ):
            fmts[rid]['warnings'].append(xml_error)

# Set up hashtables to fill:
exts = {}
mimes = {}
fmts = {}

# Grab the data:
aggregateTika()
# Note, add line numbers please:
# https://github.com/anjackson/foreg/blob/master/registries/tika/tika-mimetypes.xml#L4263
aggregatePronom()
aggregateFDD()
aggregateTRiD()

site_dir = "../digipres.github.io/formats"
data_dir = "../digipres.github.io/_data/formats"

# Write out as a data file to feed into other systems:
for fmt in fmts:
    fmts[fmt]['warnings'] = sorted(fmts[fmt]['warnings'])
    fmts[fmt]['stats'] = {}
    fmts[fmt]['stats']['total_warnings'] = len(fmts[fmt]['warnings'])
    fmts[fmt]['stats']['total_formats'] = len(fmts[fmt]['formats'])
    with open("%s/%s.yml" % (data_dir,fmt), 'w') as outfile:
        outfile.write( yaml.safe_dump(fmts[fmt], default_flow_style=False) ) 

extensions = {}
extensions['extensions'] = exts
extensions['stats'] = {}
extensions['stats']['total_extensions'] = len(exts)
with open("%s/extensions.yml" % data_dir, 'w') as outfile:
    outfile.write( yaml.safe_dump(extensions, default_flow_style=False) ) 

mimetypes = {}
mimetypes['mimetypes'] = mimes
mimetypes['stats'] = {}
mimetypes['stats']['total_mimetypes'] = len(mimes)
with open("%s/mimetypes.yml" % data_dir, 'w') as outfile:
    outfile.write( yaml.safe_dump(mimetypes, default_flow_style=False) ) 

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

