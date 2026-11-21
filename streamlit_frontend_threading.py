import streamlit as st
from langGraph_backend import (
    chatbot,
    retrieve_all_threads,
    save_chat_title,
    retrieve_chat_titles
)

from langGraph_backend import register_user, login_user
from langchain_core.messages import HumanMessage, AIMessage
import uuid

#*************utility Function***********

def generate_thread_id():
    return str(uuid.uuid4())


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []
    st.session_state['thread_titles'][thread_id] = "New chat"


def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)



def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id' : thread_id}})

    # check id messages key exists in state values , return empty list if not
    return state.values.get('messages', [])

# ******* Loging page ****************

if "authenticated" not in st.session_state:
    st.session_state['authenticated'] = False

if "user_id" not in st.session_state:
    st.session_state['user_id'] = None

if "username" not in st.session_state:
    st.session_state["username"] = None



# ************** Login / signup interface ****

if not st.session_state['authenticated']:
    st.title("Wellcome to AI Chatbot")

    option = st.radio(

        "Choose an option",
        ["Login", "Signup"],
        horizontal = True
    )

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type = "password"
    )

    if option == "Login":

        if st.button("Login"):

            success, user_id, message = login_user(
                username,
                password
            )

            if success:
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = user_id
                st.session_state["username"] = username.strip()

                st.rerun()

            else:
                st.error(message)
    else:

        if st.button("Create Account"):

            success, message = register_user(
                username,
                password
            )

            if success:
                st.success(message)
                st.info("Account created ! Now select Login .")

            else :
                st.error(message)

    st.stop()

# *******************session setup ***************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = retrieve_chat_titles(
        st.session_state["user_id"]
    )

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads(
        st.session_state["user_id"]
    )

add_thread(st.session_state['thread_id'])


#**********************Sidebar UI ************

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat '):
    reset_chat()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:

    title = st.session_state['thread_titles'].get(
        thread_id,
        "New chat"
    )
    if st.sidebar.button(title ,key=str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            elif isinstance(msg, AIMessage):
                role = 'assistant'
            else:
                continue

            temp_messages.append({'role' : role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages



# **************Main UI ***************

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input('Type here')

if user_input :

    # first add the message to message_history
    thread_id = st.session_state['thread_id']

    if not st.session_state['message_history']:
        title =  user_input[ : 40]
        st.session_state['thread_titles'][thread_id] = title

        save_chat_title(thread_id, title,  st.session_state["user_id"])


    st.session_state['message_history'].append({'role': 'user', 'content':user_input})
    with st.chat_message('user'):
        st.text(user_input)


    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {
            "thread_id": st.session_state["thread_id"]
        },
        "run_name": "chat_turn",
    }

    # first add the message to message_history

    with st.chat_message('assistant'):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {'messages' : [HumanMessage(content=user_input)]},
                config = CONFIG,
                stream_mode = 'messages'
            ):

                if isinstance(message_chunk, AIMessage):
                    # yield only assistant tokens
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content' : ai_message})