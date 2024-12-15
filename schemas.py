from datetime import datetime

def get_user_collection(db):
    return db.users

def get_conversations_collection(db):
    return db.conversations

def get_responses_collection(db):
    return db.responses

def add_user(db, user_data):
    users = get_user_collection(db)
    result = users.insert_one(user_data)
    return result.inserted_id

def add_message_to_conversation(db, user_id, sender, message):
    conversations = get_conversations_collection(db)
    conversations.update_one(
        {"user_id": user_id},
        {"$push": {"messages": {
            "sender": sender,
            "message": message,
            "timestamp": datetime.utcnow()
        }}},
        upsert=True
    )
