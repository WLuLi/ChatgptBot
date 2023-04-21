import json
import requests
from flask import Flask, request
import openai

cqhttp_url = "http://localhost:8700"
qq_number = ""
openai.api_key = ""
messages = []

server = Flask(__name__)

# Communicate with ChatGPT
def chat(message):
    try:
        messages.clear()
        messages.append({"role": "user", "content": message})
    
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = messages
        )
        reply = response["choices"][0]["message"]["content"]
        print(reply)
    except Exception as error:
        print(error)
        reply = "I'm sorry, I don't understand."
    return reply
    
# get Qq Message
@server.route("/", methods=["POST"])
def get_message():
    # private message
    if request.get_json().get('message_type') == 'private':
        uid = request.get_json().get('sender').get('user_id')
        message = request.get_json().get('raw_message')
        sender = request.get_json().get('sender')
        print("private received: " + message)
        return_text = chat(message)
        send_private_message(uid, return_text)
    
    # group message
    if request.get_json().get('message_type') == 'group':
        gid = request.get_json().get('group_id')
        uid = request.get_json().get('sender').get('user_id')
        message = request.get_json().get('raw_message')
        if str("[CQ:at,qq=%s]"%qq_number) in message:
            sender = request.get_json().get('sender')
            print("group received: " + message)
            return_text = chat(message)
            return_text = str('[CQ:at,qq=%s]\n'%uid) + str(return_text)
            send_group_message(gid, return_text)
    return "ok"

def send_group_message(gid, message):
    try:
        res = requests.post(url=cqhttp_url + "/send_group_msg",
                            params={'group_id': int(gid), 'message': message}).json()
        if res["status"] == "ok":
            print("success")
        else:
            print("fault: " + str(res['wording']))
    except:
        print("failed")

def send_private_message(uid, message):
    try:
        res = requests.post(url=cqhttp_url + "/send_private_msg",
                            params={'user_id': int(uid), 'message': message}).json()
        if res["status"] == "ok":
            print("success")
        else:
            print(res)
            print("fault: " + str(res['wording']))
    except:
        print("failed")

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=7777)