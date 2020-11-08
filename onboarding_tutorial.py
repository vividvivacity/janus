class OnboardingTutorial:
    """Constructs the onboarding message."""

    WELCOME_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Greetings, mortal. I am Janus, the all-knowing observer bot. :eye-in-speech-bubble:\n\n"
                "To get started, type \"janus help\" for a list of my commands.\n\n"
                "*Learn more about me below:*"
            ),
        },
    }

    MISSION_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "*Background:*\n"
                "With so many places having moved to online environments, Slack has become a great way "
                "for peers and colleagues to communicate, especially for asking questions and receiving "
                "help. Unfortunately, not everyone is always online to help other users. This can be "
                "especially troublesome for questions that get asked over and over, but receive no answers "
                "for a while.\n\n"
                "*Mission:*\n"
                "Janus aims to cut down on wait time for answers by determining if the question has been "
                "asked before in the workspace, see if there are replies to the question, then deliver that "
                "information to the user straight away. Through these means, Janus ensures that those who "
                "have questions which have already been answered before but do not know due to lack of time "
                "and communication will be helped."
            )
        }
    }

    DEV_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "*Progress in Development:*\n"
                "Currently, basic functionalities of what Janus aims to do have been implemented, though "
                "the methods of implementation plan to be improved on in the future. Right now, Janus "
                "utilizes the searching feature of the Slack Web API to find matching questions and a "
                "naive method of determining whether a message is a question. In the future, Janus plans "
                "to:\n\n"
                "• determine matches between questions through semantic similarity "
                "(meaning of a sentence rather than the structure of a sentence).\n"
                "• improve the method of choosing the best matching question. One idea is to score "
                "questions, choose a group of matching questions if they pass a certain threshold, "
                "and choose the question with the most replies.\n"
                "• implement a feedback system to keep track of how useful Janus currently is to users "
                "and make improvements to the bot."
            )
        }
    }

    INFO_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "*Why am I named Janus?*\n"
                "Janus is the name of the Roman god of beginnings, ends, doorways, and duality. Janus "
                "has two faces: one that looks into the past, and one that looks into the future. In "
                "this context, Janus the bot looks into past questions and uses them to help answer "
                "similar ones in the future. Also the name Janus is cool.\n\n"
                "You can read more about Janus the Roman god *<https://en.wikipedia.org/wiki/Janus|"
                "here>*."
            )
        }
    }

    DIVIDER_BLOCK = {"type": "divider"}

    def __init__(self, channel):
        self.channel = channel
        self.username = "Janus"
        self.icon_emoji = ":robot_face:"
        self.timestamp = ""
        self.reaction_task_completed = False
        self.pin_task_completed = False

    def get_message_payload(self):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                self.WELCOME_BLOCK,
                self.DIVIDER_BLOCK,
                self.MISSION_BLOCK,
                self.DIVIDER_BLOCK,
                self.DEV_BLOCK,
                self.DIVIDER_BLOCK,
                self.INFO_BLOCK
            ],
        }