# livesync_json

## Implementation Notes

There are two plugins that are required for the search to work:
- livesync_json
- search_json
(where _json_ can be replaced by any appropriate name for the plugins)

The _livesync_json_ implements the methods required by _livesync_ and _search_json_ the methods required bt _search_
The _livesync_json_ can be use as its staring point the livesync_cern and the _search_json_ can use the search_invenio

indico and the indico-plugins are using among other packages the following: 
* sqlalchemy (https://www.sqlalchemy.org/), 
* marshamallow (https://marshmallow.readthedocs.io/en/3.0/), 
* flask (http://flask.pocoo.org/), 
* jinja (http://jinja.pocoo.org/)

The plugins that will interact with the ElasticSearch will utilize the _CERN Search_ (http://cernsearchdocs.web.cern.ch/cernsearchdocs/example/)

Adrian's marshmallow schema to be used in ES: https://gist.github.com/ThiefMaster/bd78f52909ec963023ce2e368874dac6

**CERN Search usefull links**
* The architecture of the CERN Search is described at: http://cernsearch-admin-docs.web.cern.ch/cernsearch-admin-docs/architecture/ 
* The ElasticSearch mappings are: https://github.com/inveniosoftware-contrib/cern-search/blob/master/documentation/mappings/indico.md
* ElasticSearch JSON files: https://github.com/inveniosoftware-contrib/cern-search/tree/master/cern_search_rest_api/modules/cernsearch/mappings/indico/v6/cernsearch-indico

