from datetime import date
import logging
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
from . import utils

logger = logging.getLogger(__name__)


class CFPBComplaintReader(BaseReader):
    BASE_URL = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"
    SORT = "created_date_asc"
    NO_AGGS = "false"
    NO_HIGHLIGHTS = "false"
    CONSUMER_CONSENT_PROVIDED = "Consent provided"
    HAS_NARRATIVE = "true"
    FORMAT = "json"

    def __init__(
        self,
        companies: list[str] | None = None,
        start_date_YYYY_MM_DD: str | None = None,
        end_date_YYYY_MM_DD: str | None = None,
        verbose: bool = False,
    ):
        self.verbose = verbose

        today = date.today()

        if start_date_YYYY_MM_DD is None:
            start_date_YYYY_MM_DD = f"{today.year}-01-01"
            self._log(f"Using default start_date: {start_date_YYYY_MM_DD}")

        if end_date_YYYY_MM_DD is None:
            end_date_YYYY_MM_DD = today.isoformat()
            self._log(f"Using default end_date: {end_date_YYYY_MM_DD}")

        if not companies:
            self._log("No companies provided → fetching all companies")

        self.companies = companies or []
        self.start_date = utils.validate_date(start_date_YYYY_MM_DD)
        self.end_date = utils.validate_date(end_date_YYYY_MM_DD)

        if self.start_date > self.end_date:
            raise ValueError("start_date must be <= end_date")

    def _log(self, message: str):
        if self.verbose:
            logger.info(message)

    def load_data(self) -> list[Document]:
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

        if self.companies:
            self._log(f"Fetching complaints for {len(self.companies)} company batch(es)")

            for i, company in enumerate(self.companies, start=1):
                p = params.copy()
                p["company"] = company.upper()

                self._log(f"Batch {i}/{len(self.companies)}: fetching company={company}")

                items = utils.make_request(self.BASE_URL, p)
                self._log(f"Batch {i}/{len(self.companies)} returned {len(items)} records")

                results.extend(items)
        else:
            self._log("Batch 1/1: fetching complaints for ALL companies")

            items = utils.make_request(self.BASE_URL, params)
            self._log(f"Batch 1/1 returned {len(items)} records")

            results.extend(items)

        documents = []

        for res in results:
            complaint_text = res.get("complaint_what_happened")
            if not complaint_text:
                continue

            text = (
                f"Company: {res.get('company')}\n"
                f"Product: {res.get('product')}\n"
                f"Issue: {res.get('issue')}\n\n"
                f"{complaint_text}"
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

        self._log(f"Converted {len(documents)} records into LlamaIndex documents")

        return documents