from connection import connect_mongo, connect_redis, setup_openai
from schemas import add_user, add_message_to_conversation
import openai
from datetime import datetime


def generate_response_with_context(db, user_id, message, redis_client):
    # check Redis for cached response
    cached_response = redis_client.get(message.lower())
    if cached_response:
        print(f"Chatbot (from cache): {cached_response}")
        return cached_response

    # grab conversation history from MongoDB
    conversation = db.conversations.find_one({"user_id": user_id})
    messages = [{"role": "system", "content": "You are a helpful mental health chatbot."}]

    if conversation:
        for msg in conversation["messages"]:
            messages.append({"role": "user" if msg["sender"] == "user" else "assistant", "content": msg["message"]})


    # add user's new message to the context
    messages.append({"role": "user", "content": message})

    # Call the OpenAI Chat API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=messages
        )
        response_content = response['choices'][0]['message']['content']

        # Add the chatbot's response to the MongoDB conversation
        db.conversations.update_one(
            {"user_id": user_id},
            {"$push": {"messages": {"sender": "bot", "message": response_content}}},
            upsert=True
        )

        # Cache the response
        redis_client.set(message.lower(), response_content)

        return response_content

    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "Sorry, I couldn't process that. Please try again."
    

def handle_user_interaction():
    db = connect_mongo()
    redis_client = connect_redis()
    setup_openai()

    print("Welcome to the Mental Health Chatbot!")
    user_id = input("Enter your user ID (or type 'new' to create a new user): ").strip()

    # create a new user profile
    if user_id.lower() == "new":
        name = input("Enter your name: ").strip()
        age = int(input("Enter your age: "))
        preferences = input("Enter your preferences (comma-separated): ").strip().split(",")

        user_data = {
            "name": name,
            "age": age,
            "preferences": preferences,
            "created_at": datetime.utcnow()
        }

        user_id = str(add_user(db, user_data))
        print(f"New user created! Your user ID is: {user_id}")
    
    print("I am a Mental Health Chatbot. Feel free to tell me how you're feeling and ask me any questions you may have, and I'll do my best to offer you advice!")

    while True:
        user_message = input("You: ").strip()
        if user_message.lower() in ["quit", "exit"]:
            print("Chatbot: Goodbye! Take care!")
            break

        # add user's message to MongoDB
        add_message_to_conversation(db, user_id, "user", user_message)

        # generate a response from ChatGPT (or fallback logic)
        response = generate_response_with_context(db, user_id, user_message, redis_client)

        print(f"Chatbot: {response}")


if __name__ == "__main__":
    handle_user_interaction()