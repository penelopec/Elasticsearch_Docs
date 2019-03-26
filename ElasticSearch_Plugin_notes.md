# livesync_elastic

## Implementation Notes

The following are the files that need to be modified or implemented to support ElasticSearch:

* indico-plugins/livesync/indico_livesync/__init__.py 			
    https://github.com/penelopec/indico-plugins/blob/Elasticsearch/livesync/indico_livesync/__init__.py
* indico-plugins/livesync/indico_livesync/uploader.py		Add the JSON uploader stab.
	https://github.com/penelopec/indico-plugins/blob/Elasticsearch/livesync/indico_livesync/uploader.py
* indico-plugins/livesync_elastic/indico_livesync_elastic 
    plugin to be implemented.
    It will use marshmallow for the JSON schema

Looking at the Elasticsearch and using the _bulk option, we can maintain the same structure as the existing livesync_cern (marcxml) implementation. Of course, the code will be modified appropriately for using JSON and ElasticSearch

