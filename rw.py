#!/bin/python3

import json
import requests
from bs4 import BeautifulSoup

# vars
with open('directions.json') as json_file:
    directions = json.load(json_file)
api_key = ''
chat_id = ''


# Parse page
def get_seats(url, train):
    seats_pull = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    get_train = (soup.find("div", {"data-train-number": train}))
    get_seats_pull = (get_train.findAll("a", {"class": "sch-table__t-quant js-train-modal dash"}))
    for seat in get_seats_pull:
        seat = int(seat.find('span').get_text())
        seats_pull.append(seat)
    return seats_pull


# Telegram
def send_text(message):
    text = f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message}'
    response = requests.get(text)
    return response.json()


for direction in directions:
    seats = get_seats(direction['url'], direction['train'])
    if direction['seats'] != seats:
        # Write new json
        direction['seats'] = seats
        with open('directions.json', 'w', encoding='utf8') as json_file:
            json.dump(directions, json_file, indent=4, ensure_ascii=False)
        # Write new json end
        if not seats:
            seats = 0
        send_text(f'{direction["message"]}: {seats}')
