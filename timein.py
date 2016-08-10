#!/usr/bin/env python
#
# Author:  Mike Pietruszka
# Date:    Aug 10th, 2016
# Summary: Print current time for specific location.

import sys
from datetime import datetime
import pytz
import googlemaps

remote_location = sys.argv[1:]
gmaps = googlemaps.Client(key='')

geocode_result = gmaps.geocode(remote_location)
coordinates = geocode_result[0]['geometry']['location']
print str(remote_location) + " " + str(coordinates)

localtime = datetime.now()
timein = gmaps.timezone(coordinates, localtime)
print "Time zone: ", timein['timeZoneId']

fmt = "%Y-%m-%d %H:%M:%S %Z%z"

localtime = pytz.timezone('America/Chicago').localize(localtime)
print "Local time: ", localtime.strftime(fmt)
remotetime = localtime.astimezone(pytz.timezone(timein['timeZoneId']))
print "Remote time: ", remotetime.strftime(fmt)
