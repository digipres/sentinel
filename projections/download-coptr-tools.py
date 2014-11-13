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
from yaml.representer import Representer

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append("pywikibot")
import pywikibot as pywikibot

pywikibot.handleArgs()
site = pywikibot.Site()

#page = pywikibot.Page(site, u"Xena")
#print( page.exists() )

# functions
functions = {}
# tree
func_tree = []
# content types
types = {}
# tools
tools = {}
# functions and tools
table = collections.defaultdict(lambda: collections.defaultdict(bool))

# Ensure YAML knows how to handle defaultdicts of ints - as dicts:
yaml.add_representer(collections.defaultdict, Representer.represent_dict)

# Now go through pages by function:
cat = pywikibot.Category(site, u"Tool Grid")
# For every Function category:
for sub in cat.subcategories():
    if sub.isRedirectPage():
        print("Skipping redirect page "+sub.title())
    else:
        print("Processing "+sub.title())
        func = {}
        func['title'] = sub.title().replace("Category:","")
        func['title_url'] = sub.title(asUrl=True)
        func['subcats'] = []
        # Get metadata:
        for t in sub.templatesWithParams():
            if t[0].title() == "Template:Infobox stage":
                for param in t[1]:
                    if "=" in param:
                        (key, val) = param.split("=",1)
                        func[key] = val.strip()
        # Get subcategories?
        for sub2 in sub.subcategories():
            if not sub2.isRedirectPage():
                subcat = {
                    'title': sub2.title().replace("Category:",""),
                    'title_url': sub2.title(asUrl=True)
                }
                for t in sub2.templatesWithParams():
                    if t[0].title() == "Template:Infobox function":
                        for param in t[1]:
                            if "=" in param:
                                (key, val) = param.split("=",1)
                                subcat[key] = val.strip()
                func['subcats'].append(subcat)
                functions[sub2.title()] = {}
                functions[sub2.title()]['cat'] = sub2
                functions[sub2.title()]['parent'] = sub
        # And append it:
        func_tree.append(func)

# Now go through pages by function:
cat = pywikibot.Category(site, u"Content Type")
# For every type category:
for sub in cat.subcategories():
    if sub.isRedirectPage():
        print("Skipping redirect page "+sub.title())
    else:
        print("Processing "+sub.title())
        ctype = {}
        ctype['title'] = sub.title().replace("Category:","")
        ctype['title_url'] = sub.title(asUrl=True)
        ctype['tool_count'] = 0
        types[ctype['title_url']] = ctype
# Add faux-type:
types['Category:~Not Content Type Specific~'] = {}
types['Category:~Not Content Type Specific~']['title'] = '~Not Content Type Specific~'
types['Category:~Not Content Type Specific~']['title_url'] = ''
types['Category:~Not Content Type Specific~']['tool_count'] = 0

# Then, at get the articles under the second-level categories.
toolgrid = {}
for func_name in functions:
    func = functions[func_name]['cat']
    parent = functions[func_name]['parent']
    # Get the articles in this category:
    listOfArticles = func.articles()
    for a in listOfArticles:
        print("For "+parent.title()+" :: "+func_name+", found article "+a.title())
        if not a.title() in toolgrid:
            toolgrid[a.title()] = {}
            toolgrid[a.title()]['title_full'] = a.title()
            tn = a.title()
            if len(tn) > 25:
                tn = tn[0:25]+"..."
            toolgrid[a.title()]['title'] = tn
            toolgrid[a.title()]['title_url'] = a.title(asUrl=True)
            toolgrid[a.title()]['topcats'] = []
            toolgrid[a.title()]['subcats'] = []
            toolgrid[a.title()]['content_types'] = []
        toolgrid[a.title()]['topcats'].append( parent.title().replace("Category:","") )
        toolgrid[a.title()]['subcats'].append( func.title().replace("Category:","") )
        #
        for t in a.templatesWithParams():
            if t[0].title() == "Template:Infobox tool":
                for param in t[1]:
                    if "=" in param:
                        (key, val) = param.split("=",1)
                        toolgrid[a.title()][key] = val.strip()
            elif t[0].title() == "Template:Format":
                if not 'formats' in toolgrid[a.title()]:
                    toolgrid[a.title()]['formats'] = []
                toolgrid[a.title()]['formats'].append(t[1])
        #
        tools[a.title()] = a
        table[a.title()][func.title()] = True

with open('digipres.github.io/_data/tools/content_types.yml', 'w') as outfile:
    outfile.write( yaml.safe_dump(types, default_flow_style=False) ) 

with open('digipres.github.io/_data/tools/function_tree.yml', 'w') as outfile:
    outfile.write( yaml.safe_dump(func_tree, default_flow_style=False) ) 

# Go through the tool pages to get all the categories at that level:
print("Processing tool pages to get all categories...")
for tool_name in sorted(tools.keys(), key=lambda s: s.lower() ):
    a = tools[tool_name]
    # Get all categories to see what content types this item applies to
    ctype_count = 0
    for cat in a.categories():
        title = cat.title().replace("Category:","")
        title_url = cat.title(asUrl=True)
        # Counters for content-type:
        if title_url in types:
            types[title_url]['tool_count'] += 1
            if not title in toolgrid[a.title()]['content_types']:
                toolgrid[a.title()]['content_types'].append(title)
            ctype_count += 1
        # Counters for functions:?
    if ctype_count == 0:
        types['Category:~Not Content Type Specific~']['tool_count'] += 1
        title = types['Category:~Not Content Type Specific~']['title']
        if not title in toolgrid[a.title()]['content_types']:
            toolgrid[a.title()]['content_types'].append(title)

with open('digipres.github.io/_data/tools/tools.yml', 'w') as outfile:
    outfile.write( yaml.safe_dump(toolgrid.values(), default_flow_style=False) ) 





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


