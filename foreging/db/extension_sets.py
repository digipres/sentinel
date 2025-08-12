import json
import sqlite3
from collections import defaultdict
con = sqlite3.connect("registries.db")

cur = con.cursor()

ext_sets = defaultdict(set)
for row in cur.execute("SELECT registry_id, format.id, e.value FROM format, json_each(extensions) AS e ORDER BY e.value ASC"):
    ext_sets[row[0]].add(row[2])

for source, ext_set in ext_sets.items():
    ext_sets[source] = list(ext_set)

print(json.dumps(ext_sets))