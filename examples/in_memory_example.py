from markdown2pdf import MarkdownPDF

def pay(offer):
    print("Pay invoice and press Enter:")
    print(offer["payment_request"])
    input()

client = MarkdownPDF(on_payment_request=pay)
pdf_bytes = client.convert(markdown="# Memory use case", return_bytes=True) # Replace with your own unique markdown content to ensure you trigger L402.
print(f"PDF size in memory: {len(pdf_bytes)} bytes")
