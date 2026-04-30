# CFPB Connectors

A lightweight Python package for fetching Consumer Financial Protection Bureau (CFPB) complaint data and converting it into LlamaIndex `Document` objects.

## Overview

`cfpb-connectors` provides reusable CFPB data connectors for RAG, semantic search, data analysis pipelines, and LLM-powered applications.

Currently supported:

- CFPB consumer complaints

## Installation

### Development install

```bash
pip install -e .
```

### Future published install

```bash
pip install cfpb-connectors
```

## Usage

```python
from cfpb.complaints import CFPBComplaintReader

reader = CFPBComplaintReader(
    companies=["BANK OF AMERICA, NATIONAL ASSOCIATION"],
    start_date_YYYY_MM_DD="2025-01-01",
    end_date_YYYY_MM_DD="2025-01-31",
    verbose=True,
)

documents = reader.load_data()

print(len(documents))
print(documents[0].text)
print(documents[0].metadata)
```

## Optional Parameters and Defaults

All parameters are optional.

Default behavior:

- If `companies` is missing → fetch all companies
- If `start_date_YYYY_MM_DD` is missing → defaults to Jan 1 of current year
- If `end_date_YYYY_MM_DD` is missing → defaults to today
- If `verbose=True` → logs execution details

Examples:

```python
# All companies, current year
CFPBComplaintReader(verbose=True)

# One company, default dates
CFPBComplaintReader(
    companies=["BANK OF AMERICA, NATIONAL ASSOCIATION"],
    verbose=True
)

# All companies, custom date range
CFPBComplaintReader(
    start_date_YYYY_MM_DD="2025-01-01",
    end_date_YYYY_MM_DD="2025-01-31",
    verbose=True
)

# One company, missing end date
CFPBComplaintReader(
    companies=["BANK OF AMERICA, NATIONAL ASSOCIATION"],
    start_date_YYYY_MM_DD="2025-01-01",
    verbose=True
)
```

## Basic RAG Pipeline Example

Install dependencies:

```bash
pip install llama-index-llms-openai llama-index-embeddings-openai
```

Run example:

```bash
python3 -m examples.cfpb_complaint_all_parameters
```

### Batching (Recommended for Large Data)

```python
import time
import logging
from llama_index.core import VectorStoreIndex

BATCH_SIZE = 100
SLEEP_SECONDS = 1

index = None
total_batches = (len(documents) + BATCH_SIZE - 1) // BATCH_SIZE

for i in range(0, len(documents), BATCH_SIZE):
    batch = documents[i:i + BATCH_SIZE]
    batch_num = (i // BATCH_SIZE) + 1

    logging.info(f"Embedding batch {batch_num}/{total_batches}: {len(batch)} docs")

    if index is None:
        index = VectorStoreIndex.from_documents(batch, embed_model=embed_model)
    else:
        for doc in batch:
            index.insert(doc)

    time.sleep(SLEEP_SECONDS)
```

## Date Format

```text
YYYY-MM-DD
```

## Document Structure

### Text

```
Company: BANK OF AMERICA, NATIONAL ASSOCIATION
Product: Checking or savings account
Issue: Managing an account

<complaint narrative>
```

### Metadata

```python
{
    "complaint_id": "11578145",
    "company": "BANK OF AMERICA, NATIONAL ASSOCIATION",
    "product": "Checking or savings account",
    "sub_product": "Checking account",
    "issue": "Managing an account",
    "sub_issue": "...",
    "date_received": "2025-01-16",
    "date_sent_to_company": "2025-01-16",
    "state": "VA",
    "zip_code": "24012",
    "submitted_via": "Web",
    "company_response": "Closed with explanation",
    "company_public_response": "...",
    "consumer_consent_provided": "Consent provided",
    "consumer_disputed": "N/A",
    "timely": "Yes",
    "tags": None
}
```

## Error Handling

The connector raises errors when:

- Dates are invalid
- Start date > end date
- API request fails
- API response is malformed

Example:

```
ValueError: Invalid date '2025-13-01'. Expected format YYYY-MM-DD
```

## Notes

- Only complaints with narratives are returned
- No embedding or batching is handled in this package
- Those belong in the application layer

## Roadmap

- More CFPB datasets
- Additional filters (product, issue, state, ZIP)
- PyPI publishing
- LlamaHub integration

## License

MIT