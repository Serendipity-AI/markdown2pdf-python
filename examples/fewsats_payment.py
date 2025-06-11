from markdown2pdf import MarkdownPDF
from dotenv import load_dotenv
from fewsats.core import *
import json
load_dotenv()
fs = Fewsats()
# In your .env file, ensure you have set the following. You can learn more about fewsats at https://fewsats.com.
# FEWSATS_API_KEY = <your_fewsats_api_key>

def pay(offer):
    print("Paying using Fewsats:")
    print(offer)
    r = fs.pay_lightning(invoice=offer["payment_request"], amount=offer["amount"], currency=offer["currency"], description=offer["description"])
    print(f"Payment made: {r.json()}")

client = MarkdownPDF(on_payment_request=pay)
path = client.convert(markdown="# Save this one using Fewsats", download_path="output.pdf") # Replace with your own unique markdown content to ensure you trigger L402.
print("Saved PDF to:", path)
