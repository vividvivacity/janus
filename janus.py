import os
import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from onboarding_tutorial import OnboardingTutorial 
import ssl as ssl_lib
import certifi

ssl_context = ssl_lib.create_default_context(cafile=certifi.where())

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ['JANUS_SIGNING_SECRET'], "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['JANUS_TOKEN'])

# For simplicity we'll store our app data in-memory with a dictionary.
# onboarding_tutorials_sent = {"channel": {"user_id": OnboardingTutorial}}
onboarding_tutorials_sent = {}

def start_onboarding(user_id: str, channel: str):
    # Create a new onboarding tutorial.
    onboarding_tutorial = OnboardingTutorial(channel)

    # Get the onboarding message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the onboarding message in Slack
    response = slack_web_client.chat_postMessage(**message)

    # Update the timestamp
    onboarding_tutorial.timestamp = response["ts"]

    # Store the message sent in onboarding_tutorials_sent
    if channel not in onboarding_tutorials_sent:
        onboarding_tutorials_sent[channel] = {}
    onboarding_tutorials_sent[channel][user_id] = onboarding_tutorial

# ================ Team Join Event =============== #
# When a user first joins a team, they'll be welcomed with an onboarding message.
# This is the same message sent when the user types the command "janus about".
@slack_events_adapter.on("team_join")
def onboarding_message(payload):
    '''Create and send an onboarding welcome message to new users. Save the
    time stamp of this message so we can update this message in the future.
    '''
    event = payload.get("event", {})

    # Get the id of the Slack user associated with the incoming event
    user_id = event.get("user", {}).get("id")

    # Open a DM with the new user.
    response = slack_web_client.im_open(user_id)
    channel = response["channel"]["id"]

    # Post the onboarding message.
    start_onboarding(user_id, channel)


# ============== Message Events ============= #
# This is where Janus will listen for messages. If the message is a command
# for Janus, Janus will execute that command. Otherwise, Janus determines if
# the user has posted a question and then search the workspace for it.
@slack_events_adapter.on("message")
def message(payload):
    '''Display the onboarding welcome message after receiving a message
    that contains "start".
    '''
    event = payload.get("event", {})

    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    # command for "janus about"
    if text and text.lower() == "janus about":
        return start_onboarding(user_id, channel_id)

    # command for "janus help"
    elif text and text.lower() == "janus help":
        commands = get_commands()
        response = slack_web_client.chat_postMessage(channel=channel_id, text=commands)

    # determine if a question was posted
    else:
        detect_question(event)

def get_commands():
    '''Opens a file containing commands for Janus and returns
    its contents.
    '''
    
    f = open("commands.txt", "r")
    text = ""
    for line in f:
        text += line
    return text

def detect_question(event):
    '''Detect if a user has asked a question and determines if it has
       been asked before.
       '''
    
    text = event.get("text")
    channel_id = event.get("channel")
    user_id = event.get("user")

    # For now, a statement is a question if it ends with a question mark
    if text is not None and text[len(text) - 1] == "?":
        question = text
        search_results = slack_web_client.search_messages(token=os.environ['OAUTH_TOKEN'], query=question)

        # Parse matching results
        matches = search_results['messages']['matches']
        if len(matches) != 0:
            filtered_matches = filter_results(matches)
            if len(filtered_matches) != 0:
                match_link = filtered_matches[0]['permalink']
                match_msg = "Hi <@%s>, a similar question was found for your question \"%s\":\nThis question can be found here: %s"\
                    % (user_id, question, match_link)
                has_replies_msg = check_replies(filtered_matches[0])
                response = slack_web_client.chat_postMessage(channel=channel_id, text=(match_msg + has_replies_msg), link_names=True)

def filter_results(matches):
    '''Filters matches for questions by the following:
        * The result is from a real, non-app user (in this case, not from Janus).
        * The result is in a public channel (no private channels or direct messages).
        * The result is a properly-formatted question.
    '''
    
    filtered_matches = []
    for match in matches:
        text = match['text']
        if text is not None and text[len(text) - 1] == "?":
            if match['username'].lower() != "janus":
                filtered_matches.append(match)
    return filtered_matches

def check_replies(result):
    ''' Checks if the given result has replies. Returns a string based on
    if the result has replies or not.
    '''
    
    convo_id = result['channel']['id']
    ts = result['ts']
    thread = slack_web_client.conversations_replies(token=os.environ['OAUTH_TOKEN'], channel=convo_id, ts=ts)

    # Check if the "reply_count" key exists in the response
    try:
        reply_count = thread["messages"][0]["reply_count"]
        return "\nThis question has %s replies so far, which may provide further insight for your question." % reply_count
    
    # If it doesn't, there are no replies
    except:
        return "\nThis question has no replies so far, so you may choose to follow it for further replies."

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(port=3000)

