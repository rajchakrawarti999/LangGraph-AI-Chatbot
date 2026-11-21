
import os
import uuid
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage , HumanMessage
from langchain_openai import ChatOpenAI
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="deepseek-v4.1-flash",
    api_key=os.getenv("FREEMODEL_API_KEY"),
    base_url="https://freemodel.in/v1",
    max_retries=3,
    timeout=60
)

# Define state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# Chatbot node
def chat_node(state: ChatState):
    messages = state["messages"]

    response = llm.invoke(messages)

    return {"messages": [response]}

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)

conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()



# *********password************

password_hasher = PasswordHasher()

def hash_password(password : str) ->str:
        return password_hasher.hash(password)


def verify_password(password : str, stored_hash : str) -> bool:
    try:
        return password_hasher.verify(stored_hash, password)

    except(VerifyMismatchError , VerificationError):
        return False



#***********signUp function*******

def register_user(username : str, password : str):

    username = username.strip()

    if len(username) < 3:
        return False, "Username must contain at least 3 characters"

    if len(password) < 8:
        return False , "Password must contain at least 8 characters"

    user_id = str(uuid.uuid4())

    hashed_password = hash_password(password)

    try :
        with conn:
            conn.execute(

                """
                INSERT INTO users (user_id, username, password_hash)
                VALUES (?, ?, ?)
                """,
                (user_id, username, hashed_password)
            )

        return True, "Account created successfully"

    except sqlite3.IntegrityError:
        return False, "Username already exists"


# ************* loging face ********

def login_user(username : str, password : str):

    username = username.strip()

    cursor = conn.execute(

        """
        SELECT user_id, password_hash
        FROM users
        WHERE username = ?
        """,

        (username,)
    )

    user = cursor.fetchone()

    if user is None:
        return False , None, "Invalid username or password"

    user_id, stored_hash = user

    if not verify_password(password , stored_hash):
        return False, None, "Invalid username or password"

    return True, user_id, "Login sucessful"











# Initialize checkpointer
checkpointer = SqliteSaver(conn=conn)

# Build graph
graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

# Compile graph
chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads(user_id):

    cursor = conn.execute(
        """
        SELECT thread_id
        FROM conversations
        WHERE user_id = ?
        ORDER BY rowid DESC
        """,
        (str(user_id),)
    )

    return [row[0] for row in cursor.fetchall()]



# Conversation metadata table

conn.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    thread_id TEXT PRIMARY KEY,
    title TEXT NOT NULL DEFAULT 'New chat'
)
""")
conn.commit()

cursor = conn.execute("PRAGMA table_info(conversations)")

columns = [column[1] for column in cursor.fetchall()]

if "user_id" not in columns:

    conn.execute(
        """
        ALTER TABLE conversations
        ADD COLUMN user_id TEXT
        """
    )

    conn.commit()

def save_chat_title(thread_id, title, user_id):

    with conn:

        cursor = conn.execute(

            """
            INSERT INTO conversations (thread_id, title, user_id)
            VALUES (?, ?, ?)

            ON CONFLICT(thread_id)
            DO UPDATE SET title = excluded.title
            WHERE conversations.user_id = excluded.user_id
            """,
            (str(thread_id), title, str(user_id))
        )

    if cursor.rowcount !=1:
        raise PermissionError("Conversation access denied")


def retrieve_chat_titles(user_id):

    cursor = conn.execute(
        """
        SELECT thread_id, title
        FROM conversations
        WHERE user_id = ?
        """,
        (str(user_id),)
    )

    return dict(cursor.fetchall())