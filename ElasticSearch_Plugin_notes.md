# livesync_elastic

## Implementation Notes

There are two plugins that are required for the search to work:
- livesync_json
- search_json
(where _json_ can be replaced by any appropriate name for the plugins)

The _livesync_json_ implements the methods required by _livesync_ and _search_json_ the methods required bt _search_
The _livesync_json_ can be use as its staring point the livesync_cern and the _search_json_ can use the search_invenio
