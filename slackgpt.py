import os
import slack
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, Response
# from time import sleep
import openai
import ngrok
import json

openai.api_key  = os.getenv('OPENAI_API_KEY')
_ = load_dotenv(find_dotenv()) # read local .env file
client = slack.WebClient(token=os.environ["SLACK_API_TOKEN"])
BOT_ID = client.api_call("auth.test")['user_id']
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter("5150de8d44a82d5a3831ae8c0122f6d0", '/slack/events', app)
# client.chat_postMessage(channel='#test', text = 'hello world')

# what is this achieving? 
tunnel = ngrok.connect(9000, authtoken_from_env=True)
print (f"Ingress established at {tunnel.url()}")

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def get_all_channel_names():
    channels = client.conversations_list()['channels']
    names = []
    for channel in channels:
        names.append(channel['name'])    
    return names

def get_all_channel_ids():
    channels = client.conversations_list()['channels']
    ids = []
    for channel in channels:
        ids.append(channel['id'])    
    return ids

def get_channel_id_from_name(name):
    channels = client.conversations_list()['channels']
    for channel in channels:
        if channel['name'] == name:
            return channel['id']
    return None

def get_channel_name_from_id(id):
    channels = client.conversations_list()['channels']
    for channel in channels:
        if channel['id'] == id:
            return channel['name']
    return None

def get_thread(channel_id, parent_message):
    response = client.conversations_replies(channel=channel_id, ts=parent_message)
    assert response['ok'] # true if the response returned successfully
    return response['messages']

def find_parent_messages(res):
    return [data for data in res if 'reply_count' in data]

def group_parents_with_thread(all_messages, channel_id):
    parents = find_parent_messages(all_messages)
    for parent in parents:
        thread_messages = get_thread(channel_id, parent['ts'])
        del thread_messages[0] # remove parent message data from api response
        filtered_thread_messages = filter_message_data(thread_messages) # remove unnecessary metadata
        parent["thread"] = filtered_thread_messages # group thread with parent
    
    return parents

def filter_message_data(all_messages):
    filtered_message_data = []
    for data in all_messages:
        new_data = {}
        for key, value in data.items():
            if (key == 'text' or key == 'thread'):
                new_data[key] = value

        filtered_message_data.append(new_data)
    return filtered_message_data


def get_historical_data(channel_id):
    # arbitrary limit
    MAX_MESSAGES=500

    # conversations.history returns the first 100 messages by default
    page = 1
    response = client.conversations_history(channel=channel_id)
    assert response['ok'] # true if the response returned successfully
    all_messages = response['messages']

    # get paginated response
    # DOCS : https://api.slack.com/docs/pagination
    while len(all_messages) + 100 <= MAX_MESSAGES and response['has_more']:
        page += 1
        response = client.conversations_history(
            channel=channel_id,
            cursor=response['response_metadata']['next_cursor']
        )
        assert response['ok'] # true if the response returned successfully
        messages = response['messages']
        all_messages = all_messages + messages

    # if we have threads we need to pull these in separately 
    grouped_messages = group_parents_with_thread(all_messages, channel_id)
    all_messages = all_messages + grouped_messages
    all_messages = filter_message_data(all_messages)

    print(
        "Fetched a total of {} messages from channel {}".format(
            len(all_messages),
            channel_id
    ))

    # write the result to a file
    with open('{}-messages.json'.format(channel_id), 'w+', encoding='utf-8') as f:
        json.dump(
            all_messages, 
            f, 
            sort_keys=True, 
            indent=4, 
            ensure_ascii=False
        )
    return 

# test
get_historical_data('C05D3KCAM8C')

# api issue...
def get_all_historical_data() :
    all_channels_ids = get_all_channel_ids()
    for channel_id in all_channels_ids:
        get_historical_data(channel_id)

@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if user_id != None and BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id, text = text)

@app.route('/AI-Helper', methods=['POST']) #By default, flask uses GET
def ai_helper():
    global message_counts
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    text = data.get('text')
    prompt = f"""
            Identify the following items from the review text: 

            The review is delimited with triple quotes. \
            Format your response using keywords \
            "Item", "company" and "sentiment". Start by detecting the sentiment\
            and based on the sentiment,\
            reply the user in a formal tone starting by acknowledging them\
            and reply based on the sentiment to make them calm
            The reply should start with the keywords stated above before responding to the customer.\
            If the information in item/company isn't present, skip it. \
            Use the information to determine your response only\
            Make your response as short as possible. '''
            Review text: '''{text}'''
            """
    response = get_completion(prompt)
    client.chat_postMessage(channel=channel_id, text = response)
    return Response(), 200

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=80, debug=True)
