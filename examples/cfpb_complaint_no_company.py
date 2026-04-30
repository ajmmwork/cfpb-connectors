import os
import time
import logging
from getpass import getpass

from cfpb.complaints import CFPBComplaintReader
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

logging.basicConfig(level=logging.INFO)

api_key = getpass("Enter your OPENAI_API_KEY: ")
os.environ["OPENAI_API_KEY"] = api_key

llm = OpenAI(model="gpt-4.1-mini", api_key=api_key)
embed_model = OpenAIEmbedding(
    model="text-embedding-3-small",
    api_key=api_key,
)

reader = CFPBComplaintReader(
    start_date_YYYY_MM_DD="2025-01-01",
    end_date_YYYY_MM_DD="2025-01-31",
    verbose=True,
)

docs = reader.load_data()
print(f"Loaded {len(docs)} documents")

# Optional for testing
# docs = docs[:200]

BATCH_SIZE = 10000
SLEEP_SECONDS = 1

index = None
total_batches = (len(docs) + BATCH_SIZE - 1) // BATCH_SIZE

for i in range(0, len(docs), BATCH_SIZE):
    batch = docs[i:i + BATCH_SIZE]
    batch_num = (i // BATCH_SIZE) + 1

    logging.info(f"Embedding batch {batch_num}/{total_batches}: {len(batch)} docs")

    if index is None:
        index = VectorStoreIndex.from_documents(
            batch,
            embed_model=embed_model,
        )
    else:
        for doc in batch:
            index.insert(doc)

    time.sleep(SLEEP_SECONDS)

if index is None:
    raise ValueError("No documents were loaded, so no index could be created.")

query_engine = index.as_query_engine(llm=llm)

response = query_engine.query("What are common issues customers report?")

print("\nResponse:\n")
print(response)