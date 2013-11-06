#!/usr/bin/python
#
# -*- coding: utf-8 -*-
#
# To take the tools from:
# http://wiki.opf-labs.org/display/TR/Tools+by+function
# and post them to COPTR
 
from xmlrpclib import Server
import sys
import re
import pprint
import ConfigParser
import subprocess
import copy


def textileToMediawiki(textile):
    pandoc = subprocess.Popen("/usr/local/bin/pandoc -f textile -t mediawiki",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True)
    pandoc.stdin.write(textile)
    pandoc.stdin.close()
    return pandoc.stdout.read()

def parseTextileSummary(title, lines, r):
    for l in lines[1:]:
        parsed = re.match("^\| (.+) \| (.+)$",l)
        if parsed:
            parts = [ "", parsed.group(1), parsed.group(2) ]
            if re.match('Purpose', parts[1].strip(), re.I):
                r['Short Description'] = re.sub(r'{excerpt}','', parts[2].strip())
            elif re.match('Homepage', parts[1].strip(), re.I):
                r['URL'] = parts[2].strip().lstrip('[').rstrip(']')
            elif re.match('Source Code Repository', parts[1].strip(), re.I):
                r['Source'] = parts[2].strip().lstrip('[').rstrip(']')
            elif re.match('License', parts[1].strip(), re.I):
                r['License'] = parts[2].strip()
            elif re.match('Debian Package', parts[1].strip(), re.I):
                pass
            else:
                print "IGNORED SUMMARY DATA",title,parts
        elif l.strip() == "":
            pass
        else:
            print "WARNING for ",title," Could not parse summary data:",l



def parseTextileToolPage(title, text, r):
    for section in re.split("h\d. ", text, flags=re.S):
        lines = [line.strip() for line in section.split("\n")]
        # Match on section titles:
        if re.match("summary",lines[0], re.I):
            parseTextileSummary(title,lines,r)
        elif re.match("Description",lines[0], re.I):
            r['Description'] = '\n'.join(lines[1:])
        else:
            pass
            print "IGNORED SECTION",lines[0]

config = ConfigParser.ConfigParser()
config.readfp(open('coptr.cfg'))
 
#url = sys.argv[1]
url = "http://wiki.opf-labs.org/display/TR/Digital+Preservation+Tool+Registry"
 
terms = re.match('(?i)(^.*?)(?:/display/)(.*?)/(.*$)',url).groups();
 
server = terms[0]
space  = terms[1]
page   = terms[2].replace('+',' ')
 
s = Server(server + "/rpc/xmlrpc")
 
token = s.confluence1.login(config.get("Confluence","user"), config.get("Confluence","pw"))
 
page = s.confluence1.getPage(token, space, page )
 
#print page

#print s.confluence1.getLabelsById(token, page['id'])

fields = ["Name", "URL", "Source", "License", "Platform", "Short Description", "Description", 
    "User Experiences and Test Data", "Development Activity", "Function Categories", 
    "Content Categories",  "Logo", "Data Source"]
defaults = {}
for field in fields:
    defaults[field] = ""


print '\t'.join(fields)

for tp in s.confluence1.getChildren(token, page['id']):
    # Default fields:
    r = copy.copy(defaults)
    # Parse fields:
    #print tp['id'], tp['url'], tp['title']
    tp = s.confluence1.getPage(token, space, tp['title'])
    if tp['title'] != "Pagelyzer":# and tp['title'] == "Tika":
        title = tp['title'].encode('utf-8')
        txc = tp['content'].encode('utf-8')
        #print "LLL",txc
        r['Name'] = title
        r['Data Source'] = "OPF-TR"
        parseTextileToolPage(title, txc, r)
        #mwc = textileToMediawiki(txc).decode('utf-8')
        #out =  s.confluence1.renderContent(token, space, tp['id'], '', { 'style': 'clean'} )
        #print out.encode('utf-8')
        # Assemble the results:
        tsv = ""
        for field in fields:
            tsv += r[field]+'\t'
        print tsv[:-1]



