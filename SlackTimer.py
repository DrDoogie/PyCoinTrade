import requests
import schedule
import time

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )
    print(response)


myToken = "your-id"

def printhello():
    print("Autotrade Server is allive!")
    post_message(myToken, "#pycoin", "SlackTimer Test Hello")
    return 0


schedule.every(1).minutes.do(printhello)  # 1분마다 실행

while True:
    schedule.run_pending()
    time.sleep(1)