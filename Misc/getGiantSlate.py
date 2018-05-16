# Grabs slate info from StageApp (Giant)

import json
import urllib2

url = 'http://10.0.1.25:8080/currentSlate'
slate = '<none>'

try:
    slate = json.load(urllib2.urlopen(url, timeout=1))['name']
except:
    print 'Error connecting to StageApp'

print 'Current slate: ' + slate