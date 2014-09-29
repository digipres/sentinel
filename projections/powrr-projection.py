#!/usr/bin/python
#
# -*- coding: utf-8 -*-
#
# To produce a table summary of the tools in COPTR
# 
# Based on e.g. https://git.wikimedia.org/blob/pywikibot%2Fcompat.git/HEAD/category.py
# 

from __future__ import print_function
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
    #sub.subcategoriesList()
    # Get the articles in this category:
    listOfArticles = sub.articles()
    for a in listOfArticles:
        tools[a.title()] = a
        table[a.title()][sub.title()] = True

tf=open('overview_table.html', 'w')
print("---", file=tf)
print("---", file=tf)
print("""
<style>
body {
  font-family: sans-serif;
}
th {
    font-weight: normal;
}
th.rotate {
  height: 220px;
  white-space: nowrap;
}
th.rotate > div {
  transform: 
    translate(20px, 87px)
    rotate(-45deg);
  width: 35px;
}
th.rotate > div > span {
  border-bottom: 1px solid #ccc;
  padding: 5px 10px;
}
table {
 border-collapse: collapse;
}
tbody th {
  white-space: nowrap;    
}
tbody td, tbody th {
  border: 1px solid #ccc;    
}
</style>
    """, file=tf)
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


