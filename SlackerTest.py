import requests

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )
    print(response)

myToken = "your-id"
post_message(myToken, "#pycoin", "Hello Roypop")
