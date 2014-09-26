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

sys.path.append("../pywikipedia")
import wikipedia as pywikibot
import catlib

pywikibot.handleArgs()

site = pywikibot.getSite()

page = pywikibot.Page(site, u"Xena")

print( page.exists() )


# Now go through pages by function:
cat = catlib.Category(site, u"Function")

# functions
functions = collections.defaultdict(int)
# tools
tools = {}
# functions and tools
table = collections.defaultdict(lambda: collections.defaultdict(bool))

# For every Function category:
for sub in cat.subcategoriesList():
    functions[sub.title()] += 1
    # Get subcategories?
    #sub.subcategoriesList()
    # Get the articles in this category:
    listOfArticles = sub.articlesList()
    for a in listOfArticles:
        pprint.pprint(a)
        print("--> %s %s - %s " % (a.title(), a.urlname(), sub.title() ) )
        tools[a.title()] = a
        table[a.title()][sub.title()] = True

tf=open('overview_table.html', 'w')
print("---", file=tf)
print("---", file=tf)
print("""
<style>
th.rotate {
  height: 220px;
  white-space: nowrap;
}

th.rotate > div {
  transform: 
    translate(16px, 89px)
    rotate(-45deg);
  width: 30px;
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
tbody td {
  border: 1px solid #ccc;    
}
</style>

    """, file=tf)
print("<table>\n<thead>\n<tr><th></th>", file=tf)
for func in functions:
    print("<th class=\"rotate\"><div><span>%s</span></div></th>" % (func.replace("Category:","")), file=tf)
print("</tr>\n</thead>\n<tbody><tr>", file=tf)
#
for tool_name in tools:
    tool = tools[tool_name]
    tn = tool.title()
    tu = tool.urlname()
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


