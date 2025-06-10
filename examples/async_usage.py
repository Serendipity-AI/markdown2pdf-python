import asyncio
from markdown2pdf import AsyncMarkdownPDF

async def async_pay(offer):
    print("⚡ Lightning payment required")
    print(f"Amount: {offer['amount']} {offer['currency']}")
    print(f"Description: {offer['description']}")
    print(f"Invoice: {offer['payment_request']}")
    # You could add async payment processing here
    # For now, just simulate with async sleep
    await asyncio.sleep(0.1)
    input("Press Enter once paid...")

async def main():
    client = AsyncMarkdownPDF(on_payment_request=async_pay, verify_ssl=False)
    url = await client.convert(markdown="# Hello markdown2pdf async", title="My document title", date="5th June 2025")
    print("PDF URL:", url)

asyncio.run(main())