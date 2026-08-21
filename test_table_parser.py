import asyncio

from app.documents.pdf import PDFParser


async def main():
    document = await PDFParser().parse("test_table.pdf")

    print("filename:", document.filename)
    print("pages:", len(document.pages))
    print("text:")
    print(document.full_text)

    print("\ntables:")
    for page in document.pages:
        print(f"Page {page.page_number}:")
        print(page.metadata.get("tables", []))


asyncio.run(main())
