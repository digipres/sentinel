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

def RecentChangesPageGenerator(start=None, end=None, reverse=False,
                               namespaces=None, pagelist=None,
                               changetype=None, showMinor=None,
                               showBot=None, showAnon=None,
                               showRedirects=None, showPatrolled=None,
                               topOnly=False, step=None, total=None,
                               user=None, excludeuser=None, site=None):

    """
    Generate pages that are in the recent changes list.

    @param start: Timestamp to start listing from
    @type start: pywikibot.Timestamp
    @param end: Timestamp to end listing at
    @type end: pywikibot.Timestamp
    @param reverse: if True, start with oldest changes (default: newest)
    @type reverse: bool
    @param pagelist: iterate changes to pages in this list only
    @param pagelist: list of Pages
    @param changetype: only iterate changes of this type ("edit" for
        edits to existing pages, "new" for new pages, "log" for log
        entries)
    @type changetype: basestring
    @param showMinor: if True, only list minor edits; if False, only list
        non-minor edits; if None, list all
    @type showMinor: bool or None
    @param showBot: if True, only list bot edits; if False, only list
        non-bot edits; if None, list all
    @type showBot: bool or None
    @param showAnon: if True, only list anon edits; if False, only list
        non-anon edits; if None, list all
    @type showAnon: bool or None
    @param showRedirects: if True, only list edits to redirect pages; if
        False, only list edits to non-redirect pages; if None, list all
    @type showRedirects: bool or None
    @param showPatrolled: if True, only list patrolled edits; if False,
        only list non-patrolled edits; if None, list all
    @type showPatrolled: bool or None
    @param topOnly: if True, only list changes that are the latest revision
        (default False)
    @type topOnly: bool
    @param user: if not None, only list edits by this user or users
    @type user: basestring|list
    @param excludeuser: if not None, exclude edits by this user or users
    @type excludeuser: basestring|list

    """

    if site is None:
        site = pywikibot.Site()
    for item in site.recentchanges(start=start, end=end, reverse=reverse,
                                   namespaces=namespaces, pagelist=pagelist,
                                   changetype=changetype, showMinor=showMinor,
                                   showBot=showBot, showAnon=showAnon,
                                   showRedirects=showRedirects,
                                   showPatrolled=showPatrolled,
                                   topOnly=topOnly, step=step, total=total,
                                   user=user, excludeuser=excludeuser):
        yield(item)

def month_diff(d1, d2): 
    """Return the number of months between d1 and d2, 
    such that d2 + month_diff(d1, d2) == d1
    """
    diff = (12 * d1.year + d1.month) - (12 * d2.year + d2.month)
    return diff

# Process the arguments:
pywikibot.handleArgs()


# Function to process user contribs:
def user_contribs(fam,site):
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
        outfile.write( yaml.safe_dump(users, default_flow_style=False) ) 


def recent_changes(fam,site):
    # Load known recent changes
    cf = 'digipres.github.io/_data/'+fam+'-changes.yml'
    if os.path.isfile(cf):
        stream = open(cf, 'r')
        changes = yaml.load(stream)
        stream.close()
    else:
        changes = {}

    if changes == None:
        changes = {}

    # Set up date range:
    #start_date = datetime.date(2013,10,1) 
    start_date = datetime.date.today() - datetime.timedelta(days=31)
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
        for item in RecentChangesPageGenerator(reverse=True, namespaces=[0],
               start=qstart, end=qend):
            change = pywikibot.Page(pywikibot.Link(item["title"], site))
            print(change)
            if( change.exists() ):
                timestamp = item["timestamp"]
                title = item["title"]
                print(timestamp,title)
                if not (timestamp in changes):
                    changes[timestamp] = {}
                changes[timestamp]['title'] = title
                changes[timestamp]['type'] = item["type"]
    

    # Write out as a data file to feed into templates:
    with open(cf, 'w') as outfile:
        outfile.write( yaml.safe_dump(changes, default_flow_style=False) ) 


# Process a site:
def contribs(fam):
    # Set up the site
    pywikibot.config.family = fam
    site = pywikibot.Site()

    # Make output folders if needed:
    if not os.path.exists("digipres.github.io/contribs"):
        os.makedirs("digipres.github.io/contribs")  

    if not os.path.exists("digipres.github.io/_data"):
        os.makedirs("digipres.github.io/_data") 

    user_contribs(fam,site)

    recent_changes(fam,site)

# Process contributions from COPTR:
contribs("coptr")
# Process contributions from FileFormats:
contribs("ff")


