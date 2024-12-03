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


def clean_text(text):
    # 1. Remove templates like {{Lore Book|...}} and {{Lore Link|...}} while keeping content inside
    # Keep the part after the pipe in Lore Link
    text = re.sub(r'{{Lore Link\|([^|]+)\|([^}]+)}}', r'\2', text)
    text = re.sub(r'\[\[Lore:[^\|]+\|([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\[\[:File:[^\|]+\|[^\]]+\]\]', '', text)
    text = re.sub(r'\[\[File:[^\|]+\|[^\]]+\]\]', '', text)
    text = re.sub(r'MWlink=MW:', '', text)
    text = re.sub(r'\|lorenote[^\n]*', '', text)
    # Keep the content inside most other templates
    text = re.sub(r'{{[^|]*\|([^}]+)}}', r'\1', text)

    # 2. Remove other templates such as {{Nst|...}} or {{Lore Book|...}} but keep their inner content
    # Removes {{Nst|...}} completely
    text = re.sub(r'{{Nst\|[^}]*}}', '', text)
    # Removes {{Lore Book|...}} completely
    # text = re.sub(r'{{Lore Book[^}]*}}', '', text)

    text = re.sub(r'<[^>]*>', '', text)

    # 4. Remove unwanted newlines and spaces between sections for cleaner text
    # Reduce multiple newlines to a single one
    text = re.sub(r'\n+', '\n', text)
    # Remove newlines before a character (to join lines)
    text = re.sub(r'\n([^\n])', r' \1', text)

    # 5. Clean up stray punctuation (like extraneous quotes or single quotes that may appear)
    # Removes single and double quotes and newlines
    text = re.sub(r'[\'"\'\n]+', '', text)

    # 6. Optionally, strip extra spaces or fix spaces between text sections
    # Replace multiple spaces with a single space
    text = re.sub(r'\s{2,}', ' ', text)

    # 7. Clean up additional spaces or extra characters
    # Ensure no extra spaces around periods
    text = re.sub(r'\s*\.\s*', '.', text)
    # Remove spaces before punctuation like commas or semicolons
    text = re.sub(r'(\s+)[,;!?]', r'\1', text)

    # 8. Optional: remove "End" or other special words that might be in the text
    text = re.sub(r'-- End}}', '', text)  # Removes the "End" marker

    return text.strip()


def process_xml(file_path) -> list:
    """
    Process an xml file into usable data chunks
    """
    tree = etree.parse(file_path)
    root = tree.getroot()

    data_chunks = []
    i = 0
    # for element in root.iter():
    #     if element.text and element.text.strip():
    #         if i > 10:
    #             break
    #         print(type(element.tag))
    #         print(dict(element.attrib))
    #         i += 1

    for element in root.iter():
        if element.text and element.text.strip():
            document = Document(
                page_content=element.text.strip(),
                metadata={
                    "tag": element.tag
                }
            )
            data_chunks.append(document)
    logging.debug("Returning Datachunks")
    return data_chunks


def load_db(vector_store: Chroma, data):
    logging.debug("Starting embedding!")
    chunk_size = 100
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    for i, chunk in enumerate(chunks):
        uuids = [str(uuid4()) for _ in range(len(chunk))]
        vector_store.add_documents(documents=chunk, ids=uuids)
        print(f"\r|{i}/{len(chunks)} chunk/s completed!|", end="\r")
    logging.debug("Embed complete!")


def initate_db():
    logging.debug("Creating database")

    vector_store = Chroma(
        collection_name="uesp_database",
        embedding_function=embeddings,
        persist_directory="./uesp_db"
    )
    return vector_store


def find_element_on_tag(file_path, tag=""):
    context = etree.iterparse(file_path, events=("start", "end"))
    namespace = "{http://www.mediawiki.org/xml/export-0.10/}"
    elements = 0
    current_page = None
    i = 0

    for event, element in context:
        i += 1
        if element.tag == f"{namespace}page":
            current_page = {"title": None, "text": None}

        if element.tag == f"{namespace}title" and current_page is not None:
            if "Lore:" in element.text.strip():
                current_page["title"] = element.text.strip(
                ) if element.text else ""

        if element.tag == f"{namespace}text" and current_page is not None:
            if current_page["title"]:
                current_page["text"] = element.text.strip(
                ) if element.text else ""
                # elements.append(current_page)
                elements += 1
            current_page = None

        print(current_page)
        element.clear()

    # with open("test.txt", "w") as file:
    #     file.write("\n".join(elements))


def identify_tags(file_path):
    tag_counter = Counter()

    context = etree.iterparse(file_path, events=("start",))

    for event, element in context:
        tag_counter[element.tag] += 1
        element.clear

    return tag_counter


def find_element_on_tag2(file_path, tag=""):
    elements = []
    context = ET.iterparse(file_path, events=("start", "end"))
    current_page = None
    namespace = "{http://www.mediawiki.org/xml/export-0.10/}"
    # ignore_list = ["Lore:Places", ""]

    for event, element in context:
        if event == "start" and element.tag == f"{namespace}page":
            current_page = {"title": None, "text": None}

        if event == "start" and element.tag == f"{namespace}title" and current_page is not None:
            if element.text and "Lore:" in element.text.strip():
                current_page["title"] = element.text.strip()

        if event == "start" and element.tag == f"{namespace}text" and current_page is not None:
            if current_page["title"]:  # Ensure it's a page of interest
                current_page["text"] = element.text.strip(
                ) if element.text else ""

        if event == "end" and element.tag == f"{namespace}page" and current_page is not None:
            if current_page["title"]:  # Only save pages with the matching title
                elements.append(current_page)
            current_page = None  # Reset for the next page
            element.clear()  # Clear memory used by the page element
        # Free memory for all processed elements
        element.clear()
    return elements


def maintain_page(file_path):
    context = ET.iterparse(file_path, events=("start", "end"))
    current_page = {}
    namespace = "{http://www.mediawiki.org/xml/export-0.10/}"
    elements = []

    for event, element in context:
        if event == "start" and element.tag == f"{namespace}page":
            current_page = {"title": None, "content": []}

        if event == "start" and element.tag == f"{namespace}title" and current_page is not None:
            if element.text and "Lore:" in element.text.strip():
                current_page["title"] = element.text.strip()

        if event == "start" and element.tag == f"{namespace}text" and current_page is not None:
            if current_page["title"]:  # Ensure it's a page of interest
                current_page["content"].append(clean_text(element.text.strip(
                )) if element.text else "")

        if event == "end" and element.tag == f"{namespace}page" and current_page is not None:
            if current_page["title"]:
                elements.append(current_page)
            current_page = None  # Reset for the next page
            element.clear()  # Clear memory used by the page element

        # Free memory for all processed elements
        element.clear()
    print(elements[7])
    print(len(elements[7]))


if __name__ == "__main__":
    # vector_store = initate_db()
    # data = process_xml(xml_path)
    # load_db(vector_store, data)

    # tags = identify_tags(xml_path)
    # for tag, count in tags.items():
    #     print(f"{tag}: {count}")

    # find_element_on_tag(
    #     xml_path, "lore:")

    # elements = find_element_on_tag2(xml_path)
    # for i in range(1):
    #     print(elements[i])
    #     print("-"*20)

    maintain_page(xml_path)
