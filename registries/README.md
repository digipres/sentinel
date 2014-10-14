Registries
==========

This holds copies of the data from:

* PRONOM
* Library of Congress [FFD](http://www.digitalpreservation.gov/formats/fdd/fdd_xml_info.shtml)
* TRiD
* Apache Tika

There are scripts to download and refresh the data from each source, and another aggregator script that attempts to combine and compare the data from each source.


TODO
----
* Add more fields:
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
	* Fine Free File/libmagic DB.
	* [Freebase](https://www.freebase.com/query?autorun=1&q=[{%22id%22:null,%22name%22:null,%22type%22:%22/computer/file_format%22}])
	* UDFR (not sure if there's enough new data to be worth it given the point-in-time PRONOM import issue).
	* NIST SWRL?
