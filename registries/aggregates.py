from __future__ import with_statement
from __future__ import print_function
from BeautifulSoup import BeautifulSoup
import yaml
import os

def addEntry(results,key,rid,fid,name):
    if not key in results:
        results[key] = {}
        results[key][rid] = {}
    if not fid in results[key][rid]:
        results[key][rid] = {}
        results[key][rid]['name'] = name


def aggregateFDD(exts,mimes):
    rid = "fdd"
    for filename in os.listdir('fdd/fddXML'):
        if filename.endswith(".xml"):
            # Get Identifier?
            with open('fdd/fddXML/'+filename, "r") as f:
                soup = BeautifulSoup(f.read())
                ffd_id = soup.find('fdd:fdd').get('id')
                for fe in soup.findAll('fdd:filenameextension'):
                    for fev in fe.findAll('fdd:sigvalue'):
                        print(ffd_id,fev.text)




def aggregatePronom(exts,mimes):
    rid = "pronom"

    # Get identifiers from DROID BinSigs:
    with open("pronom/droid-signature-file.xml", "r") as f:
        soup = BeautifulSoup(f.read())
        for ff in soup.findAll('fileformat'):
            puid = ff.get('puid')
            # Build the name:
            pname = ff.get('name')
            if ff.get('version') != None:
                pname += " " + ff.get('version')
            # Look for extensions:
            for ext in ff.findAll('extension'):
                extension = ext.text
                addEntry(exts,extension,rid,puid,pname)
            # Look for MIME Types:
            if ff.get('mimetype') != None:
                for mime in ff.get('mimetype').split(", "):
                    addEntry(mimes,mime,rid,puid,pname)


exts = {}
mimes = {}

#aggregatePronom(exts,mimes)
aggregateFDD(exts,mimes)

# Write out as a data file to feed into other systems:
with open("extensions.yml", 'w') as outfile:
    outfile.write( yaml.safe_dump(exts, default_flow_style=False) ) 
with open("mimetypes.yml", 'w') as outfile:
    outfile.write( yaml.safe_dump(mimes, default_flow_style=False) ) 
