#!/usr/bin/python
#
# -*- coding: utf-8 -*-
#
#  given a url show the confluence page src
#  Zohar Melamed - 08/02/20005
#
#

# http://wiki.opf-labs.org/display/TR/Tools+by+function
 
from xmlrpclib import Server
import sys
import re
import pprint
import ConfigParser


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
        print tp['content'].encode('utf-8')
        #out =  s.confluence1.renderContent(token, space, tp['id'], '', { 'style': 'clean'} )
        #print out.encode('utf-8')

