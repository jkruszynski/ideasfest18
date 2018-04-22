import requests
import pandas as pd
from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify
import re

db_connect = create_engine('sqlite:///helpapp.db')

class User():
    userid = 0
    lat = 0
    long = 0
    individual = 'N'
    tier = 3
    
def newUser(u):
    conn = db_connect.connect()
    user=User()
    query = conn.execute("INSERT INTO responder (individual, lat, long, tier) VALUES (?,?,?,?)",(u.individual,u.lat,u.long,u.tier))
    
    return 'success'

def newUserQual(userid,qual):
    conn = db_connect.connect()
    user=User()
    query = conn.execute(
            "INSERT INTO res_qual_ref (resid, qualid) VALUES (?,?)",(userid,qual))
    
    return 'success'

def getResponderID(u):
    conn = db_connect.connect()
    user=User()
    query = conn.execute("SELECT max(resid) FROM responder")
    userid = 0
    for row in query:
        userid = row[0]
    
    return userid

def getVictimLocations(viclist):
    conn = db_connect.connect()
    user=User()
    filteredUsers = []
    for i in viclist:
        query = conn.execute("SELECT * FROM users WHERE assistance = 'Y' AND userid = ?",(i))
        for row in query:
            filteredUsers.append(row)
    
    return filteredUsers

def getNeedsOptions(t):
    conn = db_connect.connect()
    user=User()
    query = conn.execute("SELECT needid FROM tier_needs_ref WHERE tierid = ?", (t))
    needs = []
    for row in query:
        needs.append(row)
    t = getVictimOptions(needs)

    return t


def getVictimOptions(n):
    vicList = []
    for i in n:
        conn = db_connect.connect()
        query = conn.execute("SELECT userid FROM user_needs_ref WHERE needid = ?", i)
        for row in query:
            t=row[0]
            if t not in vicList:
                vicList.append(t)
    
    return vicList

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

r = requests.post('https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyBLHoe_WZjcrzZ6wyPm851daaV3LoMSXVU')
r = r.json()


user1=User()
user1.lat = r['location']['lat'] + random.uniform(-.05, .05)
user1.long = r['location']['lng'] + random.uniform(-.05, .05)

groupResponse = input('Are you an individual or group? i or g\n')

if groupResponse.lower() == 'i':
    user1.individual = 'Y'
elif groupResponse.lower() == 'g':
    user1.individual = 'N'

tierResponse = int(input('What tier are you?\n1: Certified First Responder\n2: First Responder\n3: Volunteer Responder\n'))

user1.tier=tierResponse

newUser(user1)
user1.userid = getResponderID(user1)

quals = input('What are your qualifications? Separate by commas\n1: Aid Agreement\n2: First Responder\n3: First Aid\n4: Safety and Awareness\n5: Incident Command\n6: CPR\n')
quals=quals.split(',')
for i in quals:
    newUserQual(user1.userid,int(i.strip()))

us = getNeedsOptions(user1.tier)
vicResults = getVictimLocations(us)


search = "key=AIzaSyAu6YVzY44hgwYc6nvjw1zpaoElGPG5xY8"
search+="&units=imperial"
search+="&origins="+str(user1.lat)+","+str(user1.long)
vicString = ""
for i in vicResults:
    if i[0] == 0:
        vicString +=str(i[1])+','+str(i[2])
    else:
        vicString +='|'+str(i[1])+','+str(i[2])
search+="&destinations=" + vicString
search

api_url = "https://maps.googleapis.com/maps/api/distancematrix/json?"+search
maps_api = requests.get(api_url)
maps_api = maps_api.json()

#maps_api['rows'][0]['elements'][0]['duration']
distanceList = []
count=0
for r in maps_api['rows']:
    for i in r['elements']:
        distanceList.append([count,float(i['duration']['text'].split()[0])])
        count+=1
    
distanceList.sort(key=lambda x: x[1])

top5 = distanceList[:5]
print('\nHere are the nearest victims in need of assistance:')
for i in top5:
    i.append(maps_api['destination_addresses'][i[0]])
    print(maps_api['destination_addresses'][i[0]])

selection = int(input('Which victim would you like to help? 1-5\n'))

vicToHelp = top5[selection-1]

print('\n\nHere are the directions\n')

search = "key=AIzaSyCIEwaZkLAwrq7cwinrmgQOjZ_PZGo7Yxw"
search+="&units=imperial"
search+="&origin="+str(user1.lat)+","+str(user1.long)
search+="&destination=" + vicToHelp[2]
search


api_url = "https://maps.googleapis.com/maps/api/directions/json?"+search
directions_api = requests.get(api_url)
directions_api = directions_api.json()

for i in directions_api['routes']:
    for l in i['legs']:
        count = 1
        for s in l['steps']:
            test = s['html_instructions'].replace('\u003cb\u003e','')
            test = cleanhtml(test)
            if 'Destination' in test:
                print(str(count) + ': ' + test.split('Destination will be on the')[0])
                count+=1
                print(str(count) + ': Destination will be on the' + test.split('Destination will be on the')[1])
            else:
                print(str(count)+": " +test)
            count+=1


