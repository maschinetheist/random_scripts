#!/usr/bin/env python
#
# Author:  Mike Pietruszka
# Date:    Nov 13th, 2016
# Summary: Monitor subreddits for latest threads and alert on latest submissions
#

from __future__ import print_function
import boto3
import praw
from datetime import datetime, timedelta
from dateutil import tz

sns = boto3.client('sns')
number = '+18888888'

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/Chicago')

r = praw.Reddit(user_agent='amzn_sns_thread_post')
subreddits = ['cars']
new_threads = {}

''' for every sub, find latest threads that were posted within past hour. '''
for sub in subreddits:
    threads = r.get_subreddit(sub).get_new(limit=10)
    for thread in threads:
        # get current UTC time and UTC time post the post
        post_time = datetime.utcfromtimestamp(thread.created_utc).strftime('%Y-%m-%d %H:%M:%S.%f')
        post_time = datetime.strptime(post_time, '%Y-%m-%d %H:%M:%S.%f')
        last_hour = datetime.utcnow() - timedelta(hours=1)
        if post_time > last_hour:
            # convert UTC time to local time
            post_time = post_time.replace(tzinfo=from_zone)
            central = post_time.astimezone(to_zone)
            #print(str(thread) + " " + str(central))
            thread_name = thread.fullname.encode('ascii', 'ignore')
            new_threads[thread_name] = {}
            new_threads[thread_name]['id'] = str(thread)
            new_threads[thread_name]['date'] = str(central)

#for thread in sorted(new_threads.items()):
#    print(thread)
sns.publish(PhoneNumber=number, Message=str(new_threads))
