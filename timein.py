#!/usr/bin/env python
#
# Author:  Mike Pietruszka
# Date:    Aug 10th, 2016
# Summary: Print current time for a specific location
#

import sys
from datetime import datetime
import pytz
import googlemaps

remote_location = sys.argv[1:]
google_api_key = ''
localtz = 'America/Chicago'
time_fmt = "%Y-%m-%d %H:%M:%S %Z%z"

def find_time(remote_location):
    gmaps = googlemaps.Client(key=google_api_key)

    geocode_result = gmaps.geocode(remote_location)
    coordinates = geocode_result[0]['geometry']['location']
    print "City: " + str(remote_location).strip("[\'\']")
    print "Coordinates: " + str(coordinates)

    localtime = datetime.now()
    timein = gmaps.timezone(coordinates, localtime)
    print "Remote Time zone: ", timein['timeZoneId']

    localtime = pytz.timezone(localtz).localize(localtime)
    print "Local time: ", localtime.strftime(time_fmt)
    remotetime = localtime.astimezone(pytz.timezone(timein['timeZoneId']))
    print "Remote time: ", remotetime.strftime(time_fmt)

if __name__ == '__main__':
    remote_location = sys.argv[1:]
    find_time(remote_location)
