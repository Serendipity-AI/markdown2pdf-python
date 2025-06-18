from openai import OpenAI
import os
import random
from markdown2pdf import MarkdownPDF
from dotenv import load_dotenv
from pyalby import Account, Invoice, Payment

load_dotenv()
# In your .env file, ensure you have set the following. You can learn more about alby at https://albyhub.com.
# BASE_URL = https://api.getalby.com
# ALBY_ACCESS_TOKEN = <your_alby_access_token>
# LOG_LEVEL = INFO
# OPENAI_API_KEY = <your_openai_api_key>
openai_client = OpenAI() 

def generate_random_markdown(topic=None):
    if topic is None:
        topic = random.choice([
            "How to Brew the Perfect Cup of Coffee",
            "Beginner's Guide to Python",
            "A Travelogue on Iceland",
            "The History of the Internet",
            "Understanding Quantum Mechanics",
            "The jazz music of Herbie Hancock",
            "Bitcoin and the Future of Money",
            "Future payment protocols for AI agents",
            "Living in Primrose Hill",
            "Einsteins Theory of Relativity",
            "Learning simple Chinese phrases",
        ])

    prompt = f"""
You are a Markdown-savvy technical writer.
Write a simple and well-formatted markdown document on the topic: **{topic}**.
Include:
- Headings
- Bullet points (be use to have a blank line prior to the first bullet point)
- Numbered lists (be use to have a blank line prior to the first bullet point)
- Blockquotes
- Emphasis (bold/italic)
- Emjois
- Code blocks if appropriate,
- Formulae/equations if appropriate. Be sure to use markdown syntax, for example:
  $$
  E = mc^2 
  $$
  For inline equations or math formatting, use:
  $E = mc^2$
  If you are listing bullet points after a Where clause, use a blank line before the first bullet point.
- Images using links to images you know exist online
- Hyperlinks

Do not prefix or suffix the content with any additional text; be sure to ONLY output markdown content.
NEVER enclose the markdown content in triple backticks or any other code block format.
Be very verbose, we are aiming for a lot of content.
Start now.
"""

    response = openai_client.chat.completions.create(model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful Markdown generator."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.1,
    max_tokens=16000)

    markdown_text = response.choices[0].message.content
    return markdown_text

if __name__ == "__main__":

    md = generate_random_markdown()
    print(f"Generated Markdown Content: {md}")

    def pay(offer):
        print("Paying using Alby:")
        payment = Payment()
        pay = payment.bolt11_payment(offer["payment_request"])
        print(f"Payment made: {pay}")

    client = MarkdownPDF(on_payment_request=pay)
    try: 
        path = client.convert(md, download_path=f"output.pdf")
        print("Saved PDF to:", path)
    except Exception as e:
        print(f"Error converting markdown to PDF for document: {e}")
