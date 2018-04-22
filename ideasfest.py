import requests
import pandas as pd
from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify
import random

db_connect = create_engine('sqlite:///helpapp.db')

class User():
    userid = 0
    lat = 0
    long = 0
    assistance = 'N'
    water = 'N'
    med = 'N'
    pets = 'N'
    baby = 'N'
    
def newUser(u):
    conn = db_connect.connect()
    user=User()
    query = conn.execute(
            "INSERT INTO users (lat, long, assistance) VALUES (?,?,?)",(u.lat,u.long,u.assistance))
    
    return 'success'

def updateNeeds(u):
    conn = db_connect.connect()
    user=User()
    query = conn.execute(
            "INSERT INTO users (lat, long, assistance) VALUES (?,?,?)",(u.lat,u.long,u.assistance))
    
    return 'success'

def updateUser(response, u):
    conn = db_connect.connect()
    query = conn.execute("UPDATE users SET assistance = ? WHERE users.userid = ?",(response,u.userid))


def getID(u):
    conn = db_connect.connect()
    user=User()
    query = conn.execute("SELECT max(userid) FROM users")
    userid = 0
    for row in query:
        userid = row[0]
    
    return userid

def newUserNeed(userid,need):
    conn = db_connect.connect()
    user=User()
    query = conn.execute(
            "INSERT INTO user_needs_ref (userid, needid) VALUES (?,?)",(userid,need))
    
    return 'success'


r = requests.post('https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyBLHoe_WZjcrzZ6wyPm851daaV3LoMSXVU')
r = r.json()


user1=User()
user1.lat = r['location']['lat'] + random.uniform(-.05, .05)
user1.long = r['location']['lng'] + random.uniform(-.05, .05)
user1.assistance = 'Y'

newUser(user1)
user1.userid = getID(user1)

search = "key=AIzaSyBejb73y72iQx6d79eC86fSikLrF6l4rEg"
search+="&location="+str(user1.lat)+","+str(user1.long)
search+="&radius=3000"
search+="&keyword=disaster+center"
search

api_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"+search
maps_api = requests.get(api_url)
maps_api = maps_api.json()


print('Here are Disaster Recovery locations within a mile of your location')
count = 1
for i in maps_api['results']:
    print(count, ': ' + i['name'])
    print('\t'+i['vicinity'])
    print('')
    count+=1


response = input('Can you reach one of these areas?: Y/N').upper()
    
if response == 'Y':
    updateUser(response,user1)
    print('Please proceed to the closest area')
else:
    needs = input('What do you need? Water, Medical, Baby, Pets.... Separate by commas\n')

    needs = needs.split(',')
    for i in needs:
        if i.lower().strip() == 'water':
            newUserNeed(user1.userid, 0)
        elif i.lower().strip() == 'medical':
            newUserNeed(user1.userid, 1)
        elif i.lower().strip() == 'baby':
            newUserNeed(user1.userid, 2)
        elif i.lower().strip() == 'pets':
            newUserNeed(user1.userid, 3)
        else:
            print(i + ' is not a valid response')



