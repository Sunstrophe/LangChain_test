# Project GuidingAgent
This project aims to create a persistent chatbot to guide the user.
The chatbot should be capable of using a tool to search for an answer in a vector database.
Also included will be the embedding function to fill the vector database.

# Information
This project uses langchain, langgraph and langsmith.
The vector database I will use i ChromaDB since it comes included with its own module in langchain.
The information I intend to use is found on the UESP wiki, https://en.uesp.net/wiki/Main_Page.
Since they are kind enough to provide an xml file on their website.

# Set up tracing in langsmith:
https://docs.smith.langchain.com/observability/how_to_guides/tracing/trace_with_langchain
