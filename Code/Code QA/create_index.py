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

llm = OpenAI(model='gpt-4', temperature=0, max_tokens=256)

embed_model = OpenAIEmbedding()
node_parser = SimpleNodeParser.from_defaults(chunk_size=100, chunk_overlap=20)

documents = SimpleDirectoryReader(input_files=['ResponseGenerator.py']).load_data()

prompt_helper = PromptHelper(
  context_window=4096,
  num_output=512,
  chunk_overlap_ratio=0.1,
)

service_context = ServiceContext.from_defaults(
  llm=llm,
  embed_model=embed_model,
  node_parser=node_parser,
  prompt_helper=prompt_helper
)

# create storage context using default stores
storage_context = StorageContext.from_defaults(
    docstore=SimpleDocumentStore(),
    vector_store=SimpleVectorStore(),
    index_store=SimpleIndexStore(),
)

index = ListIndex.from_documents(documents, service_context = service_context, storage_context=storage_context)

# save index
index.storage_context.persist(persist_dir="storage")