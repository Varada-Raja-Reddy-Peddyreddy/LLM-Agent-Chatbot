import streamlit as st
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from secret_api_keys import Groq_API_Key

import os
os.environ['groq_api_key']=Groq_API_Key

st.set_page_config(page_title="Chatbot",page_icon="🤖")
st.title("Langgraph Chatbot")

# initialize llm
llm = ChatGroq(api_key = Groq_API_Key,model_name =   "llama-3.2-90b-vision-preview")


class State(TypedDict):
    messages : Annotated [list,add_messages]

# create Graph_builder for creating StateGraph instance

Graph_builder = StateGraph(State)

#define a chatbot
def chatbot(State:State):
    return {"messages":[llm.invoke(State["messages"])]}

# Add chatbot to the graph

Graph_builder.add_node("chatbot",chatbot)
Graph_builder.set_entry_point("chatbot")
Graph_builder.set_finish_point("chatbot")

#compiler the graph
graph = Graph_builder.compile()

#Function to Stream Updates
def stream_graph_updates(user_input:str):
    initial_state = {"messages":[("user",user_input)]}
    responses = []
    for event in graph.stream(initial_state):
        for value in event.values():
            responses.append(value["messages"][-1].content)
    return responses

# initialize the session state to store conversation history
if "messages" not in st. session_state:
    st.session_state['messages']=[]

# sidebar for userinput

def chatbot_sidebar():
    st.sidebar.title("Chat With the Assistant")

    # input box for user message on the sidebar
    user_input = st.sidebar.text_input("Your message",key="input",placeholder="Type Your Message here...")

    # submit button in the sidebar
    if st.sidebar.button("send"):
        submit_message(user_input)

# Function to submit the message and Generate the message
def submit_message(user_input):
    if user_input:
        #Append input to conversation History
        st.session_state["messages"].append(f"You : {user_input}")

        # Get chatbot Response 
        responses = stream_graph_updates(user_input)

        for response in responses:
            st.session_state["messages"].append(f"Assistant : {response}")

# Main Page for displaying chat history
def display_chat():
    st.write("### Conversation")
    for message in st.session_state['messages']:
        st.write(message)

# Run the sidebar and main chat display
chatbot_sidebar() # input and submit  button on the sidebar
display_chat() # Display the conversation on the mainpage


