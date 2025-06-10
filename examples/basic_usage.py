from markdown2pdf import MarkdownPDF

def pay(offer):
    print("⚡ Lightning payment required")
    print(f"Amount: {offer['amount']} {offer['currency']}")
    print(f"Description: {offer['description']}")
    print(f"Invoice: {offer['payment_request']}")
    input("Press Enter once paid...")

client = MarkdownPDF(on_payment_request=pay, verify_ssl=False)
url = client.convert(markdown="# Hello markdown2pdf sync", title="My document title", date="5th June 2025" ) # Replace with your own unique markdown content to ensure you trigger L402.
print("PDF URL:", url)
