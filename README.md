⚡ Markdown to PDF conversion, for agents. ⚡

**Agents speak Markdown. Humans prefer PDF.
Bridge the gap for the final stage of your agentic workflow.
No sign-ups, no credit cards, just sats for bytes.**

Read the full documentation at [markdown2pdf.ai](https://markdown2pdf.ai)

Here’s the output of a markdown file converted to PDF format, showing cover page, table of contents and table support. Our engine is powered by LaTeX rather than HTML to PDF conversion as many other libraries and services use, which results in a much higher quality, print-ready output.

<img src="images/examples.png" />

This package provides a python client for the markdown2pdf.ai service. You can read full instructions in [our documentation](https://markdown2pdf.ai).

## Installation

```
pip install markdown2pdf
```

## Usage

```python

from markdown2pdf import MarkdownPDF

def pay(offer):
    print("⚡ Lightning payment required")
    print(f"Amount: {offer['amount']} {offer['currency']}")
    print(f"Description: {offer['description']}")
    print(f"Invoice: {offer['payment_request']}")
    input("Press Enter once paid...")

client = MarkdownPDF(on_payment_request=pay)
path = client.convert("# Save this one", download_path="output.pdf")
print("Saved PDF to:", path)
```
