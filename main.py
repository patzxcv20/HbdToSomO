import time
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = st.secrets["ASSISTANT_ID"]

# Initialize the OpenAI client and retrieve the assistant
client = OpenAI(api_key=OPENAI_API_KEY)
assistant = client.beta.assistants.retrieve(assistant_id=ASSISTANT_ID)

# Initialize session state to store conversation history locally to display on UI
if "chat_history" not in st.session_state:
    # Include the initial assistant message in the chat history
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hi, SomO. Mac is here to answer you!"}
    ]

# Create a new thread if it does not exist
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    # Add the initial assistant message to the thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="assistant",
        content="Hi, SomO. Mac is here to answer you!"
    )

# Title
st.set_page_config(page_title="HBDSomO!", page_icon="🤖")
st.title("Happy 22nd Birthday, SomO! 🎉")

# Display a welcome image
st.image('Welcome.gif', caption='Wish you live a happy life krub. I miss u, Hurry back!', use_column_width=True)

# Display messages in chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar="SomO.jpg"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("user", avatar="Mac.jpg"):
            st.markdown(message["content"])

# Textbox and streaming process
if user_query := st.chat_input("Don't ask me difficult questions 🥲"):

    # Display the user's query
    with st.chat_message("user",avatar="SomO.jpg"):
        st.markdown(user_query)

    # Store the user's query into the history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_query
    })
    
    # Add user query to the thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_query
    )

    # Stream the assistant's reply
    with st.chat_message("assistant"):
        stream = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=ASSISTANT_ID,
            stream=True
        )
        
        # Empty container to display the assistant's reply
        assistant_reply_box = st.empty()
        # A blank string to store the assistant's reply
        assistant_reply = ""

        # Iterate through the stream 
        for event in stream:
            # Check if the event contains a delta text
            if isinstance(event, ThreadMessageDelta):
                if isinstance(event.data.delta.content[0], TextDeltaBlock):
                    # Append new text to the assistant's reply
                    assistant_reply += event.data.delta.content[0].text.value
                    # Update the assistant reply box
                    assistant_reply_box.markdown(assistant_reply)
        
        # Once the stream is over, update chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": assistant_reply
        })
