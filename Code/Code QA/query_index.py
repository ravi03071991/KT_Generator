from llama_index import ServiceContext, ListIndex, OpenAIEmbedding, PromptHelper, SimpleDirectoryReader
from llama_index.llms import OpenAI
import openai
from llama_index.langchain_helpers.text_splitter import TokenTextSplitter
from llama_index.node_parser import SimpleNodeParser
from llama_index import StorageContext, load_index_from_storage
from llama_index.storage.docstore import SimpleDocumentStore
from llama_index.storage.index_store import SimpleIndexStore
from llama_index.vector_stores import SimpleVectorStore
from llama_index.node_parser import SimpleNodeParser

openai.api_key = "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"

# to load index later, make sure you setup the storage context
# this will loaded the persisted stores from persist_dir
storage_context = StorageContext.from_defaults(persist_dir="storage")

# then load the index object
# if loading multiple indexes from a persist dir
loaded_index = load_index_from_storage(storage_context)

query = "what is prompt manager in the code?"
query_engine = loaded_index.as_query_engine(similarity_top_k=1)
response = query_engine.query(query)

# print the synthesized response.
print(response.response)