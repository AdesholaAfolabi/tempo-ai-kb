import os
import slack
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, Response
import openai
from knowledge_base import doc_chat, load_embeddings

openai.api_key  = os.getenv('OPENAI_API_KEY')
files = ["Ultimate_introduction_white_paper.pdf", "Planner-complete-guide-to-resource-planning.pdf"]
persist_directory = "docs/chroma/"

_ = load_dotenv(find_dotenv()) # read local .env file
client = slack.WebClient(token=os.environ["SLACK_API_TOKEN"])
BOT_ID = client.api_call("auth.test")['user_id']
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ["SIGNING_SECRET"], '/slack/events', app)

# Create a vector database for document embeddings
vectordb = load_embeddings(persist_directory, files)
        
@app.route('/ai-helper', methods=['POST'])
def ai_helper():
    '''
    
    '''
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    question = data.get('text')
    response = doc_chat(vectordb,
                          model_name="gpt-3.5-turbo",
                          question=str(question)
                          )
    client.chat_postMessage(channel=channel_id, text = response)
    return Response(), 200

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=80, debug=True)