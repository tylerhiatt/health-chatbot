from pymongo import MongoClient
import redis
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def connect_mongo():
    client = MongoClient(os.getenv("MONGO_URI"))
    return client.chatbot_db

def connect_redis():
    host = os.getenv("REDIS_HOST")
    port = int(os.getenv("REDIS_PORT"))
    password = os.getenv("REDIS_PASSWORD")

    try:
        redis_client = redis.Redis(host=host, port=port, password=password, db=0)
        
        # # Test the connection
        # redis_client.ping()
        # print("Connected to Redis successfully!")
        return redis_client
    
    except redis.exceptions.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
        raise

def setup_openai():
    openai.api_key = os.getenv("OPENAI_API_KEY")
