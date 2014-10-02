#!/usr/bin/python
#
# -*- coding: utf-8 -*-
#
# To produce a table summary of contributions to MediaWiki installations,
# 
# * COPTR, i.e. since c. November 2013
# * File Formats
# * DPC?
# 

from __future__ import print_function
import os
import sys
import re
import pprint
import string
import sys
import collections
import datetime
import yaml

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append("pywikibot")
import pywikibot as pywikibot
import pywikibot.pagegenerators as pg


def month_diff(d1, d2): 
    """Return the number of months between d1 and d2, 
    such that d2 + month_diff(d1, d2) == d1
    """
    diff = (12 * d1.year + d1.month) - (12 * d2.year + d2.month)
    return diff

# Process the arguments:
pywikibot.handleArgs()

# Function to process a site:
def contribs(fam):
    # Set up the site
    pywikibot.config.family = fam
    site = pywikibot.Site() 

    # Make output folders if needed:
    if not os.path.exists("digipres.github.io/contribs"):
        os.makedirs("digipres.github.io/contribs")  

    if not os.path.exists("digipres.github.io/_data"):
        os.makedirs("digipres.github.io/_data") 

    # Collect user contribs table:
    users = []
    # Loop over users
    for user in site.allusers(total=500):
        if user['editcount'] > 0 and ("bot" not in user['groups']) and user['name'] != "Andy Tester":
          users.append(user)
    # Sort by edit count:
    users = sorted(users, key=lambda k: k['editcount'], reverse=True) 
    # Write out as a data file to feed into templates:
    with open('digipres.github.io/_data/'+fam+'-users.yml', 'w') as outfile:
        outfile.write( yaml.safe_dump(users, default_flow_style=True) ) 
    

    # Set up date range:
    start_date = datetime.date(2013,10,1)
    end_date = datetime.date.today()    

    # Loop
    total_months = month_diff(start_date,end_date)
    year = start_date.year
    month = start_date.month
    d = datetime.date(year,month,1)
    while d <= end_date:
        qstart = d.strftime("%Y-%m-%dT00:00:00Z")
        month += 1
        if month > 12:
            month = 1
            year += 1
        d = datetime.date(year,month,1)
        qend = d.strftime("%Y-%m-%dT00:00:00Z")
        print(qstart,qend)
        # Look for changes:
        for change in pg.RecentChangesPageGenerator(reverse=True, namespaces=[0],
               start=qstart, end=qend):
            print(change)
            if( change.exists()):
                print(change.editTime())    
    

    # Make a target file:
    tf=open('digipres.github.io/contribs/index.html', 'w')  

    # And close:
    tf.close()

# Process contributions from COPTR:
contribs("coptr")
# Process contributions from FileFormats:
contribs("ff")


