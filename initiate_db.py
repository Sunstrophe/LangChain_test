"""
This file intend to embed data into a vector database.
"""
from lxml import etree
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from uuid import uuid4

import os
from dotenv import load_dotenv

load_dotenv

OPENAI_KEY = os.getenv("OPENAI_KEY")

embeddings = OpenAIEmbeddings(
    api_key=OPENAI_KEY, model="text-embedding-3-large")

xml_path = "xml_files/uespwiki-2024-10-17-current.xml"


def process_xml(file_path) -> list:
    """
    Process an xml file into usable data chunks
    """
    tree = etree.parse(file_path)
    root = tree.getroot()

    data_chunks = []
    for element in root.iter():
        if element.text and element.text.strip():
            document = {
                "content": element.text.strip(),
                "metadata": {
                    "tag": element.tag,
                    "attributes": element.attrib
                }
            }
            data_chunks.append(document)
    return data_chunks


def load_db(vector_store: Chroma, data):
    uuids = [str(uuid4()) for _ in range(len(data))]
    vector_store.add_documents(documents=data, ids=uuids)


def initate_db():
    vector_store = Chroma(
        collection_name="uesp_database",
        embedding_function=embeddings,
        persist_directory="./uesp_db"
    )
    return vector_store


if __name__ == "__main__":
    vector_store = initate_db()
    data = process_xml(xml_path)
    load_db(vector_store, data)
