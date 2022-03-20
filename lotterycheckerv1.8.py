import requests, bs4, re
import logging
import csv
import datetime
from twilio.rest import Client
import os
import psycopg2
from config import config

def insert_ticket(ticket):
    """ insert a new ticket into the tickets table """
    sql = """INSERT INTO public.tickets("Bonus", "Date", "Numbers", "GPD", "Message")
             VALUES(%s,%s,%s,%s,%s) RETURNING tickets."Date";"""
    conn = None
    ticket_date = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (winning_ticket.bonus_number,winning_ticket.date,winning_ticket.numbers,winning_ticket.gpd,winning_ticket.message))
        # get the generated id back
        ticket_date = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return ticket_date

player_numbers = [2,32,37,38,45,48]
player_gpd = ['65909547-01']

class WinningTicket:
    def __init__(self,date,numbers,bonus_number,gpd,type,message):
        self.date = date
        self.numbers = numbers
        self.bonus_number = bonus_number
        self.gpd = gpd
        self.type = type
        self.message = message
    def __repr__(self):
        return "Date: {}, Numbers: {}, Bonus: {}, GPD: {}, Type: {}, Message: {}".format(self.date,self.numbers,self.bonus_number,self.gpd,self.type, self.message)
def number_getter_649():
    type = '649'
    res = requests.get('http://www.wclc.com/winning-numbers/lotto-649-extra.htm')
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text,features="html.parser")
    date = soup.find('h4').string.strip('\n').strip()
    numbers = soup.find(class_='pastWinNumbers')
    winning_numbers = []
    message = ""
    for i in numbers:
        if i.string:
              b = i.string.strip('\n')
              if len(b)>0:
                winning_numbers.append(int(b))
##   gpd is the guaranteed prize draw
    gpd = soup.find('div', class_= 'pastWinNumGPDNumber').string
    bonus_soup = soup.find('li', class_='pastWinNumberBonus',)
    bonus_number = int(bonus_soup.get_text()[5:7])
    winning_ticket  = WinningTicket(date,winning_numbers,bonus_number,gpd,type, message)
    print(winning_ticket)
    return(winning_ticket)

def check_649(ticket):
    bonus_match = False
    number_match = 0
    gpd_match = False
    global player_numbers
    global player_gpd
    for i in ticket.numbers:
        if i in player_numbers:
            number_match += 1
    if ticket.bonus_number in player_numbers:
        bonus_match = True
    if ticket.gpd == player_gpd[0]:
        gpd_match = True
    message_to_send = evaluate_649(bonus_match,number_match,gpd_match)
    return message_to_send

def evaluate_649(bonus_match,number_match,gpd_match):
    results_message = "not a winner"
    if number_match == 6:
        results_message = "you won the grand prize"
    elif bonus_match == True and number_match == 5:
        results_message = "you won the second prize"
    elif number_match == 5:
        results_message = "you won a few thousand"
    elif number_match == 4:
        results_message = "you won a hundred bucks"
    elif number_match == 3:
        results_message = "you won 10 bucks"
    elif number_match == 2 and bonus_match == True:
        results_message = "you won a 5 bucks"
    elif number_match == 2:
        results_message = "you won a free play"
    if gpd_match:
        results_message = results_message + ", you won the guranteed"
    return results_message

##Use environmental variables for below https://www.twilio.com/docs/usage/secure-credentials
def send_text(message):
    account_sid = #Removed detail - I created this before I knew how to account for such variables on Heroku
    auth_token = #Removed detail - I created this before I knew how to account for such variables on Heroku
    client = Client(account_sid, auth_token)
    print(message)
    to_send = client.messages \
                    .create(
                         body=message,
                         from_=,#Removed detail - I created this before I knew how to account for such variables on Heroku
                         to=#Removed detail - I created this before I knew how to account for such variables on Heroku
                     )
    print(to_send.sid)
    return message
thedate = datetime.datetime.now()
winning_ticket = number_getter_649()
if thedate.strftime("%A") == "Thursday" or thedate.strftime("%A") == "Sunday":
    winning_ticket.message = send_text(check_649(winning_ticket))
    print(winning_ticket)
    insert_ticket(winning_ticket)
    loadfile = open(r'lotto649.csv','a',newline='')
    outputfile = csv.writer(loadfile)
    outputfile.writerow([winning_ticket.date,winning_ticket.numbers,winning_ticket.bonus_number,winning_ticket.gpd,winning_ticket.type,winning_ticket.message])
    loadfile.close()
