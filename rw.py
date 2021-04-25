#!/bin/python3

import json
import requests
from bs4 import BeautifulSoup

#####################################################################
# Vars
#####################################################################
# load trains from external file
data_file = 'trains.json' #specify the full path
with open(data_file) as json_file:
    trains = json.load(json_file)
seats_type_dict = {
    'Общий': '1',
    'Сидячий': '2',
    'Плацкартный': '3',
    'Купейный': "4",
    'Мягкий': '5',
    'СВ': '6',
}
# Telegram settings
api_key = ''
chat_id = ''


#####################################################################
# Fuctions
#####################################################################
# Parse page and get all tickets info
def get_seats(url, train_number, seats_type):
    info = dict()
    seats_pull = dict()
    page = BeautifulSoup(requests.get(url).text, 'html.parser')
    train_info = page.find("div", {"data-train-number": train_number})
    tickets = train_info.findAll("div", {"class": 'sch-table__t-item has-quant'})
    for ticket in tickets:
        if seats_type != 'Любой':
            tickets_find = ticket.findAll("a", {"data-car-type": seats_type_dict[seats_type]})
            seats_type_new = seats_type
        else:
            tickets_find = ticket.findAll("a", {"class": "sch-table__t-quant js-train-modal dash"})
            if tickets_find:
                for key, value in seats_type_dict.items():
                    if tickets_find[0]['data-car-type'] == value:
                        seats_type_new = key
        if tickets_find:
            count = 0
            for ticket_find in tickets_find:
                seat_number = int(ticket_find.get_text())
                tickets_price = ticket.findAll("span", {"class": "js-price"})[count]['data-cost-byn']
                if seats_type_new in info:
                    info[seats_type_new].append({'tickets_number': seat_number, 'tickets_price': tickets_price})
                else:
                    info[seats_type_new] = [{'tickets_number': seat_number, 'tickets_price': tickets_price}]
                seats_pull.update(info)
                count += 1
    return seats_pull


# Telegram send message
def send_text(text):
    text = f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={text}'
    response = requests.get(text)
    return response.json()


# Compare if tickets info changed and write changes
def compare(train_val, seats_val):
    seats_pull = []
    for key, value in seats_val.items():
        for val in value:
            seats_pull.append(val['tickets_number'])
    seats_pull = sorted(seats_pull)
    if train_val['seats'] != seats_pull:
        # Write new json
        train_val['seats'] = seats_pull
        with open(data_file, 'w', encoding='utf8') as json_file_output:
            json.dump(trains, json_file_output, indent=4, ensure_ascii=False)
        # Write new json end
        return True
    else:
        return False


# Generate message for telegram
def message_generate(seats_dict):
    message_tickets = ''
    if seats_dict:
        for seat_type, seats_info in seats_dict.items():
            message_tickets = message_tickets + f'\nТип вагона: {seat_type}'
            for seat in seats_info:
                message_tickets = message_tickets + f"\n  -- Количество: {seat['tickets_number']}, " \
                                                    f"Цена: {seat['tickets_price']}"
        message = f'Поезд: {train["direction"]}, {train["number"]}' + message_tickets
    else:
        message = f'Поезд: {train["direction"]}, {train["number"]}\nДоступных билетов больше нет'
    return message


#####################################################################
# Run
#####################################################################
for train in trains:
    seats = get_seats(train['url'], train['number'], train['seats_type'])
    new_tickets = compare(train, seats)
    if new_tickets:
        send_text(message_generate(seats))
