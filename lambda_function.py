import requests as req
import json
import logging
from urlparse import parse_qs

from slackclient import SlackClient
from watson_developer_cloud import ToneAnalyzerV3


expected_token = 'u3RVKJM8LKwa5SbKTsbfBosw'
token = "xoxp-74520690725-74510694404-75803462756-e658d76786"

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def watson_analyze(text):
    tone_analyzer = ToneAnalyzerV3(
        username='1da2a265-4790-4b5d-8b3a-fe60c599a174',
        password='oTQyUwyqxrTh',
        version='2016-05-19 '
        )

    return json.dumps(tone_analyzer.tone(text), indent=2)


def generate_payload(params, command, result_json):
    payload_analyzed = {
            "token": expected_token,
            "team_id": params['team_id'][0],
            "team_domain": params['team_domain'][0],
            "channel_id": params['channel_id'][0],
            "channel_name": params['channel_name'][0],
            "user_id": params['user_id'][0],
            "user_name": params['user_name'][0],
            "command": params['command'][0],
            "text": command + " command has been acquired",
            "attachments": [
                {
                    "color": "#009B5A",
                    "pretex": "Joy:",
                    "title": "Joy:",
                    "text": result_json['document_tone']['tone_categories'][0]['tones'][3]['score'],
                    },
                {
                    "color": "#FEF935",
                    "pretex": "Sadness:",
                    "title": "Sadness:",
                    "text": result_json['document_tone']['tone_categories'][0]['tones'][4]['score'],
                    },
                {
                    "color": "#922890",
                    "pretex": "Fear:",
                    "title": "Fear:",
                    "text": result_json['document_tone']['tone_categories'][0]['tones'][2]['score'],
                    },
                {
                    "color": "#FF9224",
                    "pretex": "Disgust:",
                    "title": "Disgust:",
                    "text": result_json['document_tone']['tone_categories'][0]['tones'][1]['score'],
                    },
                {
                    "color": "#FF2A1A",
                    "pretex": "Anger:",
                    "title": "Anger:",
                    "text": result_json['document_tone']['tone_categories'][0]['tones'][0]['score'],
                    },
                ],
            "response_url": params['response_url'][0],
            }

    return payload_analyzed


def invalid_payload(params):
    payload_invalid = {
            "token": expected_token,
            "team_id": params['team_id'][0],
            "team_domain": params['team_domain'][0],
            "channel_id": params['channel_id'][0],
            "channel_name": params['channel_name'][0],
            "user_id": params['user_id'][0],
            "user_name": params['user_name'][0],
            "command": params['command'][0],
            "text": "Roger, give me some time to analyze, over & out !",
            "response_url": params['response_url'][0],
            }

    return payload_invalid


def build_slack_client():
    sc = SlackClient(token)

    return sc


def history(channel):
    sc = build_slack_client()
    messages = sc.server.api_call(
            "im.history",
            token=token,
            channel=str(channel),
            )
    messages_retreive = json.loads(str(messages))
    print messages_retreive
    messages_history = ''
    for message in messages_retreive['messages']:
        print message
        messages_history += "%s: %s\n" % (message['user'], message['text'])

    return messages_history


def lambda_handler(event, context):
    params = parse_qs(event['body'])
    token = params['token'][0]
    if token != expected_token:
        logger.error("Request token (%s) does not match expected", token)

    text = params['text'][0]
    command_text = text.split(" ")
    headers = {'content-type': 'application/json'}
    payload_now = {
            "token": expected_token,
            "team_id": params['team_id'][0],
            "team_domain": params['team_domain'][0],
            "channel_id": params['channel_id'][0],
            "channel_name": params['channel_name'][0],
            "user_id": params['user_id'][0],
            "user_name": params['user_name'][0],
            "command": params['command'][0],
            "text": "Roger, give me some time to analyze, over & out !",
            "response_url": params['response_url'][0],
            }
    response_now = req.post(params['response_url'][0], data=json.dumps(payload_now), headers=headers)

    if str(command_text[0]) == 'history':
        messages_history = history(params['channel_id'][0])
        result = watson_analyze(messages_history)
    elif str(command_text[0]) == 'analyze':
        try:
            text_analyze = ' '.join(command_text[1:])
            result = watson_analyze(text_analyze)
        except:
            payload_invalid = invalid_payload(params)
            response_invalid = req.post(params['response_url'][0], data=json.dumps(payload_invalid, headers=headers))
    else:
        payload_invalid = invalid_payload(params)
        response_invalid = req.post(params['response_url'][0], data=json.dumps(payload_invalid, headers=headers))
    result_json = json.loads(str(result))
    payload_analyzed = generate_payload(params, command_text[0], result_json)
    respone_delayed = req.post(params['response_url'][0], data=json.dumps(payload_analyzed), headers=headers)

    return "done"
