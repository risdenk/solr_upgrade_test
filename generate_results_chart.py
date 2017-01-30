#!/usr/bin/env python

from __future__ import print_function
import os
import os.path

configDirectory = 'configs'
configFiles = [f for f in os.listdir(configDirectory) if os.path.isfile(os.path.join(configDirectory, f))]

versionPairs = []
startVersions = set()
upgradeVersions = set()
for configFile in configFiles:
  (v1,v2) = configFile.replace('config_', '').replace('.ini', '').split('_')
  versionPairs.append((v1, v2))
  startVersions.add(v1)
  upgradeVersions.add(v2)
  
# Generate header
header = ''
firstColumn = '| Upgraded version >> '
header += firstColumn
for v in sorted(upgradeVersions):
  header += '| ' + v + ' '
header += '|'

print(header)
secondRow = ''
secondRow += '|' + ''.join(['-' for x in range(len(firstColumn)-1)])
secondRow += ''.join(['|-------' for x in range(len(upgradeVersions))])
secondRow += '|'
print(secondRow)

lastsv = ''
for sv in sorted(startVersions):
  row = '| ' + sv + ' '
  row += ''.join([' ' for x in range(len(firstColumn)-len(row))])
  for uv in sorted(upgradeVersions):
    if (sv, uv) in versionPairs:
      if os.path.exists(os.path.join('failures', sv + '_' + uv)):
        row += '| FAIL  '
      else:
        row += '| PASS  '
    else:
      row += '|       '
  row += '|'
  lastsv = sv
  print(row)

