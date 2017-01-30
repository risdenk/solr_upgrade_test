#!/usr/bin/env python

import os
import os.path
import subprocess

configDirectory = 'configs'
configFiles = [f for f in os.listdir(configDirectory) if os.path.isfile(os.path.join(configDirectory, f))]

for configFile in sorted(configFiles):
  subprocess.call(['python', 'test.py', os.path.join(configDirectory, configFile)])

