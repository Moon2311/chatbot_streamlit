import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

from dotenv import load_dotenv
load_dotenv()
# ********************************** Helper Functions ******************************

def generate_thread_id():
    """Generate a unique thread ID as a string"""
    return str(uuid.uuid4())

def add_thread(thread_id, thread_name=None, first_message=None):
    """Add a thread with a friendly name"""
    if thread_name is None:
        if first_message:
            # Use first 20 characters of first message as thread name
            thread_name = first_message[:20] + ("..." if len(first_message) > 20 else "")
        else:
            thread_name = f"Chat {len(st.session_state['chat_threads']) + 1}"
    st.session_state['chat_threads'].append({
        'thread_id': str(thread_id),
        'thread_name': thread_name
    })

def reset_chat(thread_name=None):
    """Start a new chat thread"""
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id, thread_name)
    st.session_state['message_history'] = []

def load_conversation(thread_id):
    """Load previous messages from chatbot backend"""
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

# **************************************** Session Setup ******************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

# Ensure current thread is added with default name
if not any(t['thread_id'] == st.session_state['thread_id'] for t in st.session_state['chat_threads']):
    add_thread(st.session_state['thread_id'])

# **************************************** Sidebar UI *********************************
st.sidebar.title('LangGraph Chatbot')

# Input for new chat name
new_chat_name = st.sidebar.text_input("New Chat Name", value="")

# Button to start a new chat
if st.sidebar.button('New Chat'):
    name = new_chat_name.strip() if new_chat_name.strip() != "" else None
    reset_chat(thread_name=name)

# Display existing chat threads
st.sidebar.header('My Conversations')
for thread in st.session_state['chat_threads'][::-1]:
    thread_id = thread['thread_id']
    thread_name = thread['thread_name']
    if st.sidebar.button(thread_name):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages

# **************************************** Main UI ************************************
st.title("🤖 LangGraph Chat")

# Display previous messages
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# User input
user_input = st.chat_input("Type here...")

if user_input:
    # If current thread has no name, use first 20 letters of this first message
    current_thread = next(
        (t for t in st.session_state['chat_threads'] if t['thread_id'] == st.session_state['thread_id']),
        None
    )
    if current_thread is None:
        add_thread(st.session_state['thread_id'], thread_name=None, first_message=user_input)

    # Add user message
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {
        'configurable': {'thread_id': st.session_state['thread_id']},
        "metadata":{
            "thread_id":st.session_state['thread_id']
        },
        'run_name':"chat_turn"
        }

    # Prepare placeholder for streaming assistant message
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_ai_message = ""

        for message_chunk, metadata in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages"
        ):
            if isinstance(message_chunk, AIMessage):
                full_ai_message += message_chunk.content
                message_placeholder.text(full_ai_message)

    # Save assistant message
    st.session_state['message_history'].append({'role': 'assistant', 'content': full_ai_message})
