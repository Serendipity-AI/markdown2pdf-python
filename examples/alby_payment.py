from markdown2pdf import MarkdownPDF
from dotenv import load_dotenv
from pyalby import Account, Invoice, Payment

load_dotenv()
# In your .env file, ensure you have set the following. You can learn more about alby at https://albyhub.com.
# BASE_URL = https://api.getalby.com
# ALBY_ACCESS_TOKEN = <your_alby_access_token>
# LOG_LEVEL = INF

def pay(offer):
    print("Paying using Alby:")
    payment = Payment()
    pay = payment.bolt11_payment(offer["payment_request"])
    print(f"Payment made: {pay}")

client = MarkdownPDF(on_payment_request=pay)
path = client.convert("# Save this one using Alby", download_path="output.pdf") # Replace with your own unique markdown content to ensure you trigger L402.
print("Saved PDF to:", path)
