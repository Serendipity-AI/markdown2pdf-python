
from markdown2pdf import MarkdownPDF

def pay(offer):
    print("⚡ Lightning payment required")
    print(f"Amount: {offer['amount']} {offer['currency']}")
    print(f"Description: {offer['description']}")
    print(f"Invoice: {offer['payment_request']}")
    input("Press Enter once paid...")

client = MarkdownPDF(on_payment_request=pay)
url = client.convert("# Hello markdown2pdf")
print("PDF URL:", url)
