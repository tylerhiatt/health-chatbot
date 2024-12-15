import tkinter as tk
from tkinter import scrolledtext
from connection import connect_mongo, connect_redis, setup_openai
from schemas import add_user, add_message_to_conversation
from chatbot import generate_response_with_context
from datetime import datetime


class ChatbotGUI:
    def __init__(self):
        # backend connections
        self.db = connect_mongo()
        self.redis_client = connect_redis()
        setup_openai()

        # user info
        self.user_id = None
        self.setup_user()

        # main window
        self.window = tk.Tk()
        self.window.title("Mental Health Chatbot")
        self.window.geometry("500x600")

        # conversation display (ScrolledText)
        self.chat_display = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, state='disabled')
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # user input field
        self.user_input = tk.Entry(self.window, font=("Arial", 14))
        self.user_input.pack(padx=10, pady=(0, 10), fill=tk.X)

        # send button
        self.send_button = tk.Button(self.window, text="Send", command=self.send_message, bg="lightblue", font=("Arial", 12))
        self.send_button.pack(padx=10, pady=10)

        # enter key binding
        self.window.bind("<Return>", lambda event: self.send_message())

    def setup_user(self):
        user_choice = input("Enter your user ID (or type 'new' to create a new user): ").strip()
        if user_choice.lower() == "new":
            name = input("Enter your name: ").strip()
            age = int(input("Enter your age: "))
            preferences = input("Enter your preferences (comma-separated): ").strip().split(",")

            user_data = {
                "name": name,
                "age": age,
                "preferences": preferences,
                "created_at": datetime.utcnow()
            }

            self.user_id = str(add_user(self.db, user_data))
            print(f"New user created! Your user ID is: {self.user_id}")
        else:
            self.user_id = user_choice
            print(f"Welcome back! Your user ID is: {self.user_id}")

    def send_message(self):
        user_message = self.user_input.get()
        if user_message.strip():
            # display user's message
            self.display_message("You", user_message)
            self.user_input.delete(0, tk.END)  # clear input field

            # add user's message to MongoDB
            add_message_to_conversation(self.db, self.user_id, "user", user_message)

            # bot response
            try:
                bot_response = generate_response_with_context(self.db, self.user_id, user_message, self.redis_client)
                self.display_message("Chatbot", bot_response)
            except Exception as e:
                self.display_message("Chatbot", f"Error: {str(e)}")

    def display_message(self, sender, message):
        self.chat_display.configure(state='normal')  # enable editing
        self.chat_display.insert(tk.END, f"{sender}: {message}\n")
        self.chat_display.configure(state='disabled')  # disable editing
        self.chat_display.see(tk.END)  # auto-scroll

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    gui = ChatbotGUI()
    gui.run()
