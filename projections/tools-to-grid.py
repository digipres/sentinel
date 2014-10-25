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

with open('digipres.github.io/_data/tools/tools.yml', 'r') as infile:
    toolgrid = yaml.load( infile ) 

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
        for cat in tool['topcats']:
            tools_matrix[ct]['topcats'][cat] += 1
        for cat in tool['subcats']:
            tools_matrix[ct]['subcats'][cat] += 1

def dictify(d):
    return {k:dictify(v) for k,v in d.items()} if \
        isinstance(d,collections.defaultdict) else d

for row in tools_matrix:
    tools_matrix[row]['topcats'] = dictify(tools_matrix[row]['topcats'])
    tools_matrix[row]['subcats'] = dictify(tools_matrix[row]['subcats'])

with open('digipres.github.io/_data/tools/tool_matrix.yml', 'w') as outfile:
    outfile.write( yaml.safe_dump(tools_matrix, default_flow_style=False) ) 
