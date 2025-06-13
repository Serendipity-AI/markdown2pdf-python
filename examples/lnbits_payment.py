from markdown2pdf import MarkdownPDF
import requests

LN_BITS_URL = "https://demo.lnbits.com/api/v1/payments"

ADMIN_KEY = "<your_lnbits_admin_key>"  # Replace with your LNbits admin key, see https://lnbits.com

def pay(offer):
    print("Paying using lnbits:")
    headers = {"X-Api-Key": ADMIN_KEY, "Content-Type": "application/json"}
    data = {
        "out": True,
        "bolt11": offer["payment_request"],
    }

    res = requests.post(LN_BITS_URL, json=data, headers=headers)
    res.raise_for_status()
    print("Payment status:", res)

client = MarkdownPDF(on_payment_request=pay)
path = client.convert(markdown="# Save this one using lnbits", download_path="output.pdf") # Replace with your own unique markdown content to ensure you trigger L402.
print("Saved PDF to:", path)
