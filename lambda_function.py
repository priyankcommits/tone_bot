import requests as req
import json
import logging
from urlparse import parse_qs

from slackclient import SlackClient
from watson_developer_cloud import ToneAnalyzerV3


expected_token = 'TVYGUuvfyIXBUsBG4yEfoihO'
token = '<SLACK AUTH TOKEN HERE>'
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def watson_analyze(text):
    tone_analyzer = ToneAnalyzerV3(
        username='1da2a265-4790-4b5d-8b3a-fe60c599a174',
        password='oTQyUwyqxrTh',
        version='2016-05-19 '
        )

    return json.dumps(tone_analyzer.tone(text), indent=2)


def generate_payload(params, type_payload, command_type=None, tone_type=None, result_json=None):
    payload = {
            "token": expected_token,
            "team_id": params['team_id'][0],
            "team_domain": params['team_domain'][0],
            "channel_id": params['channel_id'][0],
            "channel_name": params['channel_name'][0],
            "user_id": params['user_id'][0],
            "user_name": params['user_name'][0],
            "command": params['command'][0],
            "response_url": params['response_url'][0],
            }
    if type_payload == 'invalid':
        payload['text'] = 'Invalid Command, try /tone history, /tone analyze <text>'
    elif type_payload == 'now':
        payload['text'] = 'Roger, give me some time to analyze, over & out !'
    else:
        payload['text'] = command_type + " " + tone_type + " command has been acquired"
        if tone_type == 'emotion':
            payload['attachments'] = [
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
                    ]
        elif tone_type == 'language':
            payload['attachments'] = [
                    {
                        "color": "#009B5A",
                        "pretex": "Analytical:",
                        "title": "Analytical:",
                        "text": result_json['document_tone']['tone_categories'][1]['tones'][0]['score'],
                        },
                    {
                        "color": "#FEF935",
                        "pretex": "Confident:",
                        "title": "Confident:",
                        "text": result_json['document_tone']['tone_categories'][1]['tones'][1]['score'],
                        },
                    {
                        "color": "#922890",
                        "pretex": "Tentative:",
                        "title": "Tentaive:",
                        "text": result_json['document_tone']['tone_categories'][1]['tones'][2]['score'],
                        },
                    ]
        elif tone_type == 'social':
            payload['attachments'] = [
                    {
                        "color": "#009B5A",
                        "pretex": "Openess:",
                        "title": "Openess:",
                        "text": result_json['document_tone']['tone_categories'][2]['tones'][0]['score'],
                        },
                    {
                        "color": "#FEF935",
                        "pretex": "Extraversion:",
                        "title": "Extraversion:",
                        "text": result_json['document_tone']['tone_categories'][2]['tones'][1]['score'],
                        },
                    {
                        "color": "#922890",
                        "pretex": "Agreeableness:",
                        "title": "Agreeablness:",
                        "text": result_json['document_tone']['tone_categories'][2]['tones'][2]['score'],
                        },
                    {
                        "color": "#FF9224",
                        "pretex": "Emotional Range:",
                        "title": "Emotional Range:",
                        "text": result_json['document_tone']['tone_categories'][2]['tones'][3]['score'],
                        },
                    {
                        "color": "#FF2A1A",
                        "pretex": "Conscientiousness:",
                        "title": "Conscientiousness:",
                        "text": result_json['document_tone']['tone_categories'][2]['tones'][4]['score'],
                        },
                    ]

    return payload


def generate_headers():
    return {'content-type': 'application/json'}


def build_slack_client():
    sc = SlackClient(token)

    return sc


def history(channel):
    sc = build_slack_client()
    messages = sc.server.api_call(
            "im.history",
            token=token,
            channel=str(channel),
            count='20',
            )
    print channel
    messages_retreive = json.loads(str(messages))
    messages_history = ''
    for message in messages_retreive['messages']:
        messages_history += "%s: %s\n" % (message['user'], message['text'])

    return messages_history


def lambda_handler(event, context):
    params = parse_qs(event['body'])
    token = params['token'][0]
    if token != expected_token:
        logger.error("Request token (%s) does not match expected", token)

    text = params['text'][0]
    command_text = text.split(" ")

    payload = generate_payload(params, 'now', None, None)
    response_now = req.post(
            params['response_url'][0],
            data=json.dumps(payload),
            headers=generate_headers()
            )
    result = ''
    payload_analyzed = {}
    try:
        if str(command_text[0]) == 'history':
            if str(command_text[1]) == 'emotion':
                messages_history = history(params['channel_id'][0])
                result = watson_analyze(messages_history)
            elif str(command_text[1]) == 'language':
                messages_history = history(params['channel_id'][0])
                result = watson_analyze(messages_history)
            elif str(command_text[1]) == 'social':
                messages_history = history(params['channel_id'][0])
                result = watson_analyze(messages_history)
            else:
                payload_invalid = generate_payload(params, 'invalid', None, None, None)
                response_invalid = req.post(
                        params['response_url'][0],
                        data=json.dumps(payload_invalid),
                        headers=generate_headers()
                        )
        elif str(command_text[0]) == 'analyze':
            if str(command_text[1]) == 'emotion':
                text_analyze = ' '.join(command_text[2:])
                result = watson_analyze(text_analyze)
            elif str(command_text[1]) == 'language':
                text_analyze = ' '.join(command_text[2:])
                result = watson_analyze(text_analyze)
            elif str(command_text[1]) == 'social':
                text_analyze = ' '.join(command_text[2:])
                result = watson_analyze(text_analyze)
            else:
                payload_invalid = generate_payload(params, 'invalid', None, None, None)
                response_invalid = req.post(
                        params['response_url'][0],
                        data=json.dumps(payload_invalid),
                        headers=generate_headers()
                        )
        if result:
            result_json = json.loads(str(result))
        payload_analyzed = generate_payload(
                params,
                'valid',
                command_text[0],
                command_text[1],
                result_json
                )
    except:
        payload_invalid = generate_payload(params, 'invalid', None, None, None)
        response_invalid = req.post(
                params['response_url'][0],
                data=json.dumps(payload_invalid),
                headers=generate_headers()
                )
    if payload_analyzed:
        respone_delayed = req.post(
                params['response_url'][0],
                data=json.dumps(payload_analyzed),
                headers=generate_headers()
                )

        return "Commands are: /tone [history/analyze] [emotion/language/social] <text here>"
