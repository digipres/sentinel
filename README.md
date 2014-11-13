Sentinel
========

TBC

To Do:

* Link to PRONOM itself.
* http://en.wikipedia.org/wiki/Alphabetical_list_of_filename_extensions_%28M%E2%80%93R%29
* http://www.webarchive.org.uk/aadda-discovery/formats?f[0]=content_type_ext:%22.bmp%22
* https://twitter.com/benfinoradin/status/532212803630039041

COPTR Bot
---------
Talking to the wiki requires the 'pywikipedia' codebase which is installed here as a git submodule. See the pywikibot instructions for details: https://www.mediawiki.org/wiki/Manual:Pywikibot

Automated build and update process
----------------------------------

    travis env set COPTR_PW XXXXXX
    travis env set GIT_NAME "Andrew Jackson"
    travis env set GIT_EMAIL anj@anjackson.net
    travis env set GH_TOKEN XXXXXX

See also password.enc etc.
