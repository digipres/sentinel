import json
import sqlite3
import logging
import argparse
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_ext_sets(db):
    con = sqlite3.connect(db)

    cur = con.cursor()

    ext_sets = defaultdict(set)
    ext_counts = defaultdict(int)
    for row in cur.execute("SELECT registry_id, format.id, e.value FROM format, json_each(extensions) AS e ORDER BY e.value ASC"):
        ext_sets[row[0]].add(row[2].lower().strip())
        ext_counts[row[0]] += 1

    for source, ext_set in ext_sets.items():
        ext_sets[source] = list(ext_set)
        logger.info(f"Registry {source} has {ext_counts[source]} extensions, of which {len(ext_set)} are unique. Ratio: {ext_counts[source]/len(ext_set)}")
    return ext_sets, ext_counts


if __name__ == "__main__":
    # Args setup:
    parser = argparse.ArgumentParser()
    parser.add_argument('input_db')
    parser.add_argument('output_json')
    args = parser.parse_args()

    # Query and return the sets of extensions:
    ext_sets, ext_counts = generate_ext_sets(args.input_db)

    # Output the sets of extensions:
    with open(args.output_json, 'w') as f: 
        json.dump(ext_sets, f)



