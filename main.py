"""
This file comprise the main functionality of this project

This project aims to create a tool calling agent with persistent memory to guide the user.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import create_react_agent
from tools import query_database

import os
from dotenv import load_dotenv

load_dotenv

OPENAI_KEY = os.getenv("OPENAI_KEY")

tools = [query_database]

model = ChatOpenAI(api_key=OPENAI_KEY, model="gpt-3.5-turbo")

model_with_tools = model.bind_tools(tools)

config = {"configurable": {"thread_id": "abc123"}}

memory = MemorySaver()

agent_executor = create_react_agent(model, tools, checkpointer=memory)


def call_agent(query):
    response = agent_executor.invoke(
        {"messages": [HumanMessage(content=query)]}, config)
    return response["messages"]

# def call_model(state: MessagesState):
#     response = model_with_tools.invoke(state["messages"])
#     if response.content:
#         return {"messages": response}
#     elif response.tool_calls:
#         agent_response = call_agent(response.tool_calls)
#     else:
#         return{"message": "There is something wrong with my AI"}


# def initate_workflow():

#     workflow = StateGraph(state_schema=MessagesState)
#     workflow.add_edge(START, "model")
#     workflow.add_node("model", call_model)

#     memory = MemorySaver()
#     app = workflow.compile(checkpointer=memory)

#     return app

def ui_query(message):
    response = call_agent(message)
    return response


def run():
    while True:
        query = input()
        if query == "quit":
            break
        response = call_agent(query)
        print(response)


if __name__ == "__main__":
    # app = initate_workflow()
    run()
