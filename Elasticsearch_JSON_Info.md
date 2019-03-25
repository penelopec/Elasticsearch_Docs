# Indico JSON Schema

The implementation could use either the Elasticsearch package or the REST API.  The code is almost the same in both cases for \_bulk operations.
The Elasticsearch document fields are those described in the mappings document.

## JSON Schema

livesync_elastic will utilize the Elasticsearch's _bulk API to populate and update the Elasticsearch data.
https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html

Use the following as an example for loading metadata:
https://github.com/elastic/elasticsearch-py/blob/master/example/load.py

### Elasticsearch Terminology

* __Cluster__: collection of servers to contain the data identified by a unique name
* __Node__: A single cluster server
* __Index__: A collection of documents of different types, e.g. indico
* __Type__: A “category” in an index, e.g. events, contributions, subcontributions, attachments, notes
* __Document__: A basic unit of information that can be indexed. Consists of fields with key/value pairs. Documents are expressed in JSON
* __Mapping__: The fields of a document, like a database schema
* __Shards__: An index can be divided into multiple pieces called shards. A shard is an independent index
* __Replicas__: A replica is a copy of a shard


### Elasticsearch operations

* __index__: create or update a document
* __create__: create a document, if it exists an error is generated
* __update__: update a document
* __delete__: delete a document


### POST _bulk

The REST API endpoint is /_bulk, and it expects the following newline delimited JSON (NDJSON) structure:
> action_and_meta_data\n
> optional_source\n
> action_and_meta_data\n
> optional_source\n
> ....
> action_and_meta_data\n
> optional_source\n

An example of the expected data would look like:
> { "index" : { "_index" : "test", "_type" : "_doc", "_id" : "1" } }\n
> { "field1" : "value1" }\n
> { "delete" : { "_index" : "test", "_type" : "_doc", "_id" : "2" } }\n
> { "create" : { "_index" : "test", "_type" : "_doc", "_id" : "3" } }\n
> { "field1" : "value3" }\n
> { "update" : {"_id" : "1", "_type" : "_doc", "_index" : "test"} }\n
> { "doc" : {"field2" : "value2"} }\n

So, a curl call looks like:
> curl -X POST "localhost:9200/_bulk" -H 'Content-Type: application/json' -d'
> { "index" : { "_index" : "test", "_type" : "_doc", "_id" : "1" } }
> { "field1" : "value1" }
> { "delete" : { "_index" : "test", "_type" : "_doc", "_id" : "2" } }
> { "create" : { "_index" : "test", "_type" : "_doc", "_id" : "3" } }
> { "field1" : "value3" }
> { "update" : {"_id" : "1", "_type" : "_doc", "_index" : "test"} }
> { "doc" : {"field2" : "value2"} }
> '

