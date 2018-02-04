#!/usr/bin/python

import slackWebhook as slackwh

slackwh.post2slack( "test message only")
slackwh.post2slack( "test message with icon", "monkey_face")
slackwh.post2slack( "test message with icon and channel", "monkey_face", "random")
slackwh.post2slack( "test message with icon and channel", "monkey_face", "random", "Testing Program")
