from markdown2pdf import MarkdownPDF

def pay(offer):
    print("⚡ Lightning payment required")
    print(f"Amount: {offer['amount']} {offer['currency']}")
    print(f"Description: {offer['description']}")
    print(f"Invoice: {offer['payment_request']}")
    input("Press Enter once paid...")

client = MarkdownPDF(api_url="https://qa.api.markdown2pdf.ai", on_payment_request=pay)
url = client.convert("# Hello markdown2pdf") # Replace with your own unique markdown content to ensure you trigger L402.
print("PDF URL:", url)
