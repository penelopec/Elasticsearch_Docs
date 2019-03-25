# livesync_elastic

## Implementation Notes

The following are the files that need to be modified or implemented to support ElasticSearch:

* indico-plugins/livesync/indico_livesync/__init__.py 			
    https://github.com/penelopec/indico-plugins/blob/Elasticsearch/livesync/indico_livesync/__init__.py
* indico-plugins/livesync/indico_livesync/uploader.py		Add the JSON uploader stab.
	https://github.com/penelopec/indico-plugins/blob/Elasticsearch/livesync/indico_livesync/uploader.py
* indico-plugins/livesync/indico_livesync/jsonGen.py	New file (not yet on the repository, I am working on this.) 
	it combines the files and converts the xml creation into appropriate JSON for Elasticsearch: 
	* indico/indico/legacy/common/xmlGEN.py
	* indico/indico/legacy/common/output.py
* indico-plugins/livesync_elastic/indico_livesync_elastic 
    plugin to be implemented.

Looking at the Elasticsearch and using the _bulk option, we can maintain the same structure as the existing livesync_cern (marcxml) implementation. Of course, the code will be modified appropriately for using JSON and ElasticSearch

