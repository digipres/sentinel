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
        parsed = re.match("^\| (.+) \| (.+)\|$",l)
        if parsed:
            parts = [ "", parsed.group(1), parsed.group(2) ]
            if re.match('Purpose', parts[1].strip(), re.I):
                r['Short Description'] = re.sub(r'{excerpt}','', parts[2].strip())
            elif re.match('Homepage', parts[1].strip(), re.I):
                r['URL'] = parts[2].strip().lstrip('[').rstrip(']')
            elif re.match('Source Code Repository', parts[1].strip(), re.I):
                r['Source'] = parts[2].strip().lstrip('[').rstrip(']')
            elif re.match('License', parts[1].strip(), re.I):
                r['License'] = re.sub('\\\\', '', parts[2]).strip()
            elif re.match('Debian Package', parts[1].strip(), re.I):
                pass
            else:
                r['additional'] += nl + str(parts) + nl
#                print "IGNORED SUMMARY DATA",title,parts
        elif l.strip() == "":
            pass
        else:
            r['additional'] += nl + l + nl
#            print "WARNING for ",title," Could not parse summary data:",l



def parseTextileToolPage(title, text, r):
    for section in re.split("h2. ", text, flags=re.S):
        lines = [line.strip() for line in section.split("\n")]
        r['additional'] = ""
        # Match on section titles:
        if re.match("summary",lines[0], re.I):
            parseTextileSummary(title,lines,r)
        elif re.match("Description",lines[0], re.I):
            r['Description'] = nl.join(lines[1:])
        elif re.match("User Experiences",lines[0], re.I):
            r['User Experiences and Test Data'] = nl.join(lines[1:])
        elif re.match("^News Feed.*",lines[0], re.I):
            r['Development Activity'] += nl.join(lines[1:])
        else:
            content = ' '.join(lines[1:]).strip()
            if content != "":
                r['additional'] += "h2. "+lines[0]+ nl + nl.join(lines[1:])
    r['Description'] += r['additional']
    # Regex the contents for RSS links.
    r['Development Activity'] = re.sub(r'{rss:max=(.)\|url=([^}]+)}',r'<rss max=\1>\2</rss>',r['Development Activity'],flags=re.S)



def parseLabels(title, labels, r):
    fc = set()
    cc = set()
    for label in labels:
        n = label['name']
        if n == 'convert' or n == 'conversion' or n == 'migration':
            fc.add("Conversion")
        elif n == 'validation':
            fc.add('Metadata Processing/Validation')
        elif n == 'identification':
            fc.add('File Format Identification')
        elif n == 'characterisation' or n == 'characterization' or n == 'extraction' or n == 'characterise' or n == 'metadata':
            fc.add('Metadata Extraction')
        elif n == 'fixity':
            fc.add('Fixity')
        elif n == 'preservation' or n == 'too' or n == 'tool' or n == 'untagged':
            pass
        else:
            cc.add(n)
    for label in fc:
        r['Function Categories'] += label+","
    r['Function Categories'] = r['Function Categories'].rstrip(',')
    for label in cc:
        r['Content Categories'] += label+","
    r['Content Categories'] = r['Content Categories'].rstrip(',')


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

# define mid-data newline
nl = '\n'
snl = chr(13)

# Set up columns
fields = ["Name", "URL", "Source", "License", "Platform", "Short Description", "Description", 
    "User Experiences and Test Data", "Development Activity", "Function Categories", 
    "Content Categories",  "Logo", "Data Source"]
defaults = {}
for field in fields:
    defaults[field] = ""

# Output headers
sys.stdout.write((",".join(fields))[:-1])
sys.stdout.write("\r\n")

for tp in s.confluence1.getChildren(token, page['id']):
    # Default fields:
    r = copy.copy(defaults)
    # Parse fields:
    #print tp['id'], tp['url'], tp['title']
    tp = s.confluence1.getPage(token, space, tp['title'])
    labels = s.confluence1.getLabelsById(token, tp['id'])

    if tp['title'] != "Pagelyzer":# and tp['title'] == "Tika":
        title = tp['title'].encode('utf-8')
        txc = tp['content'].encode('utf-8')
        #print "LLL",txc
        r['Name'] = title
        r['Data Source'] = "OPF-TR"
        parseTextileToolPage(title, txc, r)
        parseLabels(title,labels,r)
        #mwc = textileToMediawiki(txc).decode('utf-8')
        #out =  s.confluence1.renderContent(token, space, tp['id'], '', { 'style': 'clean'} )
        #print out.encode('utf-8')
        # And convert to MediaWiki:
        r['Description'] = re.sub( nl, snl, textileToMediawiki(r['Description']) )
        r['Development Activity'] = re.sub( nl, snl, textileToMediawiki(r['Development Activity']) )
        r['Development Activity'] = re.sub( r'<br \/>', snl, r['Development Activity'] )
        # Assemble the results:
        tsv = ""
        for field in fields:
            tsv += "\""+str(re.sub("\"","'",r[field])).strip()+"\""+','
        sys.stdout.write(tsv[:-1])
        sys.stdout.write("\r\n")



