import logging
import sys, os
import configparser
import pandas as pd
import numpy as np
import time
import json
import requests
from random import randint
from numpy import random
import concurrent.futures as cf
from requests_futures.sessions import FuturesSession

_validDefaults = ['event_interval', 'app_id', 'eventsapi', 'backfill', 'runmode', 'test_mode', 'required_fields','run_mode','max_random_events']
_required_fields = ['source.ref','title','fingerprintFields']

# Hold a group of events for cherry picking or replay
class EventGroup(object):

    def __init__(self,interval,rate,duration):
        self.events = []
        self.interval = interval
        self.rate = rate
        self.duration = duration


def validateOptions(options,validOptions):

    for option in options.options('DEFAULTS'):
        if option in validOptions:
            continue
        else:
            print("ERROR: %s is not a valid option." % option)
            exit(1)

def configParse():

    # Only allow these default options

    eg_config = configparser.ConfigParser()
    eg_config.read('../config/config.cfg')

    # Try/Except a better option?
    validateOptions(eg_config,_validDefaults)

    # return True or False based upon validation?
    return eg_config

def getScenarios(config):
    pass

def parseEvents(file,c):

    _nonprops = [c['FIELDMAP']['severity'],
                 c['FIELDMAP']['status'],
                 c['FIELDMAP']['eventClass'],
                 c['FIELDMAP']['title'],
                 c['FIELDMAP']['fingerprintFields'],
                 c['FIELDMAP']['createdAt'],
                 c['FIELDMAP']['source.ref']]

    allevents = []

    df = pd.read_excel(file).replace(np.nan, '', regex=True)
    headers = df.columns.values

    for index, row in df.iterrows():

        event = {}
        properties = {}
        required = {}

        for h in headers:
            if h in _nonprops:
                required[h] = row[h]

            # We need mc_host in both places
            if h not in _nonprops or h == 'mc_host':
                properties[h] = row[h]

        event['properties'] = properties
        event['properties']['app_id'] = c['FIELDMAP']['app_id']
        event['source'] = {"ref": required[c['FIELDMAP']['source.ref']],
                           "type": "host"}
        event['status'] = required[c['FIELDMAP']['status']]
        event['severity'] = required[c['FIELDMAP']['severity']]
        event['fingerprintFields'] = c['FIELDMAP']['fingerprintFields'].split(',')
        event['eventClass'] = required[c['FIELDMAP']['eventClass']]

        # If run_mode is random, use current time for events, otherwise use original event time
        if c['DEFAULTS']['run_mode'] == 'random':
            event['createdAt'] = int(time.time())
        elif c['DEFAULTS']['run_mode'] == 'replay':
            event['createdAt'] = required[c['FIELDMAP']['createdAt']]

        event['title'] = " ".join(required[c['FIELDMAP']['title']].splitlines())

        allevents.append(event)

    return allevents

def sendEvents(events,run_mode,max_rand):

    eventset = []
    interval_events = []

    # If run_mode is random, get a handful of events, otherwise play in the original order
    if run_mode == 'random':
        eventset = random.choice(events, randint(1, max_rand))
    elif run_mode == 'replay':
        eventset = events

    for e in eventset:
        interval_events.append(e)

    #print(json.dumps(interval_events,indent=4))

    r = requests.post(c['DEFAULTS']['eventsapi'], data=json.dumps(interval_events),
                      headers={"Content-type": "application/json"},
                      auth=(os.environ['TSI_USER'], os.environ['TSI_APIKEY']))

    print('Status Code: %s - Response: %s' % (r.status_code, r.text))

    #return True

if __name__ == "__main__":

    c = configParse()
    run_mode = c['DEFAULTS']['run_mode']
    max_rand_events = c['DEFAULTS']['max_random_events']
    scenarios = c.options('SCENARIOS')
    events = []

    logging.basicConfig(
        stream=sys.stderr, level=logging.INFO,
        format='%(relativeCreated)s %(message)s'
    )
    
    for scenario in scenarios:
        events = events + parseEvents(c['SCENARIOS'][scenario],c)

    sendEvents(events,run_mode,max_rand_events)

    # while True:
    #     e = parseEvents(c['SCENARIOS']['patrol'],c)
    #     sendEvents(e,c['DEFAULTS']['run_mode'])
    #     time.sleep(int(c['DEFAULTS']['event_interval']))


