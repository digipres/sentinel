#!/usr/bin/python
#
# -*- coding: utf-8 -*-
#
# To take the tools from:
# http://wiki.opf-labs.org/display/TR/Tools+by+function
# and post them to COPTR
 
import sys
import re
import pprint
from xlrd import open_workbook
import string
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append("pywikipedia")
import wikipedia as pywikibot

pywikibot.handleArgs()

def put(title, contents):
    mysite = pywikibot.getSite() 
    page = pywikibot.Page(mysite, title)
    # Show the title of the page we're working on.
    # Highlight the title in purple.
    pywikibot.output(u">>> \03{lightpurple}%s\03{default} <<<"
        % page.title())
    # Check if it exists:
#    if page.exists():
#        print "EXISTS!"
#        return
#    else:
#        print "DOES NOT EXIST!"
    # Post it:
    comment = "Import from spreadsheet via script."
    try:
        page.put( contents, comment = comment, minorEdit = False )
    except pywikibot.LockedPage:
        pywikibot.output(u"Page %s is locked; skipping." % title)
    except pywikibot.EditConflict:
        pywikibot.output(u'Skipping %s because of edit conflict' % title)
    except pywikibot.SpamfilterError, error:
        pywikibot.output(
            u'Cannot change %s because of spam blacklist entry %s'
            % (title, error.url))

def builtCategories(funcat, concat):
    cats = ""
    totcats = funcat+","+concat
    for cat in totcats.split(","):
        cat = cat.strip()
        if cat != "":
            cats += "[[Category:%s]]\n" % cat
    return cats


# Load page template file:
mwtpl = string.Template( open('mw-tool-template.txt').read() )

# Open up the input file:
wb = open_workbook('COPTR data version 28.xlsx') #, encoding_override="cp1252")
for s in wb.sheets():
    #print 'Sheet:',s.name
    if not "Ready" == s.name:
        continue
    # Get titles:
    ti = {}
    for col in range(s.ncols):
        colt = s.cell(0,col-1).value
        ti[colt] = col-1
        #print colt
    # Go through rows:
    for row in range(s.nrows):
        values = []
        for col in range(s.ncols):
            values.append(str(s.cell(row,col).value))
        title = s.cell(row,0).value
        if title != "Pagelyzer" and title != "Name":
            for colt in ti.keys():
                print colt, " -- ", s.cell(row, ti[colt]).value
            desc = s.cell(row, ti["Description"]).value
            desc = re.sub("<br \/>","\n\n", desc)
            desc = desc.lstrip()
            logo = ""
            #if s.cell(row, ti["Logo"]) != None:
            #    logo = s.cell(row, ti["Logo"]).value
            page = mwtpl.substitute(
                purpose = s.cell(row, ti["Short Description"]).value.strip(),
                image = logo,
                homepage = s.cell(row, ti["URL"]).value.strip(),
                license = s.cell(row, ti["License"]).value.strip(),
                platforms = s.cell(row, ti["Platform"]).value.strip(),
                categories = builtCategories(s.cell(row, ti["Function Categories"]).value, s.cell(row, ti["Content Categories"]).value),
                description = desc,
                experiences = s.cell(row, ti["User Experiences and Test Data"]).value.lstrip(),
                ohloh = s.cell(row, ti["OhlohID"]).value.strip(),
                activity = s.cell(row, ti["Development Activity"]).value.lstrip()
                )
            print page
            put(title, page)

