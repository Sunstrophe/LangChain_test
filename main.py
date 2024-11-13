"""
This file comprise the main functionality of this project

This project aims to create a tool calling agent with persistent memory to guide the user.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

import os
from dotenv import load_dotenv

load_dotenv

OPENAI_KEY = os.getenv("OPENAI_KEY")

model = ChatOpenAI(api_key=OPENAI_KEY, model="gpt-3.5-turbo")

config = {"configurable": {"thread_id": "abc123"}}


def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}


def initate_workflow():

    workflow = StateGraph(state_schema=MessagesState)
    workflow.add_edge(START, "model")
    workflow.add_node("model", call_model)

    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app


if __name__ == "__main__":
    app = initate_workflow()
    print("Welcome to this AI chatbot!\nTo begin chatting write in the line below and press enter.\n")
    while True:
        query = input()
        if query == "quit":
            break
        input_messages = [HumanMessage(query)]
        response = app.invoke({"messages": input_messages}, config)
        response["messages"][-1].pretty_print()
