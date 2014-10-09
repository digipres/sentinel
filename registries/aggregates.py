from __future__ import with_statement
from __future__ import print_function
from BeautifulSoup import BeautifulSoup
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
        results[key] = []
    results[key].append("%s:%s" % ( rid, fid ) )

def addFormat(rid,fid,name,hasMagic,extensions,mimetypes,supertype):
    # Add to the formats list:
    if not rid in fmts:
        fmts[rid] = {}
        fmts[rid]['formats'] = {}
        fmts[rid]['errors'] = []
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
            fmts[rid]['errors'].append("File extension '%s' for entry %s should not start with a '.' (by convention)." % (extension,fid))
        elif not ext_pattern.match(extension):
            fmts[rid]['warnings'].append("File extension '%s' for entry %s does not appear to be a valid file extension." % (extension,fid))
    for mimetype in mimetypes:
        mimetype = mimetype.lower()
        addEntry(mimes,mimetype,rid,fid,name)
        # Also attempt to parse:
        try:
            (type, subtype, params) = parse_mime_type(mimetype)
        except:
            fmts[rid]['errors'].append("Could not parse MIME type '%s' for entry %s" % (mimetype,fid))



def aggregateFDD():
    rid = "fdd"
    for filename in os.listdir('fdd/fddXML'):
        if filename.endswith(".xml"):
            # Get Identifier?
            with open('fdd/fddXML/'+filename, "r") as f:
                soup = BeautifulSoup(f.read())
                ffd_id = soup.find('fdd:fdd').get('id')
                fname = soup.find('fdd:fdd').get('titlename')
                if soup.find('fdd:magicnumbers'):
                    hasMagic = True
                else:
                    hasMagic = False
                # Get extensions:
                extensions = list()
                for fe in soup.findAll('fdd:filenameextension'):
                    for fev in fe.findAll('fdd:sigvalue'):
                        extensions.append(fev.text)
                # Get MIME types:
                mimetypes = list()
                for imts in soup.findAll('fdd:internetmediatype'):
                    for mt in imts.findAll('fdd:sigvalue'):
                        mimetypes.append(mt.text)
                addFormat(rid,ffd_id,fname,hasMagic,extensions,mimetypes,None)

def aggregateTRiD():
    rid = "trid"
    for filename in os.listdir('trid/triddefs_xml'):
        if filename.endswith(".trid.xml"):
            # Get Identifier?
            with open('trid/triddefs_xml/'+filename, "r") as f:
                soup = BeautifulSoup(f.read())
                fid = filename[:-9]
                fname = soup.find('filetype').text
                if soup.find('frontblock'):
                    hasMagic = True
                else:
                    hasMagic = False
                # Get extensions:
                extensions = list()
                for fe in soup.findAll('ext'):
                    extensions.append(fe.text)
                # Get MIME types:
                mimetypes = list()
                addFormat(rid,fid,fname,hasMagic,extensions,mimetypes,None)

def aggregatePronom():
    rid = "pronom"

    # Get identifiers from DROID BinSigs:
    with open("pronom/droid-signature-file.xml", "r") as f:
        soup = BeautifulSoup(f.read())
        for ff in soup.findAll('fileformat'):
            puid = ff.get('puid')
            # Build the name:
            fname = ff.get('name')
            if ff.get('version') != None:
                fname += " " + ff.get('version')
            # Has Magic?
            if ff.find('internalsignatureid'):
                hasMagic = True
            else:
                hasMagic = False
            # Look for extensions:
            extensions = list()
            for ext in ff.findAll('extension'):
                extensions.append(ext.text)
            # Look for MIME Types:
            mimetypes = list()
            if ff.get('mimetype') != None:
                for mime in ff.get('mimetype').split(", "):
                    mimetypes.append(mime)
            addFormat(rid,puid,fname,hasMagic,extensions,mimetypes,None)

def aggregateTika():
    rid = "tika"

    # Get identifiers from DROID BinSigs:
    with open("tika/tika-mimetypes.xml", "r") as f:
        soup = BeautifulSoup(f.read())
        for ff in soup.findAll('mime-type'):
            fid = ff.get('type')
            # Build the name:
            fname = None
            if ff.find('_comment'):
                fname = ff.find('_comment').text
            # Has Magic?
            if ff.find('match'):
                hasMagic = True
            else:
                hasMagic = False
            # Look for extensions:
            extensions = list()
            for ext in ff.findAll('glob'):
                extension = ext.get('pattern')[2:]
                extensions.append(extension)
            # Look for MIME Types:
            mimetypes = list()
            mimetypes.append(fid)
            if ff.find('alias'):
                for alias in ff.findAll('alias'):
                    if alias.get('type'):
                        mimetypes.append(alias.get('type'))
            # Relationships:
            supertype = None
            if ff.find('sub-class-of'):
                supertype = ff.find('sub-class-of').get('type')
            addFormat(rid,fid,fname,hasMagic,extensions,mimetypes,supertype)

# Set up hashtables to fill:
exts = {}
mimes = {}
fmts = {}

# Grab the data:
aggregateTika()
aggregatePronom()
aggregateFDD()
aggregateTRiD()

# Write out as a data file to feed into other systems:
for fmt in fmts:
    with open("aggregated/formats/%s.yml" % fmt, 'w') as outfile:
        outfile.write( yaml.safe_dump(fmts[fmt], default_flow_style=False) ) 
with open("aggregated/extensions.yml", 'w') as outfile:
    outfile.write( yaml.safe_dump(exts, default_flow_style=False) ) 
with open("aggregated/mimetypes.yml", 'w') as outfile:
    outfile.write( yaml.safe_dump(mimes, default_flow_style=False) ) 
