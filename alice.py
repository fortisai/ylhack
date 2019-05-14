from flask import Flask, request
import logging
import json
import random
from requests import post

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    if req['session']['new']:
        res['response']['text'] = 'Привет! Введи <login> <password>'

    args = req["original_utterance"].strip()
    login, passw = args
    print(login, passw)
    response = post('http://localhost:5000/api/auth',
                    data={"login": login, "password": passw}).json()
    print(response)
    if response["token"]:
        res["text"] = "Успешно"
    else:
        res["text"] = response["error"]
    return


if __name__ == '__main__':
    app.run()
