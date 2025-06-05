
from markdown2pdf import MarkdownPDF

def pay(offer):
    print("Paying manually:")
    print(offer["payment_request"])
    input("Press Enter when paid...")

client = MarkdownPDF(on_payment_request=pay)
path = client.convert("# Save this one", download_path="output.pdf")
print("Saved PDF to:", path)
