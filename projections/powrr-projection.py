#!/usr/bin/python
#
# -*- coding: utf-8 -*-
#
# To produce a table summary of the tools in COPTR
# 

from __future__ import print_function
import os
import sys
import re
import pprint
import string
import sys
import collections

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append("pywikibot")
import pywikibot as pywikibot

pywikibot.handleArgs()
site = pywikibot.getSite()

#page = pywikibot.Page(site, u"Xena")
#print( page.exists() )

# Now go through pages by function:
cat = pywikibot.Category(site, u"Function")

# functions
functions = {}
# tools
tools = {}
# functions and tools
table = collections.defaultdict(lambda: collections.defaultdict(bool))

# For every Function category:
for sub in cat.subcategories():
    print("Processing "+sub.title())
    functions[sub.title()] = sub
    # Get subcategories?
    #sub.subcategories()
    # Get the articles in this category:
    listOfArticles = sub.articles()
    for a in listOfArticles:
        tools[a.title()] = a
        table[a.title()][sub.title()] = True

# Make a target file:
if not os.path.exists("digipres.github.io/tool-grid"):
    os.makedirs("digipres.github.io/tool-grid")
tf=open('digipres.github.io/tool-grid/index.html', 'w')

# Header so it picks up the right styling:
print("---", file=tf)
print("title: COPTR Tool Grid", file=tf)
print("layout: toolgrid", file=tf)
print("---", file=tf)

# And generate the table:
print("<table>\n<thead>\n<tr><th></th>", file=tf)
for func_name in functions:
    func = functions[func_name]
    print("<th class=\"rotate\"><div><span><a href=\"http://coptr.digipres.org/%s\">%s</></span></div></th>" % (func.title(asUrl=True), func.title().replace("Category:","")), file=tf)
print("</tr>\n</thead>\n<tbody><tr>", file=tf)
#
for tool_name in sorted(tools.keys(), key=lambda s: s.lower() ):
    tool = tools[tool_name]
    tn = tool.title()
    tu = tool.title(asUrl=True)
    if len(tn) > 25:
        tn = tn[0:25]+"..."
    print("<tr><th><a href=\"http://coptr.digipres.org/%s\">%s</a></th>" % ( tu, tn ), file=tf)
    for func in functions:
        if table[tn][func] == True:
            print("<td>X</td>", file=tf)
        else:
            print("<td>&nbsp;</td>", file=tf)
    print("</tr>", file=tf)
print("</tbody>\n</table>\n", file=tf)
#
tf.close()


