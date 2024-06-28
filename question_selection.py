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
        f.write(time.strftime("%Y-%m-%d %H:%M:%S") + ': ' + message + '\n')

def main():
    chat_history = []
    question = sys.argv[1]

    # Telling llm to act as a tutor, guiding the user for the selected question
    system_string = f"Act as a tutor for the user by guiding the user into thinking of the correct answer without doing any of the work for the user or providing the user with the correct answer. Only provide the answer if the user mentions it first and explains thier logic for getting the correct answer. If you do not know the answer to a question, be honest with the user. Tutor the user through the following problem: \"{question}\""
    system_message = {"role": "system", "content": system_string}
    chat_history = update_history(chat_history=chat_history, message=system_message)
    response = generate_response(chat_history=chat_history)
    chat_history[0]["content"] = chat_history[0]["content"].replace("\"", "")  # For the love of god do not delete (formats system_string to be compatible for javascript)
    llm_message = {"role": "assistant", "content": response}
    chat_history = update_history(chat_history=chat_history, message=llm_message)
    formatted_response = response.replace("\n", "<br />")

    # Return both response and chat history
    result = {
        "response": formatted_response,
        "chat_history": chat_history
    }
    # Send result to js server
    print(json.dumps(result, ensure_ascii=False))
    
if __name__ == "__main__":
    main()
