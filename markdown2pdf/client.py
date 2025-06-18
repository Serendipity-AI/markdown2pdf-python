import asyncio
import httpx
import time
import inspect
from datetime import datetime, timezone
from urllib.parse import urljoin
from datetime import datetime
from .exceptions import PaymentRequiredException, Markdown2PDFException

DEFAULT_API_URL = "https://api.markdown2pdf.ai" # URL of the markdown2pdf.ai API
POLL_INTERVAL = 3 # Time in seconds to wait between polling requests
MAX_DOC_GENERATION_POLLS = 10 # Maximum number of times to wait for a document to be generated before giving up

class AsyncMarkdownPDF:
    def __init__(self, api_url=DEFAULT_API_URL, on_payment_request=None, poll_interval=POLL_INTERVAL):
        self.api_url = api_url
        self.on_payment_request = on_payment_request
        self.poll_interval = poll_interval

    async def convert(self, markdown, date=None, title="Markdown2PDF.ai converted document", download_path=None, return_bytes=False):
        
        if not date:
            dt = datetime.now()
            date = f"{dt.day} {dt.strftime('%B %Y')}" # Nicely formatted today's date
        
        # Assemble payload for the /markdown endpoint
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

        async with httpx.AsyncClient() as client:
            while True:
                response = await client.post(f"{self.api_url}/v1/markdown", json=payload)

                if response.status_code == 402: # L402 Payment Required
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
                    invoice_resp = await client.post(offer["payment_request_url"], json={
                        "offer_id": offer["offer_id"],
                        "payment_context_token": offer["payment_context_token"],
                        "payment_method": "lightning"
                    })

                    if not invoice_resp.is_success:
                        raise Markdown2PDFException(f"Failed to fetch invoice: {invoice_resp.status_code}")

                    invoice_data = invoice_resp.json()
                    offer["payment_request"] = invoice_data["payment_request"]["payment_request"]

                    if not self.on_payment_request:
                        raise PaymentRequiredException("Payment required but no handler provided.")
                    
                    if inspect.iscoroutinefunction(self.on_payment_request):
                        await self.on_payment_request(offer)
                    else:
                        self.on_payment_request(offer)

                    await asyncio.sleep(self.poll_interval)
                    continue

                if not response.is_success:
                    raise Markdown2PDFException(f"Initial request failed: {response.status_code}, {response.text}")

                response_data = response.json()
                path = response_data["path"]
                break

            # Request document now payment has been made
            status_url = self._build_url(path)
            attempt = 0

            while attempt < MAX_DOC_GENERATION_POLLS:
                poll_resp = await client.get(status_url)
                if poll_resp.status_code != 200:
                    raise Markdown2PDFException(f"Polling error (status {poll_resp.status_code})")

                poll_data = poll_resp.json()
                if poll_data.get("status") == "Done":
                    final_metadata_url = poll_data.get("path")
                    if not final_metadata_url:
                        raise Markdown2PDFException("Missing 'path' field pointing to final metadata.")

                    metadata_resp = await client.get(final_metadata_url)
                    if not metadata_resp.is_success:
                        raise Markdown2PDFException("Failed to retrieve metadata at final path.")

                    final_data = metadata_resp.json()
                    if "url" not in final_data:
                        raise Markdown2PDFException("Missing final download URL in metadata response.")

                    final_download_url = final_data["url"]
                    break

                await asyncio.sleep(self.poll_interval)
                attempt += 1
            else:
                raise Markdown2PDFException(f"Polling exceeded max attempts ({MAX_DOC_GENERATION_POLLS}) without completion.")


            # Download the final PDF
            pdf_resp = await client.get(final_download_url)
            if not pdf_resp.is_success:
                raise Markdown2PDFException("Failed to download final PDF.")

            pdf_content = pdf_resp.content

        if return_bytes:
            return pdf_content

        if download_path:
            with open(download_path, "wb") as f:
                f.write(pdf_content)
            return download_path

        return final_download_url

    def _build_url(self, path):
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return urljoin(self.api_url, path)


class MarkdownPDF:
    """Synchronous wrapper for AsyncMarkdownPDF"""
    
    def __init__(self, api_url=DEFAULT_API_URL, on_payment_request=None, poll_interval=POLL_INTERVAL):
        self.async_client = AsyncMarkdownPDF(api_url, on_payment_request, poll_interval)

    def convert(self, markdown, date=None, title="Markdown2PDF.ai converted document", download_path=None, return_bytes=False):
        """Synchronous wrapper for the async convert method"""
        return asyncio.run(
            self.async_client.convert(markdown, date, title, download_path, return_bytes)
        )