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


sys.path.append("pywikipedia")
import wikipedia as pywikibot

def put(title, contents):
    mysite = pywikibot.getSite() 
    page = pywikibot.Page(mysite, title)
    # Show the title of the page we're working on.
    # Highlight the title in purple.
    pywikibot.output(u">>> \03{lightpurple}%s\03{default} <<<"
        % page.title())
    # Check if it exists:
    if page.exists():
        print "EXISTS!"
        return
    else:
        print "DOES NOT EXIST!"
    # Post it:
    comment = "Trial import from script."
    try:
        page.put(contents, comment = comment, minorEdit = False)
    except pywikibot.LockedPage:
        pywikibot.output(u"Page %s is locked; skipping." % title)
    except pywikibot.EditConflict:
        pywikibot.output(u'Skipping %s because of edit conflict' % title)
    except pywikibot.SpamfilterError, error:
        pywikibot.output(
            u'Cannot change %s because of spam blacklist entry %s'
            % (title, error.url))    

def textileToMediawiki(textile):
    pandoc = subprocess.Popen("/usr/local/bin/pandoc -f textile -t mediawiki",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True)
    pandoc.stdin.write(textile)
    pandoc.stdin.close()
    return pandoc.stdout.read()

def parseTextileToolPage(text):
    for section in re.split("h\d. ", text, flags=re.S):
        print "SECTION"
        lines = [line.strip() for line in section.split("\n")]
        for l in lines:
            print "l%s" % {l}

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

#pprint.pprint(
for tp in s.confluence1.getChildren(token, page['id']):
    print tp['id'], tp['url'], tp['title']
    tp = s.confluence1.getPage(token, space, tp['title'])
    if tp['title'] != "Pagelyzer" and tp['title'] == "Tika":
        title = tp['title'].encode('utf-8')
        txc = tp['content'].encode('utf-8')
        parseTextileToolPage(txc)
        mwc = textileToMediawiki(txc).decode('utf-8')
        put(title, mwc)
        #out =  s.confluence1.renderContent(token, space, tp['id'], '', { 'style': 'clean'} )
        #print out.encode('utf-8')

