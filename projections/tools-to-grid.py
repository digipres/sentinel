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
import datetime
from yaml.representer import Representer
from sets import Set

with open('digipres.github.io/_data/tools/tools.yml', 'r') as infile:
    toolgrid = yaml.load( infile ) 

# Count the number of tools:
stats = {}
stats['num_tools'] = len(toolgrid)
subcats = Set()
topcats = Set()
ctypes = Set()

# Loop through the tool lists and count the matrix:
tools_matrix = {}
for tool in toolgrid:
    for ct in tool['content_types']:
        if not ct in tools_matrix:
            tools_matrix[ct] = {}
            tools_matrix[ct]['count'] = 0
            tools_matrix[ct]['topcats'] = collections.defaultdict(int)
            tools_matrix[ct]['subcats'] = collections.defaultdict(int)
        tools_matrix[ct]['count'] += 1
        ctypes.add(ct)
        for cat in tool['topcats']:
            tools_matrix[ct]['topcats'][cat] += 1
            topcats.add(cat)
        for cat in tool['subcats']:
            tools_matrix[ct]['subcats'][cat] += 1
            subcats.add(cat)

# Count the types etc:
stats['num_topcats'] = len(topcats)
stats['num_subcats'] = len(subcats)
stats['num_ctypes'] = len(ctypes)

def dictify(d):
    return {k:dictify(v) for k,v in d.items()} if \
        isinstance(d,collections.defaultdict) else d

for row in tools_matrix:
    tools_matrix[row]['topcats'] = dictify(tools_matrix[row]['topcats'])
    tools_matrix[row]['subcats'] = dictify(tools_matrix[row]['subcats'])

with open('digipres.github.io/_data/tools/tool_matrix.yml', 'w') as outfile:
    outfile.write( yaml.safe_dump(tools_matrix, default_flow_style=False) ) 

# Load last summary
sf = 'digipres.github.io/_data/tools/summary.yml'
if os.path.isfile(sf):
    stream = open(sf, 'r')
    summary = yaml.load(stream)
    stream.close()
else:
    summary = []
# Reset if it went wrong
if summary == None:
    summary = []

# Check if anything has changed:
if len(summary) == 0:
    new_data = True
else:
    new_data = False
    for key in stats:
        if stats[key] != summary[-1]['stats'][key]:
            new_data = True
            break

# Updated the summary stats:
if new_data: 
    i = datetime.datetime.now()
    summary.append( {
        'timestamp' : i.isoformat(),
        'stats' : stats 
    } )
    # And write out:
    with open(sf, 'w') as outfile:
        outfile.write( yaml.safe_dump(summary, default_flow_style=False) ) 



