#!/usr/bin/env python

import ConfigParser
import os
import os.path
import requests

nightlyBaseUrl = 'https://builds.apache.org/job/Solr-Artifacts-master/lastSuccessfulBuild/'

r = requests.get(nightlyBaseUrl + '/buildNumber')
nightlyBuildNumber = r.text

zkUrl = 'http://mirrors.koehn.com/apache/zookeeper/zookeeper-3.4.9/zookeeper-3.4.9.tar.gz'
v1 = '6.4.0'
v2 = '7.0.0-' + nightlyBuildNumber

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
v2url = 'https://builds.apache.org/job/Solr-Artifacts-master/lastSuccessfulBuild/artifact/solr/package/solr-' + v2 + '.tgz'
config.set('solr', 'v2url', v2url)

directory = 'configs'
config_path = os.path.join(directory,'config_' + v1 + '_' + v2 + '_nightly.ini')
with open(config_path, 'wb') as configfile:
  config.write(configfile)

