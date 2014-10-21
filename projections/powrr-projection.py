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
import yaml

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append("pywikibot")
import pywikibot as pywikibot

pywikibot.handleArgs()
site = pywikibot.getSite()

#page = pywikibot.Page(site, u"Xena")
#print( page.exists() )

# Now go through pages by function:
cat = pywikibot.Category(site, u"Tool Grid")

# functions
functions = {}
# tree
func_tree = []
# tools
tools = {}
# functions and tools
table = collections.defaultdict(lambda: collections.defaultdict(bool))

# For every Function category:
for sub in cat.subcategories():
    print("Processing "+sub.title())
    func = {}
    func['title'] = sub.title().replace("Category:","")
    func['title_url'] = sub.title(asUrl=True)
    func['subcats'] = []
    # Get subcategories?
    for sub2 in sub.subcategories():
        func['subcats'].append({
                'title': sub2.title().replace("Category:",""),
                'title_url': sub2.title(asUrl=True)
            })
        functions[sub2.title()] = {}
        functions[sub2.title()]['cat'] = sub2
        functions[sub2.title()]['parent'] = sub
    # And append it:
    func_tree.append(func)

# Then, at get the articles under the second-level categories.
toolgrid = []
for func_name in functions:
    func = functions[func_name]['cat']
    parent = functions[func_name]['parent']
    # Get the articles in this category:
    listOfArticles = func.articles()
    for a in listOfArticles:
        print("For "+parent.title()+" :: "+func_name+", found article "+a.title())
        tinfo = { 
            "title": a.title(),
            "title_url": a.title(asUrl=True),
            "topcat": parent.title(),
            "topcat_url": parent.title(asUrl=True),
            "subcat": func.title(),
            "subcat_url": func.title(asUrl=True)
        }
        toolgrid.append(tinfo)
        tools[a.title()] = a
        table[a.title()][func.title()] = True

with open('digipres.github.io/_data/tools/function_tree.yml', 'w') as outfile:
    outfile.write( yaml.safe_dump(func_tree, default_flow_style=False) ) 

with open('digipres.github.io/_data/tools/tool_grid.yml', 'w') as outfile:
    outfile.write( yaml.safe_dump(toolgrid, default_flow_style=False) ) 

sys.exit(0)


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
    func = functions[func_name]['cat']
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


