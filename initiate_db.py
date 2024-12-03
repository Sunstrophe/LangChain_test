"""
This file intend to embed data into a vector database.
"""
import xml.etree.ElementTree as ET
from lxml import etree
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from uuid import uuid4
from collections import Counter
import re

import os
from dotenv import load_dotenv

import logging

logging.basicConfig(
    level=logging.ERROR,
    encoding="utf8",
    format="%(levelname)s:%(message)s"
)


load_dotenv

OPENAI_KEY = os.getenv("OPENAI_KEY")

embeddings = OpenAIEmbeddings(
    api_key=OPENAI_KEY, model="text-embedding-3-large")

xml_path = "xml_files/uespwiki-2024-10-17-current.xml"


def clean_text(text: str) -> str:
    text = re.sub(r"{{Lore Link\|([^}]+)}}", r'\1', text)
    text = re.sub(r"\{\{[Ss]ic\|([^|]+)\|.*?\}\}", r'\1', text)
    text = re.sub(r"\[\[Lore:[^\|]+\|([^]]+)\]\]", r"\1", text)
    text = re.sub(r"{{Book Footer}}", "", text)
    text = re.sub(r"{{Book End}}", "", text)
    text = re.sub(r"<.*?>", "", text)
    return text.strip()


def clean_title(text: str) -> str:
    text = re.sub(r"Lore:", "", text)
    return text.strip()


def load_db(vector_store: Chroma, documents):
    logging.debug("Starting embedding!")
    print("Starting embedding!")

    uuids = [str(uuid4()) for _ in range(len(documents))]

    vector_store.add_documents(documents=documents, ids=uuids)

    print("Embed complete!")
    logging.debug("Embed complete!")


def initate_db():
    logging.debug("Creating database")

    vector_store = Chroma(
        collection_name="uesp_database",
        embedding_function=embeddings,
        persist_directory="./uesp_db"
    )
    return vector_store


def identify_tags(file_path):
    tag_counter = Counter()

    context = etree.iterparse(file_path, events=("start",))

    for event, element in context:
        tag_counter[element.tag] += 1
        element.clear

    return tag_counter


def parse_xml(file_path):
    context = ET.iterparse(file_path, events=("start", "end"))
    current_page = {}
    namespace = "{http://www.mediawiki.org/xml/export-0.10/}"
    elements = []

    for event, element in context:
        if event == "start" and element.tag == f"{namespace}page":
            current_page = {"title": None, "content": None, "description": ""}

        if event == "start" and element.tag == f"{namespace}title" and current_page is not None:
            if element.text and "Lore:" in element.text.strip():
                current_page["title"] = clean_title(element.text)

        if event == "start" and element.tag == f"{namespace}text" and current_page is not None:
            if element.text and "{{Lore Book" in element.text:

                current_page["description"] = re.sub(
                    # r".*\|description=([^|]+).*", r"\1", element.text, flags=re.DOTALL)
                    r"\{\{Lore Book[\s\S]*?\|description=([^\n|]+).*", r"\1", element.text, flags=re.DOTALL)
                content = re.sub(
                    r"\{\{Lore Book[\s\S]*?\}\}", "", element.text).strip()
                current_page["content"] = clean_text(content)

        if event == "end" and element.tag == f"{namespace}page" and current_page is not None:
            if current_page["title"] and current_page["content"]:
                elements.append(current_page)
            # Reset for next page
            current_page = None
            element.clear()
        element.clear()
    return elements


def parse_into_document(objects: list[dict]) -> list:
    documents = []
    for object in objects:
        document = Document(
            page_content=object["content"],
            metadata={
                "title": object["title"],
                "description": object["description"]
            }
        )
        documents.append(document)
    return documents


if __name__ == "__main__":
    vector_store = initate_db()
    data = parse_xml(xml_path)
    documents = parse_into_document(data)
    load_db(vector_store, documents)

    # tags = identify_tags(xml_path)
    # for tag, count in tags.items():
    #     print(f"{tag}: {count}")
