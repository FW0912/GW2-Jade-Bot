import os
from dotenv import load_dotenv
from pymongo import AsyncMongoClient

load_dotenv()
CONNECTION_STRING = os.getenv('CONNECTION_STRING')

def get_database():
    client = AsyncMongoClient(CONNECTION_STRING)

    return client['GW2Bot_origincost']

async def insertKey(userID, api_key):
    dbname = get_database()
    user_collection = dbname['User']

    user = {
        '_id' : userID,
        'api_key' : api_key
    }

    await user_collection.insert_one(user)

async def getKey(userID):
    dbname = get_database()
    user_collection = dbname['User']

    user = await user_collection.find_one({'_id': userID})

    if(user == None):
        return None

    return user['api_key']

async def updateKey(userID, new_api_key):
    dbname = get_database()
    user_collection = dbname['User']

    await user_collection.find_one_and_update({'_id': userID}, {'$set': {'api_key': new_api_key}})

async def deleteKey(userID):
    dbname = get_database()
    user_collection = dbname['User']

    await user_collection.find_one_and_delete({'_id': userID})