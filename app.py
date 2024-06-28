import sys
import json
import time
import ollama

# Function to generate response
def generate_response(chat_history):
    response = ollama.chat(model='llama3:instruct', messages=chat_history)
    return response['message']['content']

# Function to update chat history
def update_history(chat_history, message):
    chat_history.append(message)
    return chat_history

# Function to log errors to a text file
def log_error(message):
    with open('error.log', 'a', encoding='utf-8') as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S") + ': ' + message + '\n\n')

def main():
    try:
        chat_history = json.loads(sys.argv[1])
        user_message = sys.argv[2]

        user_message = {"role": "user", "content": user_message}
        chat_history = update_history(chat_history=chat_history, message=user_message)
        response = generate_response(chat_history=chat_history)
        llm_message = {"role": "assistant", "content": response}
        chat_history = update_history(chat_history=chat_history, message=llm_message)
        formatted_response = response.replace("\n", "<br />")

        # Return both response and chat history
        result = {
            "response": formatted_response,
            "chat_history": chat_history
        }
        # Send result to js server
        print(json.dumps(result))
    except json.JSONDecodeError as decode_error:
        log_error(str(decode_error))

if __name__ == "__main__":
    main()
