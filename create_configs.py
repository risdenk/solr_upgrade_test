#!/usr/bin/env python

import ConfigParser
from itertools import izip
import os.path
import requests
from xml.etree import ElementTree

url = 'https://lucene.apache.org/solr/doap.rdf'
r = requests.get(url)

versions = []

tree = ElementTree.fromstring(r.content)
for version in tree.findall('.//{http://usefulinc.com/ns/doap#}Version'):
  revision = version.find('{http://usefulinc.com/ns/doap#}revision').text
  if revision >= '5.0.0':
    versions.append(revision)

version_pairs = []
for vA in sorted(versions):
  for vB in sorted(versions):
    if vB > vA:
      version_pairs.append((vA, vB))

directory = 'configs'
if not os.path.exists(directory):
  os.makedirs(directory)

zkUrl = 'https://archive.apache.org/dist/zookeeper/zookeeper-3.4.10/zookeeper-3.4.10.tar.gz'

for (v1,v2) in version_pairs:
  config = ConfigParser.RawConfigParser()
  config.add_section('zookeeper')
  config.set('zookeeper', 'url', zkUrl)
  config.add_section('solr')
  config.set('solr', 'numNodes', '2')
  config.set('solr', 'collection', 'testupgrade')
  config.set('solr', 'v1', v1)
  v1url = 'https://archive.apache.org/dist/lucene/solr/' + v1 + '/solr-' + v1 + '.tgz'
  config.set('solr', 'v1url', v1url)
  config.set('solr', 'v2', v2)
  v2url = 'https://archive.apache.org/dist/lucene/solr/' + v2 + '/solr-' + v2 + '.tgz'
  config.set('solr', 'v2url', v2url)

  config_path = os.path.join(directory,'config_' + v1 + '_' + v2 + '.ini')
  with open(config_path, 'wb') as configfile:
    config.write(configfile)

