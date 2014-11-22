Registries
==========

This repository holds versioned copies of the data from a number of registries:

* Apache Tika
* [Library of Congress FFD](http://www.digitalpreservation.gov/formats/fdd/fdd_xml_info.shtml)
* PRONOM
* TRiD

and combines this information to provide [an overview of all the formats known to these systems](http://www.digipres.org/formats/).

How it works
------------

There are scripts to download and refresh the data from each source, which can be run together as:

    $ cd registries
    $ ./refresh-sources.sh

This 'master' script updates the data from each source, and checks it into this repository.

Then, another aggregator script can be used to combine and compare the data from each source, and put the data a copy of the www.digipres.org website source.

    $ python aggregates.py

This populates the _data/formats directory of the digipres.github.io sub-repository:

    $ cd ../digipres.github.io/_data/formats

TODO automatic adding and committing of the updated information.

When this content is pushed to GitHub, the source templates in digipres.github.io use the data files in _data to build up a static website that exposes this information to the web (using Jekyll via GitHub Pages).

TODO Add master Travis CI script to run this automatically.

TODO
----

* Build stats-log, so we can track the stats over time.
* Build a change-log, so when new formats turn up, we know about them?
* Use sorted(d, key=lambda i: int(d[i])) form to sort PRONOM IDs numerically
* Note Parsers for Tika, note Container for DROID.
* Refer back to sources and mirrors of sig. files.
    * Add line numbers please - needed for Tika at least and maybe PRONOM.
    * https://github.com/anjackson/foreg/blob/master/registries/tika/tika-mimetypes.xml#L4263
    * http://www.digitalpreservation.gov/formats/fdd/fdd000393.shtml
    * http://apps.nationalarchives.gov.uk/pronom/fmt/278
* Add more fields:
    * hasParser? (.eml example and Tika)
    * Relationships (particularly sub/supertype).
    * Apple UTIs (and cross-ref).
    * 'Deprecated' status.
    * Length of article/description.
    * Number of external links.
    * Some kind of overall quality metric for format descriptions.
    * Canonical MIME type.
    * ???
* Improve cross-referencing:
    * Expose cross-referencing by file extension, etc.
    * Expose agreement and disagreement between tools.
* Collect stats for tools:
    * Count and list of entries with no file extension/magic/mime-type/etc.
* Add more validation:
    * Validate Apple Uniform Type Identifiers
    * Check relationship references are same (e.g that both ends exist)
* More sources:
	* fileformats.archiveteam.org
	* Wikipedia
	* Use Fido as a way of getting Tika-compatible sigs.
	* Fine Free File/libmagic DB? (not really well-structured enough)
	* [Freebase](https://www.freebase.com/query?autorun=1&q=[{%22id%22:null,%22name%22:null,%22type%22:%22/computer/file_format%22}])
	* UDFR (not sure if there's enough new data to be worth it given the point-in-time PRONOM import issue).
	* NIST SWRL?

* Related
    * https://github.com/srnsw/Preservation-Pathway & http://www.records.nsw.gov.au/digitalarchives/pathways/