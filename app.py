import streamlit as st
from streamlit_chat import message
import random
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = False
MAX_CONTEXT = 5 # conversational memory window. First index is system call

#=====================================================#
#                      API SETUP                      #
#=====================================================#
genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                              # Replace system prompt
                              system_instruction="You are a helpful chatbot that")


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


#=====================================================#
#               Font-end, yup thats it!               #
#=====================================================#

st.set_page_config(page_title="Dubhacks 24 Demo", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.header("CSEED Dubhacks 24 Generative AI Demo\n")

with st.sidebar:
    st.markdown("# About 🙌")
    st.markdown("CSEED Dubhacks 24 Workshop")
    st.markdown("Feel free to edit any of this code for your own use!")
    st.markdown("Make something cool using generative AI")
    st.markdown("---")
    st.markdown("Created by Elias Belzberg for CSEED")
    st.markdown("Code available here!\n"
                "[github.com/EliasBelz/ski-gpt](https://github.com/EliasBelz/dubhacks24-workshop)")
    st.markdown("---")
    st.markdown("This demo uses:\n"
                "- Google Gemini\n"
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