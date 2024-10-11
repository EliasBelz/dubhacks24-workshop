import streamlit as st
from streamlit_chat import message
import random
import google.generativeai as genai
import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv

load_dotenv()

MAX_CONTEXT = 5 # conversational memory window.

#=====================================================#
#                      API SETUP                      #
#=====================================================#

# Gemini setup

# Replace system prompt with your own
system_prompt = "You are a helpful chatbot."

genai.configure(api_key=os.environ["API_KEY"])

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_prompt
)

# Embedding function for vector queries
google_ef  = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=os.environ["API_KEY"])

# Vector database /!\ NOTE: must load_data.py first /!\
client = chromadb.PersistentClient(path="./data/vectorDB")
collection = client.get_collection(name="class_db", embedding_function=google_ef)

#=====================================================#
#                     Chat Code                       #
#=====================================================#

# Storing the displayed messages
if 'past' not in st.session_state:
    st.session_state['past'] = ["What's up?! What do you do?"]

# Add default welcome message. This can be useful for introducing your chatbot
if 'generated' not in st.session_state:
    st.session_state['generated'] = [
        "Beep boop -I'm a chatbot"
        ]

# Pick random avatar
if "avatars" not in st.session_state:
    st.session_state.avatars = {"user": random.randint(0,100), "bot": random.randint(0,100)}

# Storing the conversation history for the LLM
if "messages" not in st.session_state:
    st.session_state.messages = []

llm = model.start_chat(history=st.session_state.messages)

# Function to send a message to the LLM and update the UI
def chat(user_input=""):
    if user_input == "":
        user_input = st.session_state.input
    st.session_state.input = ""

    # Create chat completion based on message history + new user input
    completion = llm.send_message(user_input)

    # Add new user message to LLM message history
    st.session_state.messages.append({"role": "user", "parts": user_input})

    # Add LLM response to message history
    st.session_state.messages.append({"role": "model", "parts": completion.text})

    # Limit LLM message history using sliding window
    if len(st.session_state.messages) > MAX_CONTEXT:
      # keeps system call at index 0
      st.session_state.messages = st.session_state.messages[:MAX_CONTEXT]


    # Add LLM message to UI
    st.session_state.generated.append(completion.text)
    # Add user message to UI
    st.session_state.past.append(user_input)

# Function to query the vector database
# Returns a formatted string
def query_db(query, n_results=1):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return "".join(result for result in results["documents"][0])


#=====================================================#
#               Font-end, yup thats it!               #
#=====================================================#

st.set_page_config(page_title="Dubhacks 24 Demo", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.header("CSEED x Dubhacks 24 Generative AI Demo\n")

with st.sidebar:
    st.markdown("# About 🙌")
    st.markdown("CSEED x Dubhacks 24 Workshop")
    st.markdown("Feel free to edit any of this code for your own use!")
    st.markdown("Make something cool using generative AI")
    st.markdown("---")
    st.markdown("Created by Elias Belzberg for CSEED x Dubhacks 24")
    st.markdown("[Code available here!](https://github.com/EliasBelz/dubhacks24-workshop)")
    st.markdown("[Join the CSEED Discord!](https://discord.gg/xXUwERqHsz)\n")
    st.markdown("---")
    st.markdown("This demo uses:\n"
                "- Google Gemini\n"
                "- ChromaDB\n"
                "- Streamlit")
    st.markdown("---")

# We will get the user's input by calling the chat function
input_text = st.text_input("Input a prompt here!",
                                placeholder="Enter prompt: ", key="input", on_change=chat)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        if st.session_state['past'][i] != "":
            message(st.session_state['past'][i], is_user=True, avatar_style="adventurer",seed=st.session_state.avatars["bot"], key=str(i) + '_user')
        message(st.session_state["generated"][i],seed=st.session_state.avatars["user"] , key=str(i))