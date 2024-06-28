import sys
import json
import time
import ollama
from langchain_community.document_loaders import PyPDFLoader

# Function to load, split, and retrieve file docs
def load_pages(file_path):
    loader = PyPDFLoader(file_path)  # Initializes object for loading pdf
    pages = loader.load_and_split()  # Loads pdf and splits by pages
    return pages

# Function to extract the raw text from the loaded file
def load_doc(pages):
    doc_text = ""
    for page in pages:
        doc_text += page.page_content
    return doc_text

# Function to generate response
def generate_response(chat_history):
    response = ollama.chat(model='llama3:instruct', messages=chat_history)
    return response['message']['content']

# Function to load json formatted questions from llm response. Adds last curly brace if a json decode exception is raised.
def load_json(response):
    try:
        data = json.loads(response)
        return data
    except json.JSONDecodeError as error:
        #print("String not in json format. Error Message:", error.msg)
        #print("Attempting to re-parse string into json format")
        response += "}"
        #print("\nText:\n" + response + "\n")
        data = json.loads(response)
        #print("Data:\n" + str(data))
        return data

# Function to log errors to a text file
def log_error(message):
    with open('error.log', 'a', encoding='utf-8') as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S") + ': ' + message + '\n')

def main():
    # Telling llm to identify each question from uploaded document, then extract them in json format
    system_string = f"Identify each question in the following document provided by the user, then respond to their prompt by writing each question exactly as it is written in the document but in json format, where the key is \"Question [number here]\", and the value for each key is the exact text of the question. Don't write any text in your response other than the json formatted questions. You're output should look like this: \"{{key: value, key: value, key: value, ...}}\""
    system_message = {"role": "system", "content": system_string}
    file_path = sys.argv[1]
    
    #file_name = file_path.split("\\")[-1]
    pages = load_pages(file_path=file_path)
    doc_text = load_doc(pages)
    user_message = {"role": "user", "content": doc_text}
    chat_history = [system_message, user_message]
    response = generate_response(chat_history=chat_history)
    questions_json = load_json(response=response)
            
    # Send json formatted questions to js server
    print(json.dumps(questions_json))

if __name__ == "__main__":
    main()
