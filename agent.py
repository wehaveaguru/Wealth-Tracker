import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")



client = Groq(api_key=api_key)


def get_response(query, file_context=None):
    messages = []
    if file_context:
        messages.append({
            "role": "system",
            "content": f"You are Lumina Advisor, an expert financial AI assistant. The user has uploaded a file with the following content/context:\n\n{file_context}\n\nUse this information to answer the user's questions. Answer accurately and professionally."
        })
    else:
        messages.append({
            "role": "system",
            "content": "You are Lumina Advisor, an expert financial AI assistant. Assist the user with their queries professionally."
        })
        
    messages.append({
        "role": "user",
        "content": query,
    })

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
    )

    return chat_completion.choices[0].message.content