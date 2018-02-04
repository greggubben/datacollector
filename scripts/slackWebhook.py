#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Post a message to slack via WebHook
#
import requests
import json
import slackConf

def post2slack (message, icon="", channel="", name=""):
  webhook_url = 'https://hooks.slack.com/services/' + slackConf.access_token
  slack_data = {}
  slack_data['text'] = message
  if (icon != ""):
    slack_data['icon_emoji'] = ":{0}:".format(icon)
  if (channel != ""):
    slack_data['channel'] = "#{0}".format(channel)
  if (name != ""):
    slack_data['username'] = name
  r = requests.post(webhook_url, data=json.dumps(slack_data),
      headers={'Content-Type': 'application/json'})
  #print(r.status_code, r.reason)
  #print(r.text[:300] + '...')
  if r.status_code != 200:
    raise ValueError(
      'Request to slack returned an error %s, the response is:\n%s'
      % (r.status_code, r.text)
    )

def debug2slack (message, channel="debug"):
  post2slack(message, "eyes", channel, "Debug")

