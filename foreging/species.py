# Use the idea of a Species Accumulation Curve to understand the scale of the format challenge.
import csv
import yaml
import json
import logging
import argparse
from collections import defaultdict

logging.basicConfig(level=logging.WARNING, format='%(asctime)s: %(levelname)s - %(name)s - %(message)s')

logger = logging.getLogger(__name__)


def load_extensions():
    with open('digipres.github.io/_data/formats/extensions.yml') as f:
        extensions = yaml.safe_load(f)
    return extensions

def reindex_by_registry(extensions):
    exts = extensions['extensions']
    ext_sets = defaultdict(set)
    for ext in exts:
        for id in exts[ext]['identifiers']:
            ext_sets[id['regId']].add(ext.lower())
    return ext_sets

def compute_sac():
    ext_sets = reindex_by_registry(load_extensions())

    all_extensions = set()
    sample_total = 0

    # Go though the dict of sets, sorting them so largest sets go first (note each item is the k,v array):
    # Doing this seems to make the curve fitting more robust/consistent.
    print("source,num_exts,num_uniq_exts,percent_uniq_exts,total_exts,total_uniq_exts,added_uniq_exts")
    for set_key, ext_set in sorted(ext_sets.items(), key=lambda item: len(item[1]), reverse=True):
        sample_total += len(ext_set)
        current_total = len(all_extensions)
        all_extensions |= ext_set
        total_added = len(all_extensions) - current_total
        # Calculate the unique part, by making a copy of the set and removing all other sets from it:
        unique_ext = ext_set.copy()
        for other_set in ext_sets:
            if other_set != set_key:
                unique_ext -= ext_sets[other_set]
        # Share & Enjoy:
        set_size = len(ext_set)
        unique_size = len(unique_ext)
        print(f"{set_key},{set_size},{unique_size},{100.0*unique_size/set_size:.3f},{sample_total},{len(all_extensions)},{total_added}")


def _print_comparison(set_key, candidate_set, collection_set, collection_counts, collection_total):
    remainder = collection_set - candidate_set
    common = collection_set.intersection(candidate_set)
    remainder_count = 0
    for ext in remainder:
        remainder_count += collection_counts[ext]
    print(f"{set_key} {len(common)} {len(remainder)} {remainder_count} {collection_total}")# {json.dumps(list(remainder))}")

def compare_csv(csv_file):
    collection_set = set()
    collection_counts = {}
    collection_total = 0
    with open(csv_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ext = row['extension'].lower().strip()
            # Drop extensions with spaces in:
            if " " in ext:
                logger.warning(f"Dropping extension with space in: '{ext}'")
                continue
            # Drop extensions that are just numbers:
            if ext.isnumeric():
                logger.warning(f"Dropping extension that appears to be just a number: '{ext}'")
                continue
            # Convert to standard lower-case glob format
            ext = f"*.{ext}"
            logger.debug(f"Found extension {ext} with file_count {row['file_count']}")
            collection_set.add(ext)
            collection_counts[ext] = int(row['file_count'])
            collection_total += int(row['file_count'])
    
    ext_sets = reindex_by_registry(load_extensions())
    all_extensions = set()
    for set_key, ext_set in sorted(ext_sets.items(), key=lambda item: len(item[1]), reverse=True):
        all_extensions |= ext_set
        _print_comparison(set_key, ext_set, collection_set, collection_counts, collection_total)
    _print_comparison("_ALL_", all_extensions, collection_set, collection_counts, collection_total)

def write_extensions(output_json):
    ext_sets = reindex_by_registry(load_extensions())
    with open(output_json,"w") as f:
        json.dump(ext_sets, f, default=list)


if __name__ == "__main__":
    common_args = argparse.ArgumentParser(prog="species", add_help=False)
    common_args.add_argument('-v', '--verbose',  action='count', default=0, help='Logging level; add more -v for more logging.')

    parser = argparse.ArgumentParser(prog="species", add_help=True)
    subparsers =  parser.add_subparsers(dest="action", help='action')

    parser_sac = subparsers.add_parser('curve', parents=[common_args], help="Load the extensions and compute the Species Accumulation Curve.")

    parser_cmp = subparsers.add_parser('compare', parents=[common_args], help="Compare extensions from a CSV file with the registry contents.")
    parser_cmp.add_argument('csv_file', type=str, help='CSV file to load')

    parser_exts = subparsers.add_parser('extensions', parents=[common_args], help="Write the extensions data out as a JSON file.")
    parser_exts.add_argument('json_file', type=str, help='JSON file to write')

    args = parser.parse_args()

    # Set up verbose logging:
    if 'verbose' in args:
        if args.verbose == 1:
            logging.getLogger().setLevel(logging.INFO)
        elif args.verbose >= 2:
            logging.getLogger().setLevel(logging.DEBUG)

    if args.action == 'curve':
        compute_sac()
    elif args.action == 'compare':
        compare_csv(args.csv_file)
    elif args.action == "extensions":
        write_extensions(args.json_file)