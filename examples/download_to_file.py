from markdown2pdf import MarkdownPDF

def pay(offer):
    print("Paying manually:")
    print(offer["payment_request"])
    input("Press Enter when paid...")

client = MarkdownPDF(on_payment_request=pay)
path = client.convert(markdown="# Save this one 12345", download_path="output.pdf") # Replace with your own unique markdown content to ensure you trigger L402.
print("Saved PDF to:", path)
