from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
from . import utils


class CFPBComplaintReader(BaseReader):
    """
    Reader for fetching CFPB (Consumer Financial Protection Bureau) complaint data.

    This reader retrieves complaint narratives from the CFPB API for given companies
    within a specified date range and converts them into LlamaIndex `Document` objects.

    Each document contains:
    - text: complaint narrative (optionally prefixed with company/product/issue)
    - metadata: structured complaint attributes (company, product, issue, etc.)

    Example:
        reader = CFPBComplaintReader(
            companies=["BANK OF AMERICA, NATIONAL ASSOCIATION"],
            start_date_YYYY_MM_DD="2025-01-01",
            end_date_YYYY_MM_DD="2025-01-31",
        )

        documents = reader.load_data()
    """

    BASE_URL = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"
    SORT = "created_date_asc"
    NO_AGGS = "false"
    NO_HIGHLIGHTS = "false"
    CONSUMER_CONSENT_PROVIDED = "Consent provided"
    HAS_NARRATIVE = "true"
    FORMAT = "json"

    def __init__(
        self,
        companies: list[str],
        start_date_YYYY_MM_DD: str,
        end_date_YYYY_MM_DD: str,
    ):
        """
        Initialize the CFPBComplaintReader.

        Args:
            companies (list[str]):
                List of company names to query (e.g., ["BANK OF AMERICA, NATIONAL ASSOCIATION"]).

            start_date_YYYY_MM_DD (str):
                Start date (inclusive) in format YYYY-MM-DD.

            end_date_YYYY_MM_DD (str):
                End date (inclusive) in format YYYY-MM-DD.

        Raises:
            ValueError:
                If required parameters are missing or date range is invalid.
        """

        missing = []

        if not companies:
            missing.append("companies")
        if not start_date_YYYY_MM_DD:
            missing.append("start_date_YYYY_MM_DD")
        if not end_date_YYYY_MM_DD:
            missing.append("end_date_YYYY_MM_DD")

        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")

        self.companies = companies
        self.start_date = utils.validate_date(start_date_YYYY_MM_DD)
        self.end_date = utils.validate_date(end_date_YYYY_MM_DD)

        if self.start_date > self.end_date:
            raise ValueError(
                "start_date_YYYY_MM_DD must be before or equal to end_date_YYYY_MM_DD"
            )

    def load_data(self) -> list[Document]:
        """
        Fetch complaint data from the CFPB API and convert it into Document objects.

        Returns:
            list[Document]:
                A list of LlamaIndex Document objects containing complaint narratives
                and associated metadata.

        Raises:
            RuntimeError:
                If the API request fails or returns an invalid response.
        """

        params = {
            "date_received_min": self.start_date,
            "date_received_max": self.end_date,
            "format": self.FORMAT,
            "sort": self.SORT,
            "no_aggs": self.NO_AGGS,
            "no_highlights": self.NO_HIGHLIGHTS,
            "consumer_consent_provided": self.CONSUMER_CONSENT_PROVIDED,
            "has_narrative": self.HAS_NARRATIVE,
        }

        results = []
        for c in self.companies:
            p = params.copy()
            p["company"] = c.upper()
            items = utils.make_request(self.BASE_URL, p)
            results.extend(items)

        documents = []
        for res in results:
            text = res.get("complaint_what_happened")
            if not text:
                continue

            text = (
                f"Company: {res.get('company')}\n"
                f"Product: {res.get('product')}\n"
                f"Issue: {res.get('issue')}\n\n"
                f"{text}"
            )

            metadata = {
                "complaint_id": res.get("complaint_id"),
                "product": res.get("product"),
                "date_sent_to_company": utils.date_only(res.get("date_sent_to_company")),
                "issue": res.get("issue"),
                "sub_product": res.get("sub_product"),
                "zip_code": res.get("zip_code"),
                "tags": res.get("tags"),
                "timely": res.get("timely"),
                "consumer_consent_provided": res.get("consumer_consent_provided"),
                "company_response": res.get("company_response"),
                "submitted_via": res.get("submitted_via"),
                "company": res.get("company"),
                "date_received": utils.date_only(res.get("date_received")),
                "state": res.get("state"),
                "consumer_disputed": res.get("consumer_disputed"),
                "company_public_response": res.get("company_public_response"),
                "sub_issue": res.get("sub_issue"),
            }

            documents.append(
                Document(
                    text=text,
                    metadata=metadata,
                    doc_id=str(res.get("complaint_id")),
                )
            )

        return documents