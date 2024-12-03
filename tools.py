"""
This file contains all of our tools.

Initially this will only contain the tool to query against a vector database
"""
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool

import os
from dotenv import load_dotenv

load_dotenv

OPENAI_KEY = os.getenv("OPENAI_KEY")

embeddings = OpenAIEmbeddings(
    api_key=OPENAI_KEY, model="text-embedding-3-large")


vector_store = Chroma(
    collection_name="uesp_database",
    embedding_function=embeddings,
    persist_directory="./uesp_db"
)


@tool
def query_database(query: str) -> str:
    """Query database for an answer"""
    results = vector_store.similarity_search(query, k=1)
    return f"* [{results[0].metadata}] {results[0].page_content}"


if __name__ == "__main__":
    query_database()
