#!/usr/bin/env python

import ConfigParser
import os
import os.path
import requests

versions = {'master':'7.0.0', '6.x':'6.5.0'}

for name,version in versions.iteritems():
  buildBaseUrl = 'https://builds.apache.org/job/Solr-Artifacts-' + name  + '/lastSuccessfulBuild'
  print(buildBaseUrl)
  r = requests.get(buildBaseUrl + '/buildNumber')
  nightlyBuildNumber = r.text
  print(nightlyBuildNumber)
  zkUrl = 'http://mirrors.koehn.com/apache/zookeeper/zookeeper-3.4.9/zookeeper-3.4.9.tar.gz'
  v1 = '6.4.1'
  v2 = version + '-' + nightlyBuildNumber

  config = ConfigParser.RawConfigParser()
  config.add_section('zookeeper')
  config.set('zookeeper', 'url', zkUrl)
  config.add_section('solr')
  config.set('solr', 'numNodes', '2')
  config.set('solr', 'collection', 'testupgrade')
  config.set('solr', 'v1', v1)
  v1url = 'http://mirrors.koehn.com/apache/lucene/solr/' + v1 + '/solr-' + v1 + '.tgz'
  config.set('solr', 'v1url', v1url)
  config.set('solr', 'v2', v2)
  v2url = buildBaseUrl + '/artifact/solr/package/solr-' + v2 + '.tgz'
  config.set('solr', 'v2url', v2url)

  directory = 'configs'
  config_path = os.path.join(directory,'config_' + v1 + '_' + v2 + '_' + name + '.ini')
  with open(config_path, 'wb') as configfile:
    config.write(configfile)

