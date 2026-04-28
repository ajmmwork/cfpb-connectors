import os
from cfpb.complaints import CFPBComplaintReader
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from getpass import getpass

api_key = getpass("Enter your OPENAI_API_KEY: ")
os.environ["OPENAI_API_KEY"] = api_key

llm = OpenAI(model="gpt-4.1-mini")
embed_model = OpenAIEmbedding(model="text-embedding-3-small")

reader = CFPBComplaintReader(
    companies=["BANK OF AMERICA, NATIONAL ASSOCIATION"],
    start_date_YYYY_MM_DD="2025-01-01",
    end_date_YYYY_MM_DD="2025-01-31",
)

docs = reader.load_data()
print(f"Loaded {len(docs)} documents")


index = VectorStoreIndex.from_documents(
    docs,
    embed_model=embed_model,
)

query_engine = index.as_query_engine(llm=llm)


response = query_engine.query("What are common issues customers report?")
print("\nResponse:\n")
print(response)