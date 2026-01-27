import datetime
from google import genai
from google.genai import types
# 1. Setup the Client
# Replace "YOUR_PROJECT_ID" with your actual project ID (e.g. "my-project-123")
client = genai.Client(
    vertexai=True,
    project="studio-9101802118-8c9a8",
    location="us-central1"
)

# 2. Start the Chat
chat = client.chats.create(
    model="gemini-2.5-pro",
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful, expert assistant. Be concise, accurate, and professional."
    )
)

print("--- Chatbot started! Type 'quit' to exit. ---")

while True:
    # 1. Get input from you
    user_input = input("You: ")

    # 2. Check if you want to quit
    if user_input.lower() in ["quit", "exit"]:
        print("Goodbye!")
        break

    # 3. Send to Vertex AI, Print, and SAVE
    try:
        response = chat.send_message(user_input)
        print(f"AI: {response.text}")
        print("-" * 20)

        # --- NEW PART: Save to a file ---
        # "a" means "append" (add to the end, don't overwrite)
        with open("chat_history.txt", "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] YOU: {user_input}\n")
            f.write(f"[{timestamp}] AI:  {response.text}\n")
            f.write("-" * 40 + "\n")
        # -------------------------------

    except Exception as e:
        print(f"Error: {e}")

    # 4. Check if you want to quit
    if user_input.lower() in ["quit", "exit"]:
        print("Goodbye!")
        break

    # 5. Send to Vertex AI and print response
    try:
        response = chat.send_message(user_input)
        print(f"AI: {response.text}")
        print("-" * 20)
    except Exception as e:
        print(f"Error: {e}")