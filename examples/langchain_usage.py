import asyncio
from langchain.tools import tool
from dotenv import load_dotenv
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from markdown2pdf import AsyncMarkdownPDF

load_dotenv()

async def pay(offer):
    print("⚡ Lightning payment required")
    print(f"Amount: {offer['amount']} {offer['currency']}")
    print(f"Description: {offer['description']}")
    print(f"Invoice: {offer['payment_request']}")
    input("Press Enter once paid...")

@tool
async def convert_to_pdf(markdown: str) -> str:
    """Convert markdown to PDF"""
    client = AsyncMarkdownPDF(on_payment_request=pay)
    return await client.convert(markdown=markdown, title="LangChain PDF")

async def main():
    # Simple chatbot with PDF tool
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that can convert markdown to PDF. When asked to create a PDF, use the convert_to_pdf tool."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, [convert_to_pdf], prompt)
    agent_executor = AgentExecutor(agent=agent, tools=[convert_to_pdf])
    
    # Chat loop
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit']:
            break
            
        result = await agent_executor.ainvoke({"input": user_input}) 
        print("Assistant:", result["output"])

asyncio.run(main())