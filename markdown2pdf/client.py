import asyncio
import aiohttp
import ssl
import time
import inspect
from datetime import datetime, timezone
from urllib.parse import urljoin
from datetime import datetime
from .exceptions import PaymentRequiredException, Markdown2PDFException

DEFAULT_API_URL = "https://api.markdown2pdf.ai"
POLL_INTERVAL = 3

class AsyncMarkdownPDF:
    def __init__(self, api_url=DEFAULT_API_URL, on_payment_request=None, poll_interval=POLL_INTERVAL, verify_ssl=True):
        self.api_url = api_url
        self.on_payment_request = on_payment_request
        self.poll_interval = poll_interval
        self.verify_ssl = verify_ssl

    async def convert(self, markdown, date=None, title="Markdown2PDF.ai converted document", download_path=None, return_bytes=False):
        
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

        # Configure SSL context
        ssl_context = None
        if not self.verify_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            while True:
                async with session.post(f"{self.api_url}/v1/markdown", json=payload) as response:
                    if response.status == 402:
                        l402_offer = await response.json()
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
                        async with session.post(offer["payment_request_url"], json={
                            "offer_id": offer["offer_id"],
                            "payment_context_token": offer["payment_context_token"],
                            "payment_method": "lightning"
                        }) as invoice_resp:
                            if not invoice_resp.ok:
                                raise Markdown2PDFException(f"Failed to fetch invoice: {invoice_resp.status}")

                            invoice_data = await invoice_resp.json()
                            offer["payment_request"] = invoice_data["payment_request"]["payment_request"]

                        if not self.on_payment_request:
                            raise PaymentRequiredException("Payment required but no handler provided.")
                        
                        # Handle both sync and async payment handlers
                        if inspect.iscoroutinefunction(self.on_payment_request):
                            await self.on_payment_request(offer)
                        else:
                            self.on_payment_request(offer)

                        await asyncio.sleep(self.poll_interval)
                        continue

                    if not response.ok:
                        response_text = await response.text()
                        raise Markdown2PDFException(f"Initial request failed: {response.status}, {response_text}")

                    response_data = await response.json()
                    path = response_data["path"]
                    break

            # Step 1: Poll until status is "Done"
            status_url = self._build_url(path)
            while True:
                async with session.get(status_url) as poll_resp:
                    if poll_resp.status != 200:
                        raise Markdown2PDFException("Polling error")

                    poll_data = await poll_resp.json()
                    if poll_data.get("status") != "Done":
                        await asyncio.sleep(self.poll_interval)
                        continue

                    # Step 2: Use the returned 'path' field to retrieve final metadata
                    final_metadata_url = poll_data.get("path")
                    if not final_metadata_url:
                        raise Markdown2PDFException("Missing 'path' field pointing to final metadata.")

                    async with session.get(final_metadata_url) as metadata_resp:
                        if not metadata_resp.ok:
                            raise Markdown2PDFException("Failed to retrieve metadata at final path.")

                        final_data = await metadata_resp.json()
                        if "url" not in final_data:
                            raise Markdown2PDFException("Missing final download URL in metadata response.")

                        final_download_url = final_data["url"]
                        break

            # Step 3: Download the actual PDF
            async with session.get(final_download_url) as pdf_resp:
                if not pdf_resp.ok:
                    raise Markdown2PDFException("Failed to download final PDF.")

                pdf_content = await pdf_resp.read()

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
    
    def __init__(self, api_url=DEFAULT_API_URL, on_payment_request=None, poll_interval=POLL_INTERVAL, verify_ssl=True):
        self.async_client = AsyncMarkdownPDF(api_url, on_payment_request, poll_interval, verify_ssl)

    def convert(self, markdown, date=None, title="Markdown2PDF.ai converted document", download_path=None, return_bytes=False):
        """Synchronous wrapper for the async convert method"""
        return asyncio.run(
            self.async_client.convert(markdown, date, title, download_path, return_bytes)
        )