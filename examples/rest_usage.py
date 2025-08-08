import httpx
import time
from datetime import datetime
from urllib.parse import urljoin

DEFAULT_API_URL = "https://api.markdown2pdf.ai"
POLL_INTERVAL = 3
MAX_DOC_GENERATION_POLLS = 10

def build_url(path, base_url):
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return urljoin(base_url, path)

def pay(offer):
    print("⚡ Lightning payment required")
    print(f"Amount: {offer['amount']} {offer['currency']}")
    print(f"Description: {offer['description']}")
    print(f"Invoice: {offer['payment_request']}")
    input("Press Enter once paid...")

def convert(markdown, title="Markdown2PDF.ai converted document", date=None, download_path=None, return_bytes=False, on_payment_request=pay, api_url=DEFAULT_API_URL):
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

    with httpx.Client() as client:
        while True:
            print("Sending initial request to convert markdown...")
            response = client.post(f"{api_url}/markdown", json=payload)

            if response.status_code == 402:
                print("Received 402 Payment Required response, fetching payment offer...")
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

                invoice_resp = client.post(offer["payment_request_url"], json={
                    "offer_id": offer["offer_id"],
                    "payment_context_token": offer["payment_context_token"],
                    "payment_method": "lightning"
                })

                if not invoice_resp.is_success:
                    raise Exception(f"Failed to fetch invoice: {invoice_resp.status_code}")

                invoice_data = invoice_resp.json()
                offer["payment_request"] = invoice_data["payment_request"]["payment_request"]

                if not on_payment_request:
                    raise Exception("Payment required but no handler provided.")

                print("Prompting for payment...")
                on_payment_request(offer)

                time.sleep(POLL_INTERVAL)
                continue

            if not response.is_success:
                raise Exception(f"Initial request failed: {response.status_code}, {response.text}")

            response_data = response.json()
            path = response_data["path"]
            break

        status_url = build_url(path, api_url)
        attempt = 0
        print("Polling for document generation status...")
        while attempt < MAX_DOC_GENERATION_POLLS:
            poll_resp = client.get(status_url)
            if poll_resp.status_code != 200:
                raise Exception(f"Polling error (status {poll_resp.status_code})")

            poll_data = poll_resp.json()
            if poll_data.get("status") == "Done":
                final_metadata_url = poll_data.get("path")
                if not final_metadata_url:
                    raise Exception("Missing 'path' field pointing to final metadata.")

                metadata_resp = client.get(final_metadata_url)
                if not metadata_resp.is_success:
                    raise Exception("Failed to retrieve metadata at final path.")

                final_data = metadata_resp.json()
                if "url" not in final_data:
                    raise Exception("Missing final download URL in metadata response.")

                final_download_url = final_data["url"]
                break

            time.sleep(POLL_INTERVAL)
            attempt += 1
        else:
            raise Exception(f"Polling exceeded max attempts ({MAX_DOC_GENERATION_POLLS}) without completion.")

        print("Downloading final PDF...")
        pdf_resp = client.get(final_download_url)
        if not pdf_resp.is_success:
            raise Exception("Failed to download final PDF.")

        pdf_content = pdf_resp.content

    if return_bytes:
        return pdf_content

    if download_path:
        with open(download_path, "wb") as f:
            f.write(pdf_content)
        return download_path

    return final_download_url

# Example usage
if __name__ == "__main__":
    url = convert(
        markdown="# Hello markdown2pdf REST APIs",
        title="My document title",
        date="5th June 2025"
    )
    print("PDF URL:", url)