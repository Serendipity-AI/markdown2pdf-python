import time
import requests
from datetime import datetime, timezone
from urllib.parse import urljoin
from datetime import datetime
from .exceptions import PaymentRequiredException, Markdown2PDFException

DEFAULT_API_URL = "https://api.markdown2pdf.ai"
POLL_INTERVAL = 3
MAX_DOC_GENERATION_POLLS = 10 

class MarkdownPDF:
    def __init__(self, api_url=DEFAULT_API_URL, on_payment_request=None, poll_interval=POLL_INTERVAL):
        self.api_url = api_url
        self.on_payment_request = on_payment_request
        self.poll_interval = poll_interval

    def convert(self, markdown, date=None, title="Markdown2PDF.ai converted document", download_path=None, return_bytes=False):
        
        if not date:
            dt = datetime.now()
            date = f"{dt.day} {dt.strftime('%B %Y')}"
        
        payload = {
            "data": {
                "text_body": markdown,
                "meta": {
                    "title": title,
                    "date": date,
                }
            },
            "options": {
                "document_name": "converted.pdf"
            }
        }

        while True:
            response = requests.post(f"{self.api_url}/v1/markdown", json=payload)

            if response.status_code == 402:
                l402_offer = response.json()
                offer_data = l402_offer["offers"][0]
                offer = {
                    "offer_id": offer_data["id"],
                    "amount": offer_data["amount"],
                    "currency": offer_data["currency"],
                    "description": offer_data.get("description", ""),
                    "payment_context_token": l402_offer["payment_context_token"],
                    "payment_request_url": l402_offer["payment_request_url"]
                }

                # Get invoice
                invoice_resp = requests.post(offer["payment_request_url"], json={
                    "offer_id": offer["offer_id"],
                    "payment_context_token": offer["payment_context_token"],
                    "payment_method": "lightning"
                })

                if not invoice_resp.ok:
                    raise Markdown2PDFException(f"Failed to fetch invoice: {invoice_resp.status_code}")

                invoice_data = invoice_resp.json()
                offer["payment_request"] = invoice_data["payment_request"]["payment_request"]

                if not self.on_payment_request:
                    raise PaymentRequiredException("Payment required but no handler provided.")
                self.on_payment_request(offer)

                time.sleep(self.poll_interval)
                continue

            if not response.ok:
                raise Markdown2PDFException(f"Initial request failed: {response.status_code}, {response.text}")

            path = response.json()["path"]
            break

        status_url = self._build_url(path)
        attempt = 0

        while attempt < MAX_DOC_GENERATION_POLLS:
            poll_resp = requests.get(status_url)
            if poll_resp.status_code != 200:
                raise Markdown2PDFException(f"Polling error (status {poll_resp.status_code})")

            poll_data = poll_resp.json()
            if poll_data.get("status") == "Done":
                final_metadata_url = poll_data.get("path")
                if not final_metadata_url:
                    raise Markdown2PDFException("Missing 'path' field pointing to final metadata.")

                metadata_resp = requests.get(final_metadata_url)
                if not metadata_resp.ok:
                    raise Markdown2PDFException("Failed to retrieve metadata at final path.")

                final_data = metadata_resp.json()
                if "url" not in final_data:
                    raise Markdown2PDFException("Missing final download URL in metadata response.")

                final_download_url = final_data["url"]
                break

            time.sleep(self.poll_interval)
            attempt += 1
        else:
            raise Markdown2PDFException(f"Polling exceeded max attempts ({MAX_DOC_GENERATION_POLLS}) without completion.")

        # Step 3: Download the actual PDF
        pdf_resp = requests.get(final_download_url)
        if not pdf_resp.ok:
            raise Markdown2PDFException("Failed to download final PDF.")

        if return_bytes:
            return pdf_resp.content

        if download_path:
            with open(download_path, "wb") as f:
                f.write(pdf_resp.content)
            return download_path

        return final_download_url

    def _build_url(self, path):
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return urljoin(self.api_url, path)
