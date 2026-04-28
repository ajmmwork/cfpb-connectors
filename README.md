# CFPB Connectors

A lightweight Python package for fetching Consumer Financial Protection Bureau (CFPB) data and converting it into LlamaIndex `Document` objects.

## Overview

`cfpb-connectors` provides reusable CFPB data connectors for retrieval-augmented generation (RAG), semantic search, data analysis pipelines, and LLM-powered applications.

Currently supported:

- CFPB consumer complaints

Planned future connectors:

- Mortgages
- Credit cards
- Loans
- Additional CFPB datasets

## Installation

### Development install

Use this while actively developing the package:

```bash
pip install -e .
```

The `-e` means editable install. Code changes update immediately without reinstalling.

### Future published install

Once published to PyPI, users will install with:

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
)

documents = reader.load_data()

print(len(documents))
print(documents[0].text)
print(documents[0].metadata)
```
## Basic RAG Pipeline Example
```bash
pip install llama-index-llms-openai llama-index-embeddings-openai
python3 examples/fpb_complaint_reader_basic_usage.py
```
## Date Format

Dates must use ISO format:

```text
YYYY-MM-DD
```

Example:

```python
start_date_YYYY_MM_DD="2025-01-01"
end_date_YYYY_MM_DD="2025-01-31"
```

## Document Structure

Each CFPB complaint is converted into a LlamaIndex `Document`.

### Text

The document text contains the complaint narrative, prefixed with basic context:

```text
Company: BANK OF AMERICA, NATIONAL ASSOCIATION
Product: Checking or savings account
Issue: Managing an account

<complaint narrative>
```

### Metadata

Each document includes structured metadata:

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

The connector raises clear exceptions when:

- Required parameters are missing
- Dates are invalid or incorrectly formatted
- The start date is after the end date
- The CFPB API request fails
- The CFPB API returns an unexpected response

Example:

```text
ValueError: Invalid date '2025-13-01'. Expected format YYYY-MM-DD
```

## Development

Recommended project structure:

```text
cfpb-reader/
├── README.md
├── pyproject.toml
├── src/
│   └── cfpb/
│       ├── __init__.py
│       └── complaints/
│           ├── __init__.py
│           ├── reader.py
│           └── utils.py
└── tests/
```

## Notes

- Only complaints with consumer-provided narratives are returned.
- This package currently depends on `llama-index-core` and `requests`.

## Roadmap

Potential future improvements:

- Additional CFPB endpoint connectors
- Additional complaint filters, such as product, issue, state, and ZIP code
- PyPI publishing

## License

MIT
