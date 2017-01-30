#!/usr/bin/env python

import ConfigParser
import glob
import os
import os.path
import requests
import shutil
import subprocess
import sys
import tarfile
import time

def download_file(url):
  local_filename = url.split('/')[-1]

  if not os.path.isfile(local_filename):
    print('Downloading from ' + url)
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
      for chunk in r.iter_content(chunk_size=1024): 
        if chunk: # filter out keep-alive new chunks
          f.write(chunk)

  return local_filename

def extract_file(filename):
  print('Extracting ' + filename)
  with tarfile.open(filename) as tar:
    tar.extractall()

def mkdir(path):
  try:
    if os.path.isdir(path):
      shutil.rmtree(path)
    os.makedirs(path)
  except OSError:
    if not os.path.isdir(path):
        raise

def check_cluster(numNodes, collection, count=0):
  # Wait for recovery up to a minute (5 sec * 12)
  if count == 12:
    raise Exception('Failed cluster check')

  for x in range(numNodes):
    hostUrl = 'http://localhost:' + str(8983+x) + '/solr'
   
    r = requests.get(hostUrl + '/admin/collections', params={'action':'CLUSTERSTATUS', 'wt':'json'})
    clusterStatus = r.json()

    if len(clusterStatus['cluster']['live_nodes']) != numNodes:
      time.sleep(5)
      check_cluster(numNodes, collection, count+1)

    collectionInfo = clusterStatus['cluster']['collections'][collection]
    for shard in collectionInfo['shards'].itervalues():
      if shard['state'] != 'active':
        time.sleep(5)
        check_cluster(numNodes, collection, count+1)
      for replica in shard['replicas'].itervalues():
        if replica['state'] != 'active':
          time.sleep(5)
          check_cluster(numNodes, collection, count+1)

    r2 = requests.get(hostUrl + '/' + collection + '/select', params={'q':'*:*','wt':'json'})
    queryResults = r2.json()

    # if queryResults['response']['numFound']:

if __name__ == '__main__':
  failed = False

  config = ConfigParser.RawConfigParser()
  config.read(sys.argv[1])

  zookeeperUrl = config.get('zookeeper', 'url')
  zookeeperFile = download_file(zookeeperUrl)
  extract_file(zookeeperFile)

  solrUrl1 = config.get('solr', 'v1url')
  solrFile1 = download_file(solrUrl1)
  extract_file(solrFile1)

  solrUrl2 = config.get('solr', 'v2url')
  solrFile2 = download_file(solrUrl2)
  extract_file(solrFile2)

  numNodes = config.getint('solr', 'numNodes')
  collection = config.get('solr', 'collection')
  v1 = config.get('solr', 'v1')
  v2 = config.get('solr', 'v2')
  solrV1Path = os.path.join('solr-' + v1, 'bin')
  solrV2Path = os.path.join('solr-' + v2, 'bin')

  try:
    print('Starting ZK')
    mkdir('zookeeper_data')
    shutil.copyfile('zoo.cfg', os.path.join(glob.glob(r'zookeeper-*/')[0], 'conf', 'zoo.cfg'))
    subprocess.check_call([os.path.join(glob.glob(r'zookeeper-*/')[0], 'bin', 'zkServer.sh'), 'start'])

    print('Starting Solr')
    shutil.copyfile('log4j.properties', os.path.join('solr-' + v1, 'server', 'resources', 'log4j.properties'))
    shutil.copyfile('log4j.properties', os.path.join('solr-' + v2, 'server', 'resources', 'log4j.properties'))
    for x in range(numNodes):
      nodeName = 'node' + str(x)
      print('Starting ' + nodeName)
      mkdir(nodeName)
      shutil.copyfile('solr.xml', os.path.join(nodeName, 'solr.xml'))
      subprocess.check_call([os.path.join(solrV1Path, 'solr'), 'start', '-c', '-z', 'localhost', '-p', str(8983+x), '-s', nodeName, '-Dsolr.log.dir=' + os.path.abspath(nodeName)])

    print('Creating collection: ' + collection)
    subprocess.check_call([os.path.join(solrV1Path, 'solr'), 'create', '-c', collection, '-d', 'data_driven_schema_configs', '-s', str(numNodes), '-rf', str(numNodes)])

    print('Indexing documents to collection:' + collection)
    subprocess.check_call([os.path.join('solr-' + v1, 'bin', 'post'), '-c', collection, './solr-' + v1 + '/example/exampledocs/'])

    print('Checking cluster')
    check_cluster(numNodes, collection)

    print('Upgrading cluster')
    for x in range(numNodes):
      nodeName = 'node' + str(x)
      port = str(8983+x)
      print('Upgrading ' + nodeName)

      print('Stopping ' + nodeName + ' version ' + v1)
      subprocess.check_call([os.path.join(solrV1Path, 'solr'), 'stop', '-p', port])
    
      print('Starting ' + nodeName + ' version ' + v2)
      subprocess.check_call([os.path.join(solrV2Path, 'solr'), 'start', '-c', '-z', 'localhost', '-p', port, '-s', nodeName, '-Dsolr.log.dir=' + os.path.abspath(nodeName)])

      print('Checking cluster after ' + str(x+1) + ' of ' + str(numNodes) + ' nodes upgraded')
      check_cluster(numNodes, collection)
  except Exception as e:
    failed = True


  print('Shutting down Solr')
  subprocess.call([os.path.join(solrV1Path, 'solr'), 'stop', '-all'])
  subprocess.call([os.path.join(solrV2Path, 'solr'), 'stop', '-all'])

  print('Shutting down Zookeeper')
  subprocess.call([os.path.join(glob.glob(r'zookeeper-*/')[0], 'bin', 'zkServer.sh'), 'stop'])

  if failed:
    print('Archiving test data')
    failure_directory = 'failures'
    if not os.path.exists(failure_directory):
      os.makedirs(failure_directory)

    archive_directory = os.path.join(failure_directory, v1 + '_' + v2)
    if os.path.exists(archive_directory):
      print('Removing previous failure test data: ' + archive_directory)
      shutil.rmtree(archive_directory)
    os.makedirs(archive_directory)

    for x in range(numNodes):
      nodeName = 'node' + str(x)
      shutil.move(nodeName, archive_directory)

    print('Archived test data to ' + os.path.abspath(archive_directory))

    print('Cluster upgrade failed!')
    sys.exit(1)
  else:
    print('Cleaning up')
    for x in range(numNodes):
      nodeName = 'node' + str(x)
      shutil.rmtree(nodeName)
    shutil.rmtree('zookeeper_data')
    os.remove('zookeeper.out')

    print('Cluster upgrade successful!')
    sys.exit(0)

