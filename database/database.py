import motor.motor_asyncio
from config import ADMINS, DB_URL, DB_NAME

# Initialize MongoDB Client
dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
database = dbclient[DB_NAME]

# Collections for users, admins, and links
user_data = database['users']
admin_data = database['admins']
link_data = database['links']

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

def new_user(id):
    """
    Returns a new user document template for insertion.
    """
    return {
        '_id': id,
        'verify_status': {
            'is_verified': False,
            'verified_time': "",
            'verify_token': "",
            'link': ""
        }
    }

# Link-related Functions
async def new_link(hash: str):
    """
    Creates a new link document with initial click count.
    """
    return {
        'clicks': 0,
        'hash': hash
    }

async def gen_new_count(hash: str):
    """
    Generates a new link count by inserting a link document.
    """
    data = await new_link(hash)
    await link_data.insert_one(data)
    return

async def present_hash(hash: str):
    """
    Checks if a specific hash is present in the link collection.
    """
    found = await link_data.find_one({"hash": hash})
    return bool(found)

async def inc_count(hash: str):
    """
    Increments the click count for a specific hash.
    """
    data = await link_data.find_one({'hash': hash})
    clicks = data.get('clicks', 0)
    await link_data.update_one({'hash': hash}, {'$set': {'clicks': clicks + 1}})
    return

async def get_clicks(hash: str):
    """
    Retrieves the click count for a specific hash.
    """
    data = await link_data.find_one({'hash': hash})
    return data.get('clicks', 0)


# User-related Functions
async def present_user(user_id: int):
    """
    Checks if a user exists in the database by their user ID.
    """
    found = await user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    """
    Adds a new user to the user_data collection.
    """
    user = new_user(user_id)
    await user_data.insert_one(user)
    return

async def db_verify_status(user_id: int):
    """
    Retrieves the verification status of a user from the database.
    """
    user = await user_data.find_one({'_id': user_id}, {'verify_status': 1})
    if user:
        return user.get('verify_status', default_verify)
    return default_verify

async def db_update_verify_status(user_id: int, verify):
    """
    Updates the verification status of a user in the database.
    """
    await user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})
    return

async def del_user(user_id: int):
    """
    Deletes a user from the database by their user ID.
    """
    await user_data.delete_one({'_id': user_id})
    return

async def full_userbase():
    """
    Retrieves the full list of user IDs from the database.
    """
    user_docs = user_data.find({}, {'_id': 1})  # Only fetch the '_id' field
    user_ids = [doc['_id'] async for doc in user_docs]
    return user_ids

# Bulk Deletion for Blocked Users or inactive or invalid users
async def bulk_del_users(user_ids: list):
    """
    Deletes multiple users from the database who have blocked the bot.
    """
    await user_data.delete_many({'_id': {'$in': user_ids}})
    return


# Admin-related Functions
async def present_admin(user_id: int):
    """
    Checks if an admin exists in the database.
    """
    found = await admin_data.find_one({'_id': user_id})
    return bool(found)

async def add_admin(user_id: int):
    """
    Adds a new admin to the admin_data collection.
    """
    user = new_user(user_id)
    await admin_data.insert_one(user)
    ADMINS.append(int(user_id))
    return

async def del_admin(user_id: int):
    """
    Deletes an admin from the admin_data collection.
    """
    await admin_data.delete_one({'_id': user_id})
    ADMINS.remove(int(user_id))
    return

async def full_adminbase():
    """
    Retrieves the full list of admin IDs from the admin_data collection.
    """
    user_docs = admin_data.find()
    user_ids = [int(doc['_id']) async for doc in user_docs]
    return user_ids
