from slack_sdk import WebClient
from decouple import config

client = WebClient(token=config('TOKEN'))

blocks = [{
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": "Test *with bold text* and _italicized text_."
    }

}]

response = client.chat_postMessage(channel='#개발자', blocks=blocks)