# Solr Cloud Rolling Upgrade Test
## Overview
Based on the work from https://github.com/viveknarang/solr-upgrade-tests

### Steps
Following is the summary of the steps that the program follows to test the rolling upgrade

1. Download ZK and Solr
2. Start ZK
3. Start Solr nodes
4. Create a Test collection
5. Insert a set of documents
6. Stop each node one by one, upgrade a single node, and start node again
7. Check if the cluster status has the upgraded node
8. Check if all the documents are available from the collection
9. If 7 and 8 pass, the program repeats 6-8 for each node
10. If all nodes are updated successfully, identifies the test as successful. Upon failure of either 6 or 7, the program declares the test as failed.
12. Shutdown the nodes and cleanup

## Requirements
* Require URL for a Solr release >=5.0.0
* Python Requests (http://docs.python-requests.org/en/master/)

## Install Prerequirements
`pip install -r requirements.txt`

## Generate Configs
This parses the Solr DOAP file (https://lucene.apache.org/solr/doap.rdf) and generates configs for every version >= 5.0.0 to every later version.

`python create_configs.py`

## Run Test
`python test.py configs/CONFIG_FILE`

## TODO
* Add documentation to work off of a tgz instead of a url
* Auto generate compatibility chart between versions

